"""
distance.py

language: python
version: 3.x
author: C. Lockhart <chris@lockhartlab.org>
"""

from molecular.analysis._analysis_utils import _distances

import numpy as np


def contacts(a, b, by='atom', cutoff=4.5):
    """
    Compute atomic contacts.

    Parameters
    ----------
    a, b : Trajectory
    by : float
    cutoff : float

    Returns
    -------

    """

    results = distances(a, b) < cutoff

    if by == 'residue':
        a_map = a.topology['residue_id']
        b_map = b.topology['residue_id']

        a_res = np.unique(a_map)
        b_res = np.unique(b_map)

        a_nres = len(a_res)
        b_nres = len(b_res)

        # TODO can this be generalized into a utility function?
        new_results = np.zeros((results.shape[0], a_nres, b_nres), dtype='bool')
        for i, a_res_i in enumerate(a_res):
            a_atoms = np.ravel(np.argwhere(a_map == a_res_i))
            for j, b_res_j in enumerate(b_res):
                b_atoms = np.ravel(np.argwhere(b_map == b_res_j))
                new_results[:, i, j] = np.max(results[:, a_atoms, :][:, :, b_atoms], axis=(1, 2))

        results = new_results

    return results


# Compute the distance between two Trajectories
def distances(a, b):
    """
    Compute the distance between two Trajectory instances.

    Parameters
    ----------
    a, b : Trajectory
        Two trajectories. Must have same dimensions.

    Returns
    -------
    numpy.ndarray
        Distance between every frame in the trajectory.
    """

    a_xyz = a.xyz.to_numpy().reshape(*a.shape)
    b_xyz = b.xyz.to_numpy().reshape(*b.shape)

    return _distances(a_xyz, b_xyz)


# Compute the distance between two Trajectories
def distance(a, b):
    """
    Compute the distance between two Trajectory instances.

    Parameters
    ----------
    a, b : Trajectory
        Two trajectories. Must have same dimensions.

    Returns
    -------
    numpy.ndarray
        Distance between every frame in the trajectory.
    """

    # TODO there must be a better way
    a_xyz = a.xyz.to_numpy().reshape(*a.shape)
    b_xyz = b.xyz.to_numpy().reshape(*b.shape)

    return np.sqrt(np.sum(np.square(a_xyz - b_xyz), axis=(1, 2)))

# Compute pairwise distance between two Trajectories (or within a Trajectory?)
def pairwise_distance(a, b):
    pass
