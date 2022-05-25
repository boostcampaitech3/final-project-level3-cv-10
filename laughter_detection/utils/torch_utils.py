import numpy as np, os, sys, shutil, time, math
import torch
from torch import nn
from torch.autograd import Variable
from tensorboardX import SummaryWriter
import text_utils

# Import different progress bar depending on environment
# https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
if 'ipykernel' in sys.modules:
    from tqdm import tqdm_notebook as tqdm
else:
    from tqdm import tqdm


##################### INITIALIZATION ##########################

def count_parameters(model):
    counts = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f'The model has {counts:,} trainable parameters')

def init_weights(model):
    for name, param in model.named_parameters():
        nn.init.normal_(param.data, mean=0, std=0.01)


##################### TENSOR OPERATIONS #######################

def torch_one_hot(y, device, n_dims=None):
    """ Take integer y (tensor or variable) with n dims and convert it to 1-hot representation with n+1 dims. """
    # Source https://discuss.pytorch.org/t/convert-int-into-one-hot-format/507/23
    y_tensor = y.data if isinstance(y, Variable) else y
    y_tensor = y_tensor.type(torch.LongTensor).view(-1, 1)
    n_dims = n_dims if n_dims is not None else int(torch.max(y_tensor)) + 1
    y_one_hot = torch.zeros(y_tensor.size()[0], n_dims).scatter_(1, y_tensor, 1)
    y_one_hot = y_one_hot.view(*y.shape, -1)
    outp = Variable(y_one_hot) if isinstance(y, Variable) else y_one_hot
    return outp.to(device)

def create_embedding_layer(weight_matrix, trainable=True):
    vocab_size, embedding_dim = weight_matrix.shape
    embedding_layer = nn.Embedding(vocab_size, embedding_dim)
    embedding_layer.load_state_dict({'weight': torch.from_numpy(weight_matrix)})
    if not trainable:
        embedding_layer.weight.requires_grad = False
    return embedding_layer

def num_batches_per_epoch(generator):
    return len(generator.dataset)/generator.batch_size

def compute_bow_loss(output, trg, device):
    # output shape: (seq_len, batch_size, output_dim). eg (75, 32, 64)
    # trg shape: (seq_len, batch_size). eg (75, 32)

    output_dim = output.shape[2]
    batch_size = output.shape[1]
    seq_len = output.shape[0]

    total_loss = torch.zeros(1)[0].to(device)

    for i in range(batch_size):
        single_output = output[:,i,:].argmax(1) # predicted bag of words
        bow_output_tensor = torch.zeros(output_dim).to(device)
        for ind in single_output: bow_output_tensor[ind] = 1
        single_target = trg[:,i] # target bag of words
        bow_target_tensor = torch.zeros(output_dim).to(device)
        for ind in single_target: bow_target_tensor[ind] = 1
        single_loss = (bow_target_tensor - bow_output_tensor).abs().sum()
        total_loss += single_loss

    return total_loss / batch_size / seq_len


################## CHECKPOINTING ##############################

def save_checkpoint(state, is_best, checkpoint):
    """Saves model and training parameters at checkpoint + 'last.pth.tar'. If is_best==True, also saves
    checkpoint + 'best.pth.tar'
    Args:
        state: (dict) contains model's state_dict, may contain other keys such as epoch, optimizer state_dict
        is_best: (bool) True if it is the best model seen till now
        checkpoint: (string) folder where parameters are to be saved

    Modified from: https://github.com/cs230-stanford/cs230-code-examples/
    """
    filepath = os.path.join(checkpoint, 'last.pth.tar')
    if not os.path.exists(checkpoint):
        print("Checkpoint Directory does not exist! Making directory {}".format(checkpoint))
        os.mkdir(checkpoint)
    torch.save(state, filepath)
    if is_best:
        shutil.copyfile(filepath, os.path.join(checkpoint, 'best.pth.tar'))


def load_checkpoint(checkpoint, model, optimizer=None):
    """Loads model parameters (state_dict) from file_path. If optimizer is provided, loads state_dict of
    optimizer assuming it is present in checkpoint.
    Args:
        checkpoint: (string) filename which needs to be loaded
        model: (torch.nn.Module) model for which the parameters are loaded
        optimizer: (torch.optim) optional: resume optimizer from checkpoint

    Modified from: https://github.com/cs230-stanford/cs230-code-examples/
    """
    if not os.path.exists(checkpoint):
        raise ("File doesn't exist {}".format(checkpoint))
    else:
        pass
        # print("Loading checkpoint at:", checkpoint)
    checkpoint = torch.load(checkpoint)
    model.load_state_dict(checkpoint['state_dict'])

    if optimizer:
        optimizer.load_state_dict(checkpoint['optim_dict'])

    if 'epoch' in checkpoint:
        model.epoch = checkpoint['epoch']

    if 'global_step' in checkpoint:
        model.global_step = checkpoint['global_step'] + 1
        pass
        # print("Loading checkpoint at step: ", model.global_step)

    if 'best_val_loss' in checkpoint:
        model.best_val_loss = checkpoint['best_val_loss']

    return checkpoint

