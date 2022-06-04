import os
import os.path as osp
import numpy as np
from collections import defaultdict

def intra_cluster_dispersion(cluster_dir, result_dir, fingerprints):
    '''
    Calculate Intra-Cluster Dispersion (S_i)
    '''
    centroid = np.zeros(256)
    encodings = np.empty((0, 256))
    num_points = 0

    for img_fname in os.listdir(cluster_dir):
        if not img_fname.endswith('png') and not img_fname.endswith('jpg'):
            continue

        cluster_img_path = osp.join(cluster_dir, img_fname)
        result_img_path = osp.join(result_dir, cluster_img_path.split('/')[-1])

        fingerprint = fingerprints[result_img_path]
        encodings = np.vstack((encodings, fingerprint))
        centroid += fingerprint
        num_points += 1

    centroid /= float(num_points)
    x = encodings - centroid
    S = np.sqrt((1.0 / num_points) * np.sum((encodings - centroid) ** 2))
    return S, centroid


def separation_measure(centroid1, centroid2):
    return np.sqrt(np.sum((centroid1 - centroid2) ** 2))

def davies_bouldin_index(
    fingerprints,
    merged_cluster_dir = '/opt/ml/input/final-project-level3-cv-10/result/imagecluster/merged_clusters',
    result_dir = '/opt/ml/input/final-project-level3-cv-10/result',
):
    S = []
    centroids = []
    num_clusters = 0
    for sup_dir in os.listdir(merged_cluster_dir):
        for cluster_dir in os.listdir(osp.join(merged_cluster_dir, sup_dir)):
            cluster_dir = osp.join(merged_cluster_dir, sup_dir, cluster_dir)
            print(cluster_dir)
            S_i, centroid = intra_cluster_dispersion(cluster_dir, result_dir, fingerprints)
            S.append(S_i)
            centroids.append(centroid)
            num_clusters += 1


