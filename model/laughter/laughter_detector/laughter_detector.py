import librosa, sys, torch, os, numpy as np
from functools import partial
from .import wav_converter, laugh_segmenter
from utils import audio_utils, data_loaders, torch_utils
import warnings
warnings.filterwarnings(action='ignore')

class LaughterDetector:
    def __init__(self,video_path,wav_path,model_cfg):
        self.video_path = video_path
        self.wav_path = wav_path
        self.model_cfg = model_cfg
        self.sample_rate = 8000
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        
    def mp4_to_wav(self):
        wav_converter.convert(self.video_path,self.wav_path)
        
        
    def get_output(self):
        audio_path = self.wav_path + '.wav'
        model_path = self.model_cfg['model_path']
        model = self.model_cfg['model'](dropout_rate=0.0, linear_layer_size=self.model_cfg['linear_layer_size'], filter_sizes=self.model_cfg['filter_sizes'])
        feature_fn = self.model_cfg['feature_fn']
        model.set_device(self.device)

        if os.path.exists(model_path):
            torch_utils.load_checkpoint(model_path+'/best.pth.tar', model)
            model.eval()
        else:
            raise Exception(f"Model checkpoint not found at {model_path}")
        
        inference_dataset = data_loaders.SwitchBoardLaughterInferenceDataset(
            audio_path=audio_path, feature_fn=feature_fn, sr=self.sample_rate)

        collate_fn=partial(audio_utils.pad_sequences_with_labels,
                                expand_channel_dim=self.model_cfg['expand_channel_dim'])

        inference_generator = torch.utils.data.DataLoader(
            inference_dataset, num_workers=4, batch_size=8, shuffle=False, collate_fn=collate_fn)

        probs = []
        for model_inputs, _ in inference_generator:
            x = torch.from_numpy(model_inputs).float().to(self.device)
            preds = model(x).cpu().detach().numpy().squeeze()
            if len(preds.shape)==0:
                preds = [float(preds)]
            else:
                preds = list(preds)
            probs += preds
        probs = np.array(probs)

        file_length = audio_utils.get_audio_length(audio_path)
        fps_wav = len(probs)/float(file_length)

        probs = laugh_segmenter.lowpass(probs)
        laughter_output = laugh_segmenter.get_laughter_instances(probs, threshold=self.model_cfg['threshold'], min_length=float(self.model_cfg['min_length']), fps=fps_wav)
        
        return laughter_output, file_length
    

    def make_laugh_timeline(self,input_timeline,whole_length):
        audio_path = self.wav_path + '.wav'
        audio, sr = librosa.load(audio_path,self.sample_rate)
        
        output_timeline = []
        start,end = -50,-50
        laugh_length = 0
        mean_amp = 0
        mean_amp_count = 0
        for s,e in input_timeline:
            if end<s-12:
                if end-start>20:
                    mean_amp /= mean_amp_count
                    laugh_length /= (end-start+10.5)
                    output_timeline.append((round(start-10,2),round(end+0.5,2),round(laugh_length,2),round(mean_amp,4)))
                    laugh_length = 0
                    mean_amp = 0
                    mean_amp_count = 0
                start,end = s,e
                laugh_length = (e-s)
                mean_amp = audio_utils.get_mean_amplitude(audio,sr,s,e)
                mean_amp_count = 1
            else:
                laugh_length += (e-s)
                mean_amp += audio_utils.get_mean_amplitude(audio,sr,s,e)
                mean_amp_count += 1
                end = e
        output_timeline.append((round(start-10,2),round(end+0.5,2),round(laugh_length/(end-start+10.5),2),round(mean_amp/mean_amp_count,4)))
        if output_timeline[0][0]<0:
            output_timeline[0]=(0,output_timeline[0][1],output_timeline[0][2],output_timeline[0][3]) # 시작값 0보다 작은경우
        if output_timeline[-1][1]>whole_length:
            output_timeline[-1]=(output_timeline[-1][0],whole_length-1,output_timeline[-1][2],output_timeline[-1][3]) # 마지막값이 동영상 전체 길이 벗어나는경우
        return output_timeline
    
    
    def calculate_interest(self,input_timeline):
        if len(input_timeline) == 0:
            return None
        elif len(input_timeline) == 1:
            return [(input_timeline[0][0],input_timeline[0][1],1)]
        else:
            output_timeline = []
            feat_1_min, feat_1_max = 1e3, 0
            feat_2_min, feat_2_max = 1e3, 0
            for start, end, f1, f2 in input_timeline:
                if f1 < feat_1_min:
                    feat_1_min = f1
                if f1 > feat_1_max:
                    feat_1_max = f1
                if f2 < feat_2_min:
                    feat_2_min = f2
                if f2 > feat_2_max:
                    feat_2_max = f2
            for start, end, f1, f2 in input_timeline:
                infos = (start, end, round(0.66*(f1-feat_1_min)/(feat_1_max-feat_1_min+1e-6) + 0.33*(f2-feat_2_min)/(feat_2_max-feat_2_min+1e-6),2))
                output_timeline.append(infos)
            return output_timeline