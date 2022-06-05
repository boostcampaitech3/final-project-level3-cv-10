import librosa, numpy as np, pandas as pd, audioread, itertools
from joblib import Parallel, delayed
from tqdm import tqdm
from functools import partial
#from keras.preprocessing.sequence import pad_sequences as keras_pad_seqs
from collections import defaultdict
from . import text_utils
from sklearn.utils import shuffle
import copy, random
import six
import warnings
import scipy.signal
import pyloudnorm as pyln

warnings.filterwarnings(action='ignore')


"""
# Useful functions for loading audio files
"""

def get_mean_amplitude(audio,sr,start,end):
    return np.mean(np.abs(audio[int(sr*start):int(sr*end)]))

# librosa.load() but return only the signal, not (y, sr)
def librosa_load_without_sr(f, sr=None,offset=None,duration=None):
    if offset is not None and duration is not None:
        return librosa.load(f, sr=sr,offset=offset,duration=duration)[0]
    else:
        return librosa.load(f, sr=sr)[0]

# Runs librosa.load() on a list of files in parallel, returns [y1, y2, ...]
def parallel_load_audio_batch(files,n_processes,sr=None,offsets=None,
    durations=None):
    if offsets is not None and durations is not None:
        return Parallel(n_jobs=n_processes)(
            delayed(librosa_load_without_sr)(files[i],sr=sr,offset=offsets[i],
                duration=durations[i]) for i in tqdm(range(len(files))))
    else:
        return Parallel(n_jobs=n_processes)(
            delayed(librosa_load_without_sr)(f,sr=sr) for f in tqdm(files))

def get_audio_length(path):
    with audioread.audio_open(path) as f:
        return f.duration

"""
# Sequence utils
"""

def keras_pad_seqs(sequences, maxlen=None, dtype='int32',
                  padding='pre', truncating='pre', value=0.):
    """Pads sequences to the same length.
    This function transforms a list of
    `num_samples` sequences (lists of integers)
    into a 2D Numpy array of shape `(num_samples, num_timesteps)`.
    `num_timesteps` is either the `maxlen` argument if provided,
    or the length of the longest sequence otherwise.
    Sequences that are shorter than `num_timesteps`
    are padded with `value` at the end.
    Sequences longer than `num_timesteps` are truncated
    so that they fit the desired length.
    The position where padding or truncation happens is determined by
    the arguments `padding` and `truncating`, respectively.
    Pre-padding is the default.
    # Arguments
        sequences: List of lists, where each element is a sequence.
        maxlen: Int, maximum length of all sequences.
        dtype: Type of the output sequences.
            To pad sequences with variable length strings, you can use `object`.
        padding: String, 'pre' or 'post':
            pad either before or after each sequence.
        truncating: String, 'pre' or 'post':
            remove values from sequences larger than
            `maxlen`, either at the beginning or at the end of the sequences.
        value: Float or String, padding value.
    # Returns
        x: Numpy array with shape `(len(sequences), maxlen)`
    # Raises
        ValueError: In case of invalid values for `truncating` or `padding`,
            or in case of invalid shape for a `sequences` entry.
    """
    if not hasattr(sequences, '__len__'):
        raise ValueError('`sequences` must be iterable.')
    num_samples = len(sequences)

    lengths = []
    for x in sequences:
        try:
            lengths.append(len(x))
        except TypeError:
            raise ValueError('`sequences` must be a list of iterables. '
                             'Found non-iterable: ' + str(x))

    if maxlen is None:
        maxlen = np.max(lengths)

    # take the sample shape from the first non empty sequence
    # checking for consistency in the main loop below.
    sample_shape = tuple()
    for s in sequences:
        if len(s) > 0:
            sample_shape = np.asarray(s).shape[1:]
            break

    is_dtype_str = np.issubdtype(dtype, np.str_) or np.issubdtype(dtype, np.unicode_)
    if isinstance(value, six.string_types) and dtype != object and not is_dtype_str:
        raise ValueError("`dtype` {} is not compatible with `value`'s type: {}\n"
                         "You should set `dtype=object` for variable length strings."
                         .format(dtype, type(value)))

    x = np.full((num_samples, maxlen) + sample_shape, value, dtype=dtype)
    for idx, s in enumerate(sequences):
        if not len(s):
            continue  # empty list/array was found
        if truncating == 'pre':
            trunc = s[-maxlen:]
        elif truncating == 'post':
            trunc = s[:maxlen]
        else:
            raise ValueError('Truncating type "%s" '
                             'not understood' % truncating)

        # check `trunc` has expected shape
        trunc = np.asarray(trunc, dtype=dtype)
        if trunc.shape[1:] != sample_shape:
            raise ValueError('Shape of sample %s of sequence at position %s '
                             'is different from expected shape %s' %
                             (trunc.shape[1:], idx, sample_shape))

        if padding == 'post':
            x[idx, :len(trunc)] = trunc
        elif padding == 'pre':
            x[idx, -len(trunc):] = trunc
        else:
            raise ValueError('Padding type "%s" not understood' % padding)
    return x


def pad_sequences(sequences, pad_value=None, max_len=None):
    # If a list of features are supposed to be sequences of the same length
    # But are not, then zero pad the end
    # Expects the sequence length dimension to be the first dim (axis=0)
    # Optionally specify a specific value `max_len` for the sequence length.
    # If none is given, will use the maximum length sequence.
    if max_len is None:
        #lengths = [len(ft) for ft in sequences]
        max_len = max([len(ft) for ft in sequences])
    # Pass along the pad value if provided
    kwargs = {'constant_values': pad_value} if pad_value is not None else {}

    sequences = [librosa.util.fix_length(
        np.array(ft), max_len, axis=0, **kwargs) for ft in sequences]
    return sequences

# This function is for concatenating subfeatures that all have
# the same sequence length
# e.g.  feature_list = [mfcc(40, 12), deltas(40, 12), rms(40, 1)]
# output would be (40, 25)
# The function calls pad_sequences first in case any of the
# sequences of features are off-by-one in length
def concatenate_and_pad_features(feature_list):
    feature_list = pad_sequences(feature_list)
    return np.concatenate(feature_list, axis=1)

"""
# Feature Utils
"""
def featurize_mfcc(f=None, offset=0, duration=None, y=None, sr=None,
        augment_fn=None, hop_length=None, **kwargs):
    """ Accepts either a filepath with optional offset/duration
    or a 1d signal y and sample rate sr. But not both.
    """
    if f is not None and y is not None:
        raise Exception("You should only pass one of `f` and `y`")

    if (y is not None) ^ bool(sr):
        raise Exception("Can't use only one of `y` and `sr`")

    if (offset is not None) ^ (duration is not None):
        raise Exception("Can't use only one of `offset` and `duration`")

    if y is None:
        try:
            y, sr = librosa.load(f, sr=sr, offset=offset, duration=duration)
        except:
            import pdb; pdb.set_trace()
    else:
        if offset is not None and duration is not None:
            start_sample = librosa.core.time_to_samples(offset,sr)
            duration_in_samples = librosa.core.time_to_samples(duration,sr)
            y = y[start_sample:start_sample+duration_in_samples]

    # Get concatenated and padded MFCC/delta/RMS features
    S, phase = librosa.magphase(librosa.stft(y, hop_length=hop_length))
    rms = librosa.feature.spectral.rms(S=S).T
    mfcc_feat = librosa.feature.mfcc(y,sr,n_mfcc=13, n_mels=13,
        hop_length=hop_length, n_fft=int(sr/40)).T#[:,1:]
    deltas = librosa.feature.delta(mfcc_feat.T).T
    delta_deltas = librosa.feature.delta(mfcc_feat.T, order=2).T
    feature_list = [rms, mfcc_feat, deltas, delta_deltas]
    feats = concatenate_and_pad_features(feature_list)
    return feats

def featurize_melspec(f=None, offset=None, duration=None, y=None, sr=None,
        hop_length=None , augment_fn=None, spec_augment_fn=None, **kwargs):
    """ Accepts either a filepath with optional offset/duration
    or a 1d signal y and sample rate sr. But not both.
    """
    if f is not None and y is not None:
        raise Exception("You should only pass one of `f` and `y`")

    if (y is not None) ^ bool(sr):
        raise Exception("Can't use only one of `y` and `sr`")

    if (offset is not None) ^ (duration is not None):
        raise Exception("Can't use only one of `offset` and `duration`")

    if y is None:
        try:
            y, sr = librosa.load(f, sr=sr, offset=offset, duration=duration)
        except:
            import pdb; pdb.set_trace()
    else:
        if offset is not None and duration is not None:
            start_sample = librosa.core.time_to_samples(offset,sr)
            duration_in_samples = librosa.core.time_to_samples(duration,sr)
            y = y[start_sample:start_sample+duration_in_samples]

    if augment_fn is not None:
        y = augment_fn(y)
    S = librosa.feature.melspectrogram(y, sr, hop_length=hop_length).T
    S = librosa.amplitude_to_db(S, ref=np.max)
    if spec_augment_fn is not None:
        S = spec_augment_fn(S)
    return S

#def load_audio_file_segments(f, sr, segments):
#    """ Method to load multiple segments of audio from one file. For example,
#    if there are multiple annotations corresponding to different points in the
#    file.
#    Returns: The clipped audio file
#
#    """

def featurize_audio_segments(segments, feature_fn, f=None, y=None, sr=None):
    """ Method to load features for multiple segments of audio from one file.
    For example, if annotations correspond to different points in the file.
    Accepts either a path to an audio file (`f`), or a preloaded signal (`y`)
    and sample rate (`sr`).

    Args:
    segments: List of times in seconds, of the form (offset, duration)
    feature_fn: A function to compute features for each segment
        feature_fn must accept params (f, offset, duration, y, sr)
    f: Filename of audio file for which to get feature
    y: Preloaded 1D audio signal.
    sr: Sample rate
    Returns: A list of audio features computed by feature_fn, for each
        segment in `segments`.
    """

    if f is not None and y is not None:
            raise Exception("You should only pass one of `f` and `y`")

    if (y is not None) ^ bool(sr):
            raise Exception("Can't use only one of `y` and `sr`")

    feature_list = []
    for segment in segments:
        feature_list.append(feature_fn(f=f, offset=segment[0],
            duration=segment[1], y=y, sr=sr))
    return feature_list


"""
# Collate Functions
# For use in Pytorch DataLoaders
# These functions are applied to the list of items returned by the __get_item__
# method in a Pytorch Dataset object.  We need to follow this pattern in order
# to get the benefit of the multi-processing implemented
# in torch.utils.data.DataLoader
"""
def pad_sequences_with_labels(seq_label_tuples, sequence_pad_value=0,
    label_pad_value=None, input_vocab=None, output_vocab=None,
    max_seq_len=None,  max_label_len=None, one_hot_labels=False,
    one_hot_inputs=False, expand_channel_dim=False, auto_encoder_like=False):

    """ Args:
            seq_label_tuples: a list of length batch_size. If the entries in this
            list are already tuples (i.e. type(seq_label_tuples[0]) is tuple),
            we're dealing with the "Basic" setup, where __get_item__ returns 1
            example per file. In that case, we don't need to do anything extra.
            But if seq_label_tuples[0] is a list, then that means we have a
            list of examples for each file, so we need to combine those lists
            and store the results.

            auto_encoder_like: Flag indicating the the labels are also sequences
            like the inputs, and should be padded the same way.

            Pads at the beginning for input sequences and at the end for
            label sequences.

    """
    # First remove any None entries from the list
    # These may have been caused by too short of a sequence in the dataset or some
    # other data problem.
    seq_label_tuples = [s for s in seq_label_tuples if s is not None]

    if len(seq_label_tuples) == 0:
        return None

    try:
      if type(seq_label_tuples[0]) is list:
          # Each file has multiple examples need to combine into one larger
          # list of batch_size*n_samples tuples, instead of a list of lists of tuples
          combined_seq_label_tuples = []
          for i in range(len(seq_label_tuples)):
              combined_seq_label_tuples += seq_label_tuples[i]
          seq_label_tuples = combined_seq_label_tuples
    except:
      import pdb; pdb.set_trace()


    if (output_vocab is None and one_hot_labels) or (input_vocab is None and one_hot_labels):
        raise Exception("Need to provide vocab to convert labels to one_hot.")

    sequences, labels = unpack_list_of_tuples(seq_label_tuples)

    sequences = keras_pad_seqs(sequences, maxlen=max_seq_len, dtype='float32',
        padding='pre', truncating='post', value=sequence_pad_value)

    # Treat the labels the same as the input seqs if this flag is passed
    if auto_encoder_like:
        labels = keras_pad_seqs(labels, maxlen=max_seq_len, dtype='float32',
        padding='pre', truncating='post', value=sequence_pad_value)

    # If there are no labels, then expect the batch of labels as [None, None...]
    elif labels[0] is not None:
        if label_pad_value is not None:
            # label_pad_value should be the string value, not the integer in the voc
            labels = pad_sequences(labels, label_pad_value, max_len=max_label_len)

        # Convert vocab to integers after padding
        if output_vocab is not None:
            labels = [text_utils.sequence_to_indices(l, output_vocab) for l in labels]

        if one_hot_labels:
            labels = [text_utils.np_onehot(l, depth=len(output_vocab)) for l in labels]

    if expand_channel_dim:
        sequences = np.expand_dims(sequences, 1)
        if auto_encoder_like:
            labels = np.expand_dims(labels, 1)
    return sequences, labels

"""
# Misc Functions
"""
def unpack_list_of_tuples(list_of_tuples):
    return [list(tup) for tup in list(zip(*list_of_tuples))]