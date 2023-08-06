import argparse
import os
import re
import string
import time
import sys
from pathlib import Path
import torch
import pandas as pd

import towhee
from towhee.operator.base import NNOperator, OperatorFlag
from towhee import register
import warnings
warnings.filterwarnings('ignore')
import logging
log = logging.getLogger()

@register(output_schema=["scorelist"],
          flag=OperatorFlag.STATELESS | OperatorFlag.REUSEABLE)

class Deepfake(NNOperator):
    '''
    Deepfake
    '''
    def __init__(self):
        super().__init__()
        sys.path.append(str(Path(__file__).parent))
        weights_dir = os.path.join(str(Path(__file__).parent),"weights/")
        self.model_paths = [os.path.join(weights_dir,model) for model in os.listdir(weights_dir)]
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def __call__(self, filepath: string) -> list:
        from kernel_utils import VideoReader, FaceExtractor, confident_strategy, predict_on_video
        from classifiers import DeepFakeClassifier
        models = []
        for path in self.model_paths:
            model = DeepFakeClassifier(encoder="tf_efficientnet_b7_ns").to(self.device)
            print("loading state dict {}".format(path))
            checkpoint = torch.load(path, map_location="cpu")
            state_dict = checkpoint.get("state_dict", checkpoint)
            model.load_state_dict({re.sub("^module.", "", k): v for k, v in state_dict.items()}, strict=False)
            model.eval()
            del checkpoint
            models.append(model.half())
        frames_per_video = 32
        video_reader = VideoReader()
        video_read_fn = lambda x: video_reader.read_frames(x, num_frames=frames_per_video)
        face_extractor = FaceExtractor(video_read_fn)
        input_size = 384
        strategy = confident_strategy
        #stime = time.time()
        prediction = predict_on_video(False, face_extractor=face_extractor, video_path=filepath, 
                                    input_size=input_size, batch_size=frames_per_video, models=models, 
                                    strategy=strategy, apply_compression=False)
        '''
        test_videos = sorted([x for x in os.listdir(filepath) if x[-4:] == ".mp4"])
        print("Predicting {} videos".format(len(test_videos)))
        predictions = predict_on_video_set(False, face_extractor=face_extractor, input_size=input_size, models=models,
                                        strategy=strategy, frames_per_video=frames_per_video, videos=test_videos,
                                        num_workers=2, test_dir=filepath)
        '''
        return prediction
'''
if __name__ == "__main__":
    filepath = "/Users/zilliz/Desktop/deepfake_video/test/aagfhgtpmv.mp4"
    op = Deepfake()
    pred = op(filepath=filepath)
    print(pred)
'''
