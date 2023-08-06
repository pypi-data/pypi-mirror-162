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
from math import sqrt, pi, inf
from torch import empty, exp, square, isinf, bmm, softmax, cat, zeros_like, nan_to_num, finfo
from torch.nn import Module, GELU, Embedding, Parameter, ModuleList, Sequential, Linear, LayerNorm, Dropout
from torch.nn.init import uniform_, constant_
from torchtyping import TensorType
from typing import Tuple, Union
from .transformer import EncoderLayer


s2pi = sqrt(2 * pi)


class ConformerEncoder(Module):
    def __init__(self, *, shared_layers: bool = True, nkernel: int = 128, posinf: float = 10.,
                 d_model: int = 1024, nhead: int = 16, num_layers: int = 8, dim_feedforward: int = 3072,
                 dropout: float = 0.1, activation=GELU, layer_norm_eps: float = 1e-5):
        """
        Reimplemented Graphormer3D <https://github.com/microsoft/Graphormer>

        :param nkernel: number of Gaussian functions.
        :param shared_layers: ALBERT-like encoder layer sharing.
        """
        super().__init__()
        self.eps = layer_norm_eps
        self.nhead = nhead
        self.atoms_encoder = Embedding(121, d_model, 0)
        self.centrality_encoder = Linear(nkernel, d_model)
        self.gaussian = GaussianLayer(nkernel, posinf, layer_norm_eps)
        self.spatial_encoder = Sequential(Linear(nkernel, nkernel),
                                          LayerNorm(nkernel, eps=layer_norm_eps),
                                          activation(),
                                          Dropout(dropout),
                                          Linear(nkernel, nhead))
        self.force = ForceLayer(d_model, nhead, dropout)

        if shared_layers:
            self.layer = layer = EncoderLayer(d_model, nhead, dim_feedforward, dropout, activation, layer_norm_eps)
            self.layers = [layer] * num_layers
        else:
            self.layers = ModuleList(EncoderLayer(d_model, nhead, dim_feedforward, dropout, activation, layer_norm_eps)
                                     for _ in range(num_layers))

    def forward(self, batch: Tuple[TensorType['batch', 'atoms', int],
                                   TensorType['batch', 'atoms', 'atoms', float],
                                   TensorType['batch', 'atoms', 'atoms', 3, float]], /, *, force: bool = True) -> \
            Union[TensorType['batch', 'atoms', 'embedding'],
                  Tuple[TensorType['batch', 'atoms', 'embedding'], TensorType['batch', 'atoms', 3]]]:
        """
        :param batch: input data
        :param force: return atom forces
        """
        atoms, dist, dirs = batch

        # padding has inf dist > gfs will be zero > no contribution to spatial and centrality encoding
        gf = self.gaussian(atoms, dist)  # BxNxNxK
        # mask padding and long-distance interactions
        # d_mask - is distance lvl attention bw atoms
        d_mask = self.spatial_encoder(gf).masked_fill_(isinf(dist).unsqueeze_(-1), -inf)  # BxNxNxK > BxNxNxH
        d_mask = d_mask.permute(0, 3, 1, 2).flatten(end_dim=1)  # BxNxNxH > BxHxNxN > B*HxNxN

        x = self.atoms_encoder(atoms) + self.centrality_encoder(gf.sum(2))  # BxNxE
        for lr in self.layers:
            x, _ = lr(x, d_mask)
        if force:
            # prepare padding mask from distances
            # BxNxN > BxNxNx1 > BxNxNxH
            d_mask = zeros_like(dist).masked_fill_(isinf(dist), -inf).unsqueeze_(-1).expand(-1, -1, -1, self.nhead)
            d_mask = d_mask.permute(0, 3, 1, 2).flatten(end_dim=1)  # BxNxNxH > BxHxNxN > B*HxNxN
            return x, self.force(x, dirs, d_mask)
        return x


class GaussianLayer(Module):
    """
    x = a * d + b
    g = exp(-.5 * ((x - u) ** 2 / s ** 2)) / (s * sqrt(2 * pi))
    """
    def __init__(self, nkernel: int, posinf: float = 10., eps: float = 1e-5):
        super().__init__()
        self.nkernel = nkernel
        self.posinf = posinf
        self.eps = eps
        self.mu = Parameter(empty(nkernel))
        self.sigma = Parameter(empty(nkernel))
        self.a = Parameter(empty(121, 121))
        self.b = Parameter(empty(121, 121))
        self.reset_parameters()

    def reset_parameters(self):
        uniform_(self.mu, 0, 3)
        uniform_(self.sigma, 1, 3)
        constant_(self.a, 1)
        constant_(self.b, 0)

    def forward(self, atoms, distances):
        a = self.a[atoms.unsqueeze(-1), atoms.unsqueeze(1)]  # [BxNx1, Bx1xN] > BxNxN
        b = self.b[atoms.unsqueeze(-1), atoms.unsqueeze(1)]
        # exp(-inf) > nan
        d = nan_to_num(distances, posinf=self.posinf)
        # BxNxN > BxNxNx1 > BxNxNxK
        x = (a * d + b).unsqueeze(-1).expand(-1, -1, -1, self.nkernel)
        return exp(-.5 * square((x - self.mu) / self.sigma)) / ((self.sigma.abs() + self.eps) * s2pi)


class ForceLayer(Module):
    """
    Attention matrix bw atoms slitted to the 3 axes with scaled contribution.
    """
    def __init__(self, d_model, nhead, dropout: float = 0.1):
        super().__init__()
        self.projection = Linear(d_model, 3 * d_model)
        self.dropout = Dropout(dropout)
        self.force = Linear(d_model, 1)

        self.scale = sqrt(d_model)
        self.dhead = d_model // nhead
        self.nhead = nhead

    def forward(self, emb, dirs, d_mask):
        b, n, _ = emb.size()
        q, k, v = self.projection(emb).chunk(3, dim=-1)

        # BxNxE > BxNxHxD > BxHxNxD > B*HxNxD
        q = q.view(b, n, self.nhead, self.dhead).transpose(1, 2).flatten(end_dim=1) / self.scale
        # BxNxE > BxNxHxD > BxHxDxN > B*HxDxN
        k = k.view(b, n, self.nhead, self.dhead).permute(0, 2, 3, 1).flatten(end_dim=1)
        v = v.view(b, n, self.nhead, self.dhead).transpose(1, 2).unsqueeze(2)  # BxNxE > BxNxHxD > BxHx1xNxD

        # B*HxNxD @ B*HxDxN > B*HxNxN > BxHxNxN
        attn = self.dropout(softmax(bmm(q, k) + d_mask, dim=-1)).view(b, self.nhead, n, n)
        # extract per axis attention
        # BxHxNxNx1 * Bx1xNxNx3 > BxHxNxNx3 > BxHx3xNxN
        attn = (attn.unsqueeze(-1) * dirs.unsqueeze(1)).permute(0, 1, 4, 2, 3)
        # BxHx3xNxN @ BxHx1xNxD > BxHx3xNxD > BxNx3xHxD > BxNx3xH*D(E)
        xyz = (attn @ v).permute(0, 3, 2, 1, 4).flatten(start_dim=3)
        return cat((self.force(xyz[:, :, 0]), self.force(xyz[:, :, 1]), self.force(xyz[:, :, 2])), dim=-1)  # BxNx3


__all__ = ['ConformerEncoder']
