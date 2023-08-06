# -*- coding: utf-8 -*-
#
#  Copyright 2022 Ramil Nugmanov <nougmanoff@protonmail.com>
#  This file is part of chytorch.
#
#  chytorch is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
from chython import MoleculeContainer
from math import inf
from numpy import empty, nan_to_num, ndarray, ones, sqrt, square, zeros, errstate
from torch import LongTensor, Size, Tensor, int64, ones as t_ones, full, zeros as t_zeros
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset
from torchtyping import TensorType
from typing import Sequence, Tuple, Union


def collate_conformers(batch) -> Tuple[TensorType['batch', 'atoms', int],
                                       TensorType['batch', 'atoms', 'atoms', float],
                                       TensorType['batch', 'atoms', 'atoms', 3, float]]:
    """
    Prepares batches of conformers.

    :return: atoms, distances, directions.
    """
    atoms, distances, diffs = [], [], []

    for a, d, f in batch:
        atoms.append(a)
        distances.append(d)
        diffs.append(f)

    pa = pad_sequence(atoms, True)
    b, s = pa.shape
    # set pad distance to inf
    tmp_a = full((b, s, s), inf)
    tmp_a[:, :, 0] = 0  # prevent nan in MHA softmax on padding
    # diff to pad set to zero
    tmp_b = t_zeros(b, s, s, 3)
    for i, (d, f) in enumerate(zip(distances, diffs)):
        s = d.size(0)
        tmp_a[i, :s, :s] = d
        tmp_b[i, :s, :s, :] = f
    distances = tmp_a
    diffs = tmp_b
    return pa, distances, diffs  # noqa


class ConformerDataset(Dataset):
    def __init__(self, molecules: Sequence[Union[MoleculeContainer, Tuple[ndarray, ndarray]]], *,
                 distance_cutoff: float = 3., infinite_cutoff: bool = True, add_cls: bool = True,
                 symmetric_cls: bool = True, unpack: bool = True):
        """
        convert molecules to tuple of:
            atoms vector with atomic numbers + 2,
            matrix with the Euclidian distances between atoms. for added cls distance set to 1 to each atom
            matrix with xyz normal vectors between atoms.

        Note: atoms shifted to differentiate from padding equal to zero, special cls token equal to 1, and reserved MLM
              task token equal to 2.

        :param molecules: map-like molecules collection or tuples of atomic numbers array and coordinates array.
        :param distance_cutoff: radius of visible neighbors sphere
        :param infinite_cutoff: set distances greater than cutoff to infinite or cutoff
        :param add_cls: add special token at first position
        :param symmetric_cls: do bidirectional attention of cls to atoms and back, or set atom to cls distance to inf
        :param unpack: unpack coordinates from `chython.MoleculeContainer` (True) or use prepared data (False).
            predefined data structure: (vector of atomic numbers, matrix of coordinates).
        """
        self.molecules = molecules
        self.distance_cutoff = distance_cutoff
        self.infinite_cutoff = infinite_cutoff
        self.add_cls = add_cls
        self.symmetric_cls = symmetric_cls
        self.unpack = unpack

    def __getitem__(self, item: int) -> Tuple[TensorType['atoms', int], TensorType['atoms', 'atoms', float],
                                              TensorType['atoms', 'atoms', 3, float]]:
        mol = self.molecules[item]
        if self.unpack:
            if self.add_cls:
                atoms = t_ones(len(mol) + 1, dtype=int64)  # cls token = 1
            else:
                atoms = LongTensor(len(mol))

            for i, (n, a) in enumerate(mol.atoms(), self.add_cls):
                atoms[i] = a.atomic_number + 2

            xyz = empty((len(mol), 3))
            conformer = mol._conformers[0]
            for i, n in enumerate(mol):
                xyz[i] = conformer[n]
        else:
            a, xyz = mol
            if self.add_cls:
                atoms = t_ones(len(a) + 1, dtype=int64)
                atoms[1:] = LongTensor(a + 2)
            else:
                atoms = LongTensor(a + 2)

        diff = xyz[None, :, :] - xyz[:, None, :]  # NxNx3
        dist = sqrt(square(diff).sum(axis=-1))  # NxN
        dist[dist > self.distance_cutoff] = (inf if self.infinite_cutoff else self.distance_cutoff)  # hide far atoms
        with errstate(divide='ignore', invalid='ignore'):  # catch self-loops
            direction = nan_to_num(diff / dist[:, :, None], copy=False)
        if self.add_cls:  # set cls to atoms distance equal to 1
            tmp = ones((len(atoms), len(atoms)))
            tmp[1:, 1:] = dist
            if not self.symmetric_cls:  # disable atom to cls by setting infinity distance
                tmp[1:, 0] = inf
            dist = tmp

            # set direction to/from cls to zero. cls is invisible stationary point.
            tmp = zeros((len(atoms), len(atoms), 3))
            tmp[1:, 1:] = direction
            direction = tmp
        return atoms, Tensor(dist), Tensor(direction)  # noqa

    def __len__(self):
        return len(self.molecules)

    def size(self, dim):
        if dim == 0:
            return len(self.molecules)
        elif dim is None:
            return Size((len(self.molecules),))
        raise IndexError


__all__ = ['ConformerDataset', 'collate_conformers']
