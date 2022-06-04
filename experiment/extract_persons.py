from face_extractor.face_extractor import FaceExtractor
from clustering_metric import davies_bouldin_index
import pandas as pd
import argparse
import os
import os.path as osp
import numpy as np
import cv2
import shutil

def main(video_path, data_dir, result_dir, log_dir, log_csv_path, args):
    if not osp.exists(log_dir):
        os.mkdir(log_dir)

    if osp.isfile(log_csv_path):
        df = pd.read_csv(log_csv_path)
    else:
        col_names = ['exp_id', 'face_cloth_weights', 'sim_threshold', 'face_cnt', 'min_csize', 'use_merging', 'number of persons', 'DBI']
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
    print("fingerprints:", extractor.fingerprints)
    print("DBI:", DBI)

    df.loc[next_idx] = [
        'exp{}'.format(next_idx),
        extractor.config['face_cloth_weights'],
        extractor.config['sim_threshold'],
        extractor.config['face_cnt'],
        extractor.config['min_csize'],
        extractor.config['use_merging'],
        len(extractor.final_dict),
        DBI
    ]
    print(df)

    df.to_csv(log_csv_path, index=False)

    imgs = [cluster['repr_img_array'] for cluster in extractor.final_dict.values()]
    img_width = [img.shape[1] for img in imgs]
    img_height = [img.shape[0] for img in imgs]
    max_width = max(img_width)
    total_height = sum(img_height)

    combined_img = np.ones((total_height, max_width, 3))

    cum_height = 0
    for img in imgs:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        combined_img[cum_height: cum_height + img.shape[0], : img.shape[1]] = img
        cum_height += img.shape[0]

    combined_img = combined_img.astype(np.int32)
    cluster_img_path = osp.join(log_dir, 'exp{}.png'.format(next_idx))
    cv2.imwrite(cluster_img_path, combined_img)

    shutil.rmtree(result_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs=2, type=float, default=[1.0, 1.0])
    parser.add_argument('--sim-thresh', type=float, default=0.63)
    parser.add_argument('--face-cnt', type=int, default=250)
    parser.add_argument('--min-csize', type=int, default=10)
    parser.add_argument('--use-merging', type=bool, default=True)

    args = parser.parse_args()

    video_path = '/opt/ml/input/final-project-level3-cv-10/data/testvideo_3_0.mp4'
    data_dir = '/opt/ml/input/final-project-level3-cv-10/data/'
    result_dir = '/opt/ml/input/final-project-level3-cv-10/result'

    log_dir = '/opt/ml/input/final-project-level3-cv-10/experiment/log'
    log_csv_path = '/opt/ml/input/final-project-level3-cv-10/experiment/log/log.csv'

    main(video_path, data_dir, result_dir, log_dir, log_csv_path, args)
