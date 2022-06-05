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
        col_names = ['exp_id', 'video file', 'resolution', 'FPS', 'length(s)', 'sim_threshold', 'face_cnt', 'min_csize', 'face_cloth_weights', 'use_merging', 'number of persons', 'total time(s)', 'DBI']
        df = pd.DataFrame(columns=col_names)

    next_idx = len(df)
    args.use_merging = True if args.use_merging == 'true' else False

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
    dbi_cluster_dir = extractor.merged_cluster_dir if extractor.use_merging else extractor.cluster_dir
    DBI = davies_bouldin_index(extractor.fingerprints, dbi_cluster_dir)

    df.loc[next_idx] = [
        'exp{}'.format(str(next_idx).zfill(4)),
        extractor.video_path.split('/')[-1],
        str(extractor.src_info['frame_h']) + 'x' + str(extractor.src_info['frame_w']),
        extractor.src_info['fps'],
        extractor.src_info['num_seconds'],
        extractor.config['sim_threshold'],
        extractor.config['face_cnt'],
        extractor.config['min_csize'],
        extractor.config['face_cloth_weights'],
        extractor.config['use_merging'],
        len(extractor.final_dict),
        extractor.total_time,
        DBI
    ]

    df.to_csv(log_csv_path, index=False)

    imgs = [(cluster['repr_img_array'], cluster['num_samples']) for cluster in extractor.final_dict.values()]
    
    
    img_width = [img[0].shape[1] for img in imgs]
    img_height = [img[0].shape[0] for img in imgs]
    max_width = max(img_width)
    total_height = sum(img_height)

    combined_img = np.ones((total_height, max_width, 3))

    cum_height = 0
    for img, num_samples in imgs:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.putText(img, "samples: {}".format(num_samples), (0, 30), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255, 255, 100), thickness=2)
        combined_img[cum_height: cum_height + img.shape[0], : img.shape[1]] = img
        cum_height += img.shape[0]

    combined_img = combined_img.astype(np.int32)
    cluster_img_path = osp.join(log_dir, 'exp{}.png'.format(str(next_idx).zfill(4)))
    cv2.imwrite(cluster_img_path, combined_img)

    shutil.rmtree(result_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs=2, type=float, default=[1.0, 1.0])
    parser.add_argument('--sim-thresh', type=float, default=0.63)
    parser.add_argument('--face-cnt', type=int, default=250)
    parser.add_argument('--min-csize', type=int, default=10)
    parser.add_argument('--use-merging', type=str, default='true')

    args = parser.parse_args()

    video_path = '/opt/ml/input/final-project-level3-cv-10/data/testvideo_3_0.mp4'
    data_dir = '/opt/ml/input/final-project-level3-cv-10/data/'
    result_dir = '/opt/ml/input/final-project-level3-cv-10/result'

    log_dir = '/opt/ml/input/final-project-level3-cv-10/experiment/log'
    log_csv_path = '/opt/ml/input/final-project-level3-cv-10/experiment/log/log.csv'

    main(video_path, data_dir, result_dir, log_dir, log_csv_path, args)