def make_state_dict(model, optimizer=None, epoch=None, global_step=None,
    best_val_loss=None):
    return {'epoch': epoch, 'global_step': global_step,
        'best_val_loss': best_val_loss, 'state_dict': model.state_dict(),
        'optim_dict' : optimizer.state_dict()
    }




##################### PREDICTING FROM TRAINED MODELS #####################

class Predictor:
    def __init__(self, dataset, filepaths, model=None, reverse_vocab=None, generator=None,
                 label_paths=None, batch_size=None, labels=None, label_fn=None,
                collate_fn=None):

        # Validate args
        if generator is None and collate_fn is None:
            raise Exception("Need either `generator` or `collate_fn`")

        self.reverse_vocab = reverse_vocab
        self.batch_size = batch_size

        # Create a new Dataset of the same type as the given one
        # Copy over all the attributes except for the file paths
        d_vars = vars(dataset)

        self.dataset = type(dataset)(filepaths,
            feature_and_label_fn=d_vars['feature_and_label_fn'],
            feature_fn=d_vars['feature_fn'],
            label_paths=label_paths, labels=labels, label_fn=label_fn,
            does_subsample=d_vars['does_subsample'],
            **d_vars['kwargs'])

        self.model=model

        # Create a new Generator of the same type as the given one
        # And copy over the attributes if provided
        if generator is not None:
            g_vars = vars(generator)
            self.generator=type(generator)(self.dataset,
                num_workers=g_vars['num_workers'],
                batch_size=g_vars['batch_size'],
                collate_fn=g_vars['collate_fn'])
        else:
            self.generator = torch.utils.data.DataLoader(
            self.dataset, num_workers=0, batch_size=self.batch_size or len(filepaths),
            shuffle=False, collate_fn=collate_fn)

    def predict(self):
        to_return = []
        for i_batch, batch in enumerate(self.generator):
            seqs, labs = batch

            if labs is not None:
                # Convert to readable labels with reverse vocab
                labs = [text_utils.readable_outputs(
                    s, self.reverse_vocab) for s in np.array(labs)]

            # Run model forward
            with torch.no_grad():
                src = torch.from_numpy(np.array(seqs)).float().permute((1,0,2)).cpu()#.to(device)
                output = self.model(src).cpu() # No labels given

            # Remove batch dimension, get arxmax from one hot, and convert to numpy
            output_seqs = np.argmax(output.cpu().numpy(), axis=-1).T

            readable_preds = [text_utils.readable_outputs(
                s, self.reverse_vocab) for s in output_seqs]

            to_return.append( (readable_preds, labs) )
        return to_return

class OneFileDatasetPredictor:
    def __init__(self, dataset, index, model=None, reverse_vocab=None,
                 batch_size=None, generator=None,collate_fn=None):

        # Validate args
        if generator is None and collate_fn is None:
            raise Exception("Need either `generator` or `collate_fn`")

        self.reverse_vocab = reverse_vocab
        self.batch_size = batch_size or 1

        # Create a new Dataset of the same type as the given one
        # Copy over all the attributes except for the file paths
        d_vars = vars(dataset)

        self.dataset = type(dataset)(filepath=d_vars['filepath'],
            feature_and_label_fn=d_vars['feature_and_label_fn'],
            start_index = index, end_index = index+self.batch_size,
            load_fn=d_vars['load_fn'],
            **d_vars['kwargs'])

        self.model=model

        # Create a new Generator of the same type as the given one
        # And copy over the attributes if provided
        if generator is not None:
            g_vars = vars(generator)
            self.generator=type(generator)(self.dataset,
                num_workers=g_vars['num_workers'],
                batch_size=g_vars['batch_size'],
                collate_fn=g_vars['collate_fn'])
        else:
            self.generator = torch.utils.data.DataLoader(
            self.dataset, num_workers=0, batch_size=self.batch_size,
            shuffle=False, collate_fn=collate_fn)

    def predict(self):
        to_return = []
        for i_batch, batch in enumerate(self.generator):
            seqs, labs = batch

            if labs is not None:
                # Convert to readable labels with reverse vocab
                labs = [text_utils.readable_outputs(
                    s, self.reverse_vocab) for s in np.array(labs)]

            # Run model forward
            with torch.no_grad():
                src = torch.from_numpy(np.array(seqs)).float().permute((1,0,2))#.to(device)
                output = self.model(src) # No labels given

            # Remove batch dimension, get arxmax from one hot, and convert to numpy
            output_seqs = np.argmax(output.cpu().numpy(), axis=-1).T

            readable_preds = [text_utils.readable_outputs(
                s, self.reverse_vocab) for s in output_seqs]

            to_return.append( (readable_preds, labs) )
        return to_return