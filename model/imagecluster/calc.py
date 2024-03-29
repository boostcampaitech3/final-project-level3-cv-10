import os
from collections import OrderedDict

import numpy as np
from scipy.spatial import distance
from scipy.cluster import hierarchy
from sklearn.decomposition import PCA

import torchvision.transforms as transforms
import torchvision.models as models
import torch

from PIL import Image

data_transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def get_model():
    """Keras Model of the VGG16 network, with the output layer set to `layer`.

    The default layer is the second-to-last fully connected layer 'fc2' of
    shape (4096,).

    Parameters
    ----------
    layer : str
        which layer to extract (must be of shape (None, X)), e.g. 'fc2', 'fc1'
        or 'flatten'

    Notes
    -----
    ::

        base_model.summary()
            ....
            block5_conv4 (Conv2D)        (None, 15, 15, 512)       2359808
            _________________________________________________________________
            block5_pool (MaxPooling2D)   (None, 7, 7, 512)         0
            _________________________________________________________________
            flatten (Flatten)            (None, 25088)             0
            _________________________________________________________________
            fc1 (Dense)                  (None, 4096)              102764544
            _________________________________________________________________
            fc2 (Dense)                  (None, 4096)              16781312
            _________________________________________________________________
            predictions (Dense)          (None, 1000)              4097000
    """

    base_model = models.resnet18(pretrained=True)
    model = torch.nn.Sequential(
        *(list(base_model.children())[:6]), # (28, 28, 128)
        torch.nn.AdaptiveAvgPool2d((1,1)),
        torch.nn.Flatten()
    )


    return model


def fingerprint(pil_images, model, device):

    # pil_images = [Image.fromarray((image).astype(np.uint8)) for image in images]

    arr4ds_tt = [torch.FloatTensor(data_transform(pil_image)) for pil_image in pil_images]

    arr4d_tt = torch.stack(arr4ds_tt)

    model = model.to(device)
    model.eval()
    arr4d_tt = arr4d_tt.to(device)

    ret = model.forward(arr4d_tt).cpu().detach().numpy()

    # print(ret.shape)

    return ret

def pca(fingerprints, n_components=0.9, **kwds):
    """PCA of fingerprints for dimensionality reduction.

    Parameters
    ----------
    fingerprints : see :func:`fingerprints`
    n_components, kwds : passed to :class:`sklearn.decomposition.PCA`

    Returns
    -------
    dict
        same format as in :func:`fingerprints`, compressed fingerprints, so
        hopefully lower dim 1d arrays
    """
    if 'n_components' not in kwds.keys():
        kwds['n_components'] = n_components
    # Yes in recent Pythons, dicts are ordered in CPython, but still.
    _fingerprints = OrderedDict(fingerprints)
    X = np.array(list(_fingerprints.values()))
    Xp = PCA(**kwds).fit(X).transform(X)
    return {k:v for k,v in zip(_fingerprints.keys(), Xp)}


def cluster(fingerprints, sim=0.5, timestamps=None, alpha=0.3, method='average',
            metric='euclidean', extra_out=False, print_stats=False, min_csize=2):
    """Hierarchical clustering of images based on image fingerprints,
    optionally scaled by time distance (`alpha`).

    Parameters
    ----------
    fingerprints: dict
        output of :func:`fingerprints`
    sim : float 0..1
        similarity index
    timestamps: dict
        output of :func:`~imagecluster.io.read_timestamps`
    alpha : float
        mixing parameter of image content distance and time distance, ignored
        if timestamps is None
    method : see :func:`scipy.cluster.hierarchy.linkage`, all except 'centroid' produce
        pretty much the same result
    metric : see :func:`scipy.cluster.hierarchy.linkage`, make sure to use
        'euclidean' in case of method='centroid', 'median' or 'ward'
    extra_out : bool
        additionally return internal variables for debugging
    print_stats : bool
    min_csize : int
        return clusters with at least that many elements

    Returns
    -------
    clusters [, extra]
    clusters : dict
        We call a list of file names a "cluster".

        | keys = size of clusters (number of elements (images) `csize`)
        | value = list of clusters with that size

        ::

            {csize : [[filename, filename, ...],
                      [filename, filename, ...],
                      ...
                      ],
            csize : [...]}
    extra : dict
        if `extra_out` is True
    """
    assert 0 <= sim <= 1, "sim not 0..1"
    assert 0 <= alpha <= 1, "alpha not 0..1"
    assert min_csize >= 1, "min_csize must be >= 1"
    files = list(fingerprints.keys())
    # array(list(...)): 2d array
    #   [[... fingerprint of image1 (4096,) ...],
    #    [... fingerprint of image2 (4096,) ...],
    #    ...
    #    ]
    dfps = distance.pdist(np.array(list(fingerprints.values())), metric)
    if timestamps is not None:
        # Sanity error check as long as we don't have a single data struct to
        # keep fingerprints and timestamps, as well as image data. This is not
        # pretty, but at least a safety hook.
        set_files = set(files)
        set_tsfiles = set(timestamps.keys())
        set_diff = set_files.symmetric_difference(set_tsfiles)
        assert len(set_diff) == 0, (f"files in fingerprints and timestamps do "
                                    f"not match: diff={set_diff}")
        # use 'files' to make sure we have the same order as in 'fingerprints'
        tsarr = np.array([timestamps[k] for k in files])[:,None]
        dts = distance.pdist(tsarr, metric)
        dts = dts / dts.max()
        dfps = dfps / dfps.max()
        dfps = dfps * (1 - alpha) + dts * alpha
    # hierarchical/agglomerative clustering (Z = linkage matrix, construct
    # dendrogram), plot: scipy.cluster.hierarchy.dendrogram(Z)
    Z = hierarchy.linkage(dfps, method=method, metric=metric)
    # cut dendrogram, extract clusters
    # cut=[12,  3, 29, 14, 28, 27,...]: image i belongs to cluster cut[i]
    cut = hierarchy.fcluster(Z, t=dfps.max()*(1.0-sim), criterion='distance')
    cluster_dct = dict((iclus, []) for iclus in np.unique(cut))

    for iimg,iclus in enumerate(cut):
        cluster_dct[iclus].append(files[iimg])
    # group all clusters (cluster = list_of_files) of equal size together
    # {number_of_files1: [[list_of_files], [list_of_files],...],
    #  number_of_files2: [[list_of_files],...],
    # }
    clusters = {}
    for cluster in cluster_dct.values():
        csize = len(cluster)
        if csize >= min_csize:
            if not (csize in clusters.keys()):
                clusters[csize] = [cluster]
            else:
                clusters[csize].append(cluster)

    # if print_stats:
    #     print_cluster_stats(clusters)
    if extra_out:
        extra = {'Z': Z, 'dfps': dfps, 'cluster_dct': cluster_dct, 'cut': cut}
        return clusters, extra
    else:
        return clusters


def cluster_stats(clusters):
    """Count clusters of different sizes.

    Returns
    -------
    2d array
        Array with column 1 = csize sorted (number of images in the cluster)
        and column 2 = cnum (number of clusters with that size).

        ::

            [[csize, cnum],
             [...],
            ]
    """
    return np.array([[k, len(clusters[k])] for k in
                     np.sort(list(clusters.keys()))], dtype=int)


def print_cluster_stats(clusters):
    """Print cluster stats.

    Parameters
    ----------
    clusters : see :func:`cluster`
    """
    print("#images : #clusters")
    stats = cluster_stats(clusters)
    for csize,cnum in stats:
        print(f"{csize} : {cnum}")
    if stats.shape[0] > 0:
        nimg = stats.prod(axis=1).sum()
    else:
        nimg = 0
    print("#images in clusters total: ", nimg)
