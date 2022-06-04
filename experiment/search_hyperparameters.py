from face_extractor.face_extractor import FaceExtractor
from clustering_metric import davies_bouldin_index
import pandas as pd
import argparse
import os
import os.path as osp

def main(video_path, data_dir, result_dir, log_path, args):
    if osp.isfile(log_path):
        df = pd.read_csv(log_path)
    else:
        col_names = ['face_cloth_weights', 'sim_threshold', 'face_cnt', 'min_csize', 'use_merging', 'number of persons', 'DBI']
        df = pd.DataFrame(columns=col_names)

    next_idx = len(df)

    extractor = FaceExtractor(
        video_path, data_dir, result_dir,
        threshold=args.sim_thresh,
        face_cnt=args.face_cnt,
        face_cloth_weights=args.weights,
        min_csize=args.min_csize,
        use_merging=args.use_merging
    )

    final_clusters = extractor.cluster_video()
    extractor.summarize_results()
    DBI = davies_bouldin_index(extractor.fingerprints)

    df.loc[next_idx] = [
        extractor.config['face_cloth_weights'],
        extractor.config['sim_threshold'],
        extractor.config['face_cnt'],
        extractor.config['min_csize'],
        extractor.config['use_merging'],
        len(extractor.final_dict)
        DBI
    ]

    df.to_csv(log_path, index=False)
    print(df)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs=2, default=[1.0, 1.0])
    parser.add_argument('--sim-thresh', type=float, default=0.63)
    parser.add_argument('--face-cnt', type=int, default=250)
    parser.add_argument('--min-csize', type=int, default=10)
    parser.add_argument('--use-merging', type=bool, default=True)

    args = parser.parse_args()

    video_path = '/opt/ml/input/final-project-level3-cv-10/data/testvideo_3_0.mp4'
    data_dir = '/opt/ml/input/final-project-level3-cv-10/data/'
    result_dir = '/opt/ml/input/final-project-level3-cv-10/result'

    log_path = '/opt/ml/input/final-project-level3-cv-10/log.csv'

    main(video_path, data_dir, result_dir, log_path, args)
