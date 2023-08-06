# Copyright 2018 The KaiJIN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""PointCloud Datasets
"""
import os
import math
import pickle
import time
import tqdm
import glob

import torch
import numpy as np
import scipy

import tw
import tw.transform as T
from tw.media.ply import read_ply, write_ply


class SensatUrban(torch.utils.data.Dataset):

  """https://github.com/QingyongHu/SensatUrban

    Ref: Towards Semantic Segmentation of Urban-Scale 3D Point Clouds:
        A Dataset, Benchmarks and Challenges
  """

  def __len__(self):
    return self.num_per_epoch

  def __init__(self, original_block_ply_path,
               grid_path,
               phase,
               batchsize,
               step,
               noise_init=3.5,
               num_points=65536,
               num_layers=5,
               knn_num=16,
               sub_sampling_ratio=[4, 4, 4, 4, 2],
               rank=0,
               subset='',
               **kwargs):
    tw.fs.raise_path_not_exist(original_block_ply_path)
    tw.fs.raise_path_not_exist(grid_path)

    # distributed sampler
    self.rank = rank
    self.subset = subset
    self.current_epoch = 0

    # record batchsize and step to prepare
    self.batchsize = batchsize
    self.step = step
    self.phase = phase
    # self.transform = transform
    self.num_per_epoch = self.step * self.batchsize
    self.noise_init = noise_init
    self.num_points = num_points
    self.num_layers = num_layers
    self.sub_sampling_ratio = sub_sampling_ratio
    self.knn_search = tw.nn.KnnSearch(k=knn_num)
    self.knn_search_up = tw.nn.KnnSearch(k=1)

    # label to name mapping
    self.label_to_names = {
        0: 'Ground', 1: 'High Vegetation', 2: 'Buildings', 3: 'Walls',
        4: 'Bridge', 5: 'Parking', 6: 'Rail', 7: 'traffic Roads', 8: 'Street Furniture',
        9: 'Cars', 10: 'Footpath', 11: 'Bikes', 12: 'Water'}
    self.num_classes = len(self.label_to_names)
    self.label_values = np.sort([k for k, v in self.label_to_names.items()])
    self.label_to_idx = {l: i for i, l in enumerate(self.label_values)}
    self.ignored_labels = np.array([])

    # make sure original ply
    all_files = np.sort(glob.glob(os.path.join(original_block_ply_path, '*.ply')))

    # val and test subset
    if self.subset == 'all':
      val_file_name = ['birmingham_block_1', 'birmingham_block_5', 'cambridge_block_10', 'cambridge_block_7']
      test_file_name = ['birmingham_block_2', 'birmingham_block_8', 'cambridge_block_15', 'cambridge_block_22',
                        'cambridge_block_16', 'cambridge_block_27']
    elif self.subset == 'birmingham':
      val_file_name = ['birmingham_block_1', 'birmingham_block_5']
      test_file_name = ['birmingham_block_2', 'birmingham_block_8']
    elif self.subset == 'cambridge':
      val_file_name = ['cambridge_block_10', 'cambridge_block_7']
      test_file_name = ['cambridge_block_15', 'cambridge_block_22', 'cambridge_block_16', 'cambridge_block_27']
    elif self.subset == 'bike':
      val_file_name = ['birmingham_block_1', 'birmingham_block_5', 'cambridge_block_10', 'cambridge_block_7']
      test_file_name = ['birmingham_block_2', 'birmingham_block_8', 'cambridge_block_15', 'cambridge_block_22',
                        'cambridge_block_16', 'cambridge_block_27']
    elif self.subset == 'rail':
      val_file_name = ['birmingham_block_1', 'birmingham_block_5', 'cambridge_block_10', 'cambridge_block_7']
      test_file_name = ['birmingham_block_2', 'birmingham_block_8', 'cambridge_block_15', 'cambridge_block_22',
                        'cambridge_block_16', 'cambridge_block_27']
    else:
      raise NotImplementedError(self.subset)

    # train subset
    if self.subset == 'all':
      train_file_name = [x.split('/')[-1][:-4] for x in all_files]
    elif self.subset == 'birmingham':
      train_file_name = [x.split('/')[-1][:-4] for x in filter(lambda x: 'birmingham' in x, all_files)]
    elif self.subset == 'cambridge':
      train_file_name = [x.split('/')[-1][:-4] for x in filter(lambda x: 'cambridge' in x, all_files)]
    elif self.subset == 'bike':
      train_file_name = ['cambridge_block_12', 'cambridge_block_13', 'cambridge_block_18']
    elif self.subset == 'rail':
      train_file_name = ['birmingham_block_4']
    else:
      raise NotImplementedError(self.subset)

    # train filter val and test collection
    for name in train_file_name:
      if name in val_file_name or name in test_file_name:
        train_file_name.remove(name)

    # select used files
    self.all_files = []
    for file_path in all_files:
      cloud_name = file_path.split('/')[-1][:-4]
      if self.phase == tw.phase.train and cloud_name in train_file_name:
        self.all_files.append(file_path)
      elif self.phase == tw.phase.val and cloud_name in val_file_name:
        self.all_files.append(file_path)
      elif self.phase == tw.phase.test and cloud_name in test_file_name:
        self.all_files.append(file_path)
    assert len(self.all_files) > 0, "at least including a file."

    # initialize
    self.num_per_class = np.zeros(self.num_classes)
    self.val_proj = []
    self.val_labels = []
    self.test_proj = []
    self.test_labels = []
    self.possibility = {}
    self.min_possibility = {}
    self.input_trees = []
    self.input_colors = []
    self.input_labels = []
    self.input_names = []

    # loading sub-sampled clouds
    self.load_sub_sampled_clouds(grid_path)

    # remove ignored labels
    for ignore_label in self.ignored_labels:
      self.num_per_class = np.delete(self.num_per_class, ignore_label)

    # generate possibility
    self.possibility = []
    self.min_possibility = []
    for i, tree in enumerate(self.input_colors):
      if self.phase == tw.phase.train:
        # where we define random sample possibility for each data point of each file.
        self.possibility += [np.random.rand(tree.data.shape[0]) * 0.001]
      else:
        # for validation or test, we uniformly sample.
        self.possibility += [np.zeros(tree.data.shape[0])]
      # find minimum possibility
      self.min_possibility += [float(np.min(self.possibility[-1]))]

    tw.logger.info(f'num samples per class: {self.num_per_class.tolist()}')
    tw.logger.info(f'generate {len(self.input_colors)} group possibility.')

  def load_sub_sampled_clouds(self, sub_grid_path):
    """loading and process sub-sampled clouds.
    """
    # loading original ply to split train/val/test
    for i, file_path in enumerate(self.all_files):
      t0 = time.time()
      cloud_name = file_path.split('/')[-1][:-4]

      # name of the input files
      kd_tree_file = os.path.join(sub_grid_path, '{:s}_KDTree.pkl'.format(cloud_name))
      sub_ply_file = os.path.join(sub_grid_path, '{:s}.ply'.format(cloud_name))

      data = read_ply(sub_ply_file)
      sub_colors = np.vstack((data['red'], data['green'], data['blue'])).T
      sub_labels = data['class']

      # compute num_per_class in training set
      if self.phase == tw.phase.train:
        self.num_per_class += self.get_num_class_from_label(sub_labels, self.num_classes)

      # read pkl with search tree
      with open(kd_tree_file, 'rb') as f:
        search_tree = pickle.load(f)

      self.input_trees += [search_tree]
      self.input_colors += [sub_colors]
      self.input_labels += [sub_labels]
      self.input_names += [cloud_name]

      size = sub_colors.shape[0] * 4 * 7
      tw.logger.info('[{}] {:s} {:.1f} MB loaded in {:.1f}s, search_tree:{}, sub_colors:{}, sub_labels:{}'.format(
          self.phase.name, kd_tree_file.split('/')[-1], size * 1e-6, time.time() - t0,
          search_tree.data.shape, sub_colors.shape, sub_labels.shape))

  def get_num_class_from_label(self, labels, total_class):
    """count number sample of per class.

    Args:
        labels ([np.numpy]): sample labels.
        total_class ([int]): number of classes

    Returns:
        [int]: number sample per class
    """
    num_pts_per_class = np.zeros(total_class, dtype=np.int32)
    # original class distribution
    val_list, counts = np.unique(labels, return_counts=True)
    for idx, val in enumerate(val_list):
      num_pts_per_class[val] += counts[idx]
    return num_pts_per_class

  def get_class_weights(self, num_per_class, name='sqrt'):
    # pre-calculate the number of points in each category
    frequency = num_per_class / float(sum(num_per_class))
    ce_label_weight = np.zeros_like(frequency)

    if name == 'sqrt' or name == 'lovas':
      ce_label_weight[frequency != 0] = 1 / np.sqrt(frequency[frequency != 0])
    elif name == 'wce':
      ce_label_weight = 1 / (frequency + 0.02)
    elif name == 'cb':
      beta = 0.999
      frequency = np.sqrt(frequency)
      ce_label_weight[frequency != 0] = (1 - beta) / (1 - np.power(beta, frequency[frequency != 0]))
    else:
      raise ValueError('Only support sqrt and wce')
    return np.expand_dims(ce_label_weight, axis=0)

  def shuffle_idx(self, x):
    """shuffle list.

    Args:
        x ([list]): a list

    """
    idx = np.arange(len(x))
    np.random.shuffle(idx)
    return x[idx]

  def data_aug(self, xyz, color, labels, idx, num_out):
    """repeat points
    """
    num_in = len(xyz)
    dup = np.random.choice(num_in, num_out - num_in)
    xyz_dup = xyz[dup, ...]
    xyz_aug = np.concatenate([xyz, xyz_dup], 0)
    color_dup = color[dup, ...]
    color_aug = np.concatenate([color, color_dup], 0)
    idx_dup = list(range(num_in)) + list(dup)
    idx_aug = idx[idx_dup]
    label_aug = labels[idx_dup]

    if self.phase == tw.phase.train and np.random.rand() < 0.0:
        xyz_aug[..., 0] = -xyz_aug[..., 0]
    if self.phase == tw.phase.train and np.random.rand() < 0.0:
        xyz_aug[..., 1] = -xyz_aug[..., 1]

    return xyz_aug, color_aug, idx_aug, label_aug

  def sample(self):
    # select a minimum possibility point cloud
    cloud_idx = int(np.argmin(self.min_possibility))

    # choose a minimum possibility point from minimum possibility point cloud
    point_ind = np.argmin(self.possibility[cloud_idx])

    # get points from tree structure [k, 3]
    points = np.array(self.input_trees[cloud_idx].data, copy=False)

    # center point of input region [1, 3]
    center_point = points[point_ind, :].reshape(1, -1)

    if self.phase == tw.phase.train:
      # add noise to the center point
      noise = np.random.normal(scale=self.noise_init / 10, size=center_point.shape)
      pick_point = center_point + noise.astype(center_point.dtype)
    else:
      # 1) fixed point to inference but maybe damage effects.
      # pick_point = center_point
      # 2) vanilla implementation: random sample but need multiple inference.
      # add noise to the center point
      noise = np.random.normal(scale=self.noise_init / 10, size=center_point.shape)
      pick_point = center_point + noise.astype(center_point.dtype)

    # sample nearest points
    if len(points) < self.num_points:
      queried_idx = self.input_trees[cloud_idx].query(pick_point, k=len(points))[1][0]
    else:
      queried_idx = self.input_trees[cloud_idx].query(pick_point, k=self.num_points)[1][0]

    # shuffle nearest points index
    if self.phase == tw.phase.train:
      queried_idx = self.shuffle_idx(queried_idx)
    else:
      # using random point to inference and take average
      queried_idx = self.shuffle_idx(queried_idx)

    # collect points and colors ([num_points, 3], [num_points, 3], [num_points, ])
    queried_pc_xyz = points[queried_idx]
    queried_pc_xyz = queried_pc_xyz - pick_point  # normalize spatial position in terms of pick point
    queried_pc_colors = self.input_colors[cloud_idx][queried_idx]
    queried_pc_labels = self.input_labels[cloud_idx][queried_idx]

    # compute normalized distance between sampled points and center points
    dists = np.sum(np.square((points[queried_idx] - pick_point).astype(np.float32)), axis=1)
    # close to center, gain higher possibility
    delta = np.square(1 - dists / np.max(dists))  # to [0, 1]
    # add delta to vanilla
    self.possibility[cloud_idx][queried_idx] += delta
    self.min_possibility[cloud_idx] = float(np.min(self.possibility[cloud_idx]))

    if len(points) < self.num_points:
      queried_pc_xyz, queried_pc_colors, queried_idx, queried_pc_labels = self.data_aug(
          queried_pc_xyz, queried_pc_colors, queried_pc_labels, queried_idx, self.num_points)

    return (queried_pc_xyz[None].astype(np.float32),  # [1, 65536, 3]
            queried_pc_colors[None].astype(np.float32),  # [1, 65536, 3]
            queried_pc_labels[None],  # [1, 65536, ]
            queried_idx[None].astype(np.int32),  # [1, 65536, ]
            np.array([cloud_idx], dtype=np.int32))  # [1, ]

  def sample_an_epoch_impl(self):
    targets = []
    for _ in tqdm.tqdm(range(self.num_per_epoch)):
      # (1, 65536, 3) (1, 65536, 3) (1, 65536,) (1, 65536,) (1,)
      pc_xyz, pc_colors, pc_labels, queried_idx, cloud_idx = self.sample()
      targets.append((pc_xyz, pc_colors, pc_labels, queried_idx, cloud_idx))
    return targets

  def sample_an_epoch(self):
    """add using cephFS code, it require at least 1.5T space.
    """
    t1 = time.time()

    # path1: prefer to select a cache file
    if self.num_points == 16384:
      if self.phase == tw.phase.train and self.num_per_epoch == 8000:
        cache_path = f'/cephFS/video_lab/datasets/segment3d/SensatUrban/{self.num_per_epoch}/Epoch-{self.current_epoch}.pth'
      elif self.phase != tw.phase.train and self.num_per_epoch == 5600:
        cache_path = f'/cephFS/video_lab/datasets/segment3d/SensatUrban/{self.num_per_epoch}/{self.phase.name}.pth'
      else:
        cache_path = None
    else:
      cache_path = None

    # sample or load
    if cache_path is None:
      self.targets = self.sample_an_epoch_impl()

    elif not os.path.exists(cache_path):
      self.targets = self.sample_an_epoch_impl()

      # allowing to create a folder
      try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        torch.save(self.targets, cache_path)
        tw.logger.info(f'save targets to cephFS: {cache_path}')
      except BaseException:
        tw.logger.warn(f'failed to save targets to cephFS: {cache_path}')

    else:
      tw.logger.info(f'load targets from cephFS: {cache_path}')
      self.targets = torch.load(cache_path, 'cpu')

    t2 = (time.time() - t1)

    # distribution
    self.sample_weight = np.array(self.get_class_weights(self.num_per_class, name='sqrt')[0])

    # stat
    tw.logger.info(f'generate a batch of {len(self.targets)} samples, {t2}s.')
    self.current_epoch += 1

  def normalize(self, weight):
    return weight / np.sum(weight, axis=0)

  def __getitem__(self, idx):

    # sample a item
    # (1, 65536, 3) (1, 65536, 3) (1, 65536,) (1, 65536,) (1,)
    pc_xyz, pc_colors, pc_labels, queried_idx, cloud_idx = self.targets[idx]

    # zero-norm
    pc_xyz = pc_xyz - np.min(pc_xyz.reshape(-1, 3), axis=0)

    # augmentation for random drop
    if self.phase == tw.phase.train and np.random.rand() < 0.0:
      pc_colors[..., :3] = 0

    # xyz + colors to tensor [bs, num_points, 6]
    input_features = torch.cat([torch.tensor(pc_xyz), torch.tensor(pc_colors)], dim=2)[0].transpose(1, 0)

    # labels to tensor [bs, num_points]
    input_labels = torch.tensor(pc_labels).long()[0]
    input_queried = torch.tensor(queried_idx).long()[0]
    input_idx = torch.tensor(cloud_idx).long()[0]

    # random pooling: form [1, 1, 65536] -> [1, 1, 256]
    input_points, input_neighbors, input_pools, input_up_samples = [], [], [], []

    # random
    sub_labels = pc_labels[0]
    select_random_sample = np.random.rand() > 0.2

    for i in range(self.num_layers):
      # find neighbour_idx of pc_xyz
      _, num_points, _ = pc_xyz.shape
      neighbour_idx = self.knn_search(pc_xyz, pc_xyz)  # pc_xyz [1, 65546, 3], idx[1, 65536, 16]

      if self.phase == tw.phase.train:

        if select_random_sample:
          # 1) random sample
          # there, it is not to sample top-k points
          # note that the sequence order of pc_xyz has been shuffled during training.
          # therefore, top (num_points // self.sub_sampling_ratio[i]) points means that
          #   sample random (num_points // self.sub_sampling_ratio[i]) points from whole space
          #   instead of top-k space.
          sub_points = pc_xyz[:, :num_points // self.sub_sampling_ratio[i], :]  # [1, 16384, 3]
          pool_i = neighbour_idx[:, :num_points // self.sub_sampling_ratio[i], :]  # [1, 16384, 16]

        else:
          # 2) weighted sample
          inds = np.random.choice(np.arange(num_points),
                                  size=num_points // self.sub_sampling_ratio[i],
                                  p=self.normalize(self.sample_weight[sub_labels]))
          sub_labels = sub_labels[inds]
          sub_points = pc_xyz[:, inds, :]
          pool_i = neighbour_idx[:, inds, :]

      else:
        # NOTE: if using `queried_idx = self.shuffle_idx(queried_idx)`, this line will
        # take no effects!!!
        # sample point in terms of fixed stride to subsample whole space.
        sub_points = pc_xyz[:, ::self.sub_sampling_ratio[i], :]  # [1, 16384, 3]
        pool_i = neighbour_idx[:, ::self.sub_sampling_ratio[i], :]  # [1, 16384, 16]

      # find nearest points for each pc_xyz in sub_points
      up_i = self.knn_search_up(sub_points, pc_xyz)  # [1, 16384, 1]

      # add into tensor list
      input_points.append(torch.tensor(pc_xyz.transpose(0, 2, 1))[0].float().unsqueeze(-1))  # [bs, 3, num_points, 1]
      input_neighbors.append(torch.tensor(neighbour_idx)[0].long())  # [bs, num_points, num_neighbor]
      input_pools.append(torch.tensor(pool_i)[0].long())  # [bs, sub_num_points, num_neighbor]
      input_up_samples.append(torch.tensor(up_i)[0].long())  # [bs, num_points, num_neighbor]

      # next, we use sub_points to sample. aka. <random pool>
      pc_xyz = sub_points

    return input_points, input_neighbors, input_pools, input_up_samples, input_features, input_labels, input_queried, input_idx


class STPLS3D(torch.utils.data.Dataset):

  def __init__(self, root, phase=tw.phase.train, repeat=1,
               config={'scale': 3, 'spatial_shape': [128, 512], 'max_npoint': 250000, 'min_npoint': 5000},
               **kwargs):
    # setting basic parametere
    self.phase = phase
    self.config = config

    from tw.nn.ops3d import ops3d
    self.ops3d = ops3d

    # collect data files
    self.targets = sorted(glob.glob(f'{root}/*.pth') * repeat)
    tw.logger.info(f'total loading {self.phase.name} {len(self.targets)} files.')

  def __len__(self):
    return len(self.targets)

  #!<----------------------------------------
  #!< AUGMENTATION
  #!<----------------------------------------

  def elastic(self, x, gran, mag):
    blur0 = np.ones((3, 1, 1)).astype('float32') / 3
    blur1 = np.ones((1, 3, 1)).astype('float32') / 3
    blur2 = np.ones((1, 1, 3)).astype('float32') / 3

    bb = np.abs(x).max(0).astype(np.int32) // gran + 3
    noise = [np.random.randn(bb[0], bb[1], bb[2]).astype('float32') for _ in range(3)]
    noise = [scipy.ndimage.filters.convolve(n, blur0, mode='constant', cval=0) for n in noise]
    noise = [scipy.ndimage.filters.convolve(n, blur1, mode='constant', cval=0) for n in noise]
    noise = [scipy.ndimage.filters.convolve(n, blur2, mode='constant', cval=0) for n in noise]
    noise = [scipy.ndimage.filters.convolve(n, blur0, mode='constant', cval=0) for n in noise]
    noise = [scipy.ndimage.filters.convolve(n, blur1, mode='constant', cval=0) for n in noise]
    noise = [scipy.ndimage.filters.convolve(n, blur2, mode='constant', cval=0) for n in noise]
    ax = [np.linspace(-(b - 1) * gran, (b - 1) * gran, b) for b in bb]
    interp = [scipy.interpolate.RegularGridInterpolator(ax, n, bounds_error=0, fill_value=0) for n in noise]

    def g(x_):
      return np.hstack([i(x_)[:, None] for i in interp])
    return x + g(x) * mag

  def augment(self, xyz, jitter=False, flip=False, rot=False, prob=1.0):
    """jitter, flip or rot the xyz point cloud
    """
    m = np.eye(3)
    if jitter and np.random.rand() < prob:
      m += np.random.randn(3, 3) * 0.1
    if flip and np.random.rand() < prob:
      m[0][0] *= np.random.randint(0, 2) * 2 - 1  # flip x randomly
    if rot and np.random.rand() < prob:
      theta = np.random.rand() * 2 * math.pi
      m = np.matmul(m, [[math.cos(theta), math.sin(theta), 0],
                        [-math.sin(theta), math.cos(theta), 0],
                        [0, 0, 1]])  # rotation
    else:
      # Empirically, slightly rotate the scene can match the results from checkpoint
      theta = 0.35 * math.pi
      m = np.matmul(m, [[math.cos(theta), math.sin(theta), 0],
                        [-math.sin(theta), math.cos(theta), 0],
                        [0, 0, 1]])

    return np.matmul(xyz, m)

  def crop(self, xyz, spatial_shape=[128, 512], max_npoint=250000):
    """crop xyz cloud points to target number
    """
    xyz_offset = xyz.copy()
    valid_idxs = (xyz_offset.min(1) >= 0)
    assert valid_idxs.sum() == xyz.shape[0]

    spatial_shape = np.array([spatial_shape[1]] * 3)
    room_range = xyz.max(0) - xyz.min(0)
    while (valid_idxs.sum() > max_npoint):
      step_temp = step
      if valid_idxs.sum() > 1e6:
        step_temp = step * 2
      offset = np.clip(spatial_shape - room_range + 0.001, None, 0) * np.random.rand(3)
      xyz_offset = xyz + offset
      valid_idxs = (xyz_offset.min(1) >= 0) * ((xyz_offset < spatial_shape).sum(1) == 3)
      spatial_shape[:2] -= step_temp

    return xyz_offset, valid_idxs

  #!<----------------------------------------
  #!< INFO
  #!<----------------------------------------

  def get_valid_ins_label(self, instance_label, valid_idxs):
    """squeeze instance label when select valid idxs
      before [0, N]  ---> valid idxs ---> after [0, N-2(maybe)]
    """
    instance_label = instance_label[valid_idxs]
    j = 0
    while (j < instance_label.max()):
      if (len(np.where(instance_label == j)[0]) == 0):
        instance_label[instance_label == instance_label.max()] = j
      j += 1
    return instance_label

  def get_instance_info(self, xyz, instance_label, semantic_label):
    """record the mean, min, max for each instance and place into each point

    Args:
        xyz (np.ndarray): (n, 3)
        instance_label (int): (n, ) 0~nInst-1, -100)

    Returns:
        instance_num: dict
    """
    pt_mean = np.ones((xyz.shape[0], 3), dtype=np.float32) * -100.0
    instance_pointnum = []
    instance_cls = []
    instance_num = int(instance_label.max()) + 1
    for i_ in range(instance_num):
      inst_idx_i = np.where(instance_label == i_)
      xyz_i = xyz[inst_idx_i]
      pt_mean[inst_idx_i] = xyz_i.mean(0)
      instance_pointnum.append(inst_idx_i[0].size)
      cls_idx = inst_idx_i[0][0]
      instance_cls.append(semantic_label[cls_idx])
    pt_offset_label = pt_mean - xyz

    # ignore instance of class 0 and reorder class id
    instance_cls = [x - 1 if x != -100 else x for x in instance_cls]
    return instance_num, instance_pointnum, instance_cls, pt_offset_label

  #!<----------------------------------------
  #!< TRANSFORM
  #!<----------------------------------------

  def transform_train(self, xyz, rgb, semantic_label, instance_label, aug_prob=1.0):
    """
    """
    scale = self.config['scale']
    min_npoint = self.config['min_npoint']

    xyz_middle = self.augment(xyz, True, True, True, aug_prob)
    xyz = xyz_middle * scale
    if np.random.rand() < aug_prob:
      xyz = self.elastic(xyz, 6, 40.)
      xyz = self.elastic(xyz, 20, 160.)
    # xyz_middle = xyz / self.voxel_cfg.scale
    xyz = xyz - xyz.min(0)

    max_tries = 5
    while (max_tries > 0):
      xyz_offset, valid_idxs = self.crop(xyz)
      if valid_idxs.sum() >= min_npoint:
        xyz = xyz_offset
        break
      max_tries -= 1
    if valid_idxs.sum() < min_npoint:
      return None

    xyz = xyz[valid_idxs]
    xyz_middle = xyz_middle[valid_idxs]
    rgb = rgb[valid_idxs]
    semantic_label = semantic_label[valid_idxs]
    instance_label = self.get_valid_ins_label(instance_label, valid_idxs)
    return xyz, xyz_middle, rgb, semantic_label, instance_label

  def transform_test(self, xyz, rgb, semantic_label, instance_label):
    """
    """
    scale = self.config['scale']
    xyz_middle = self.augment(xyz, False, False, False)
    xyz = xyz_middle * scale
    xyz -= xyz.min(0)
    valid_idxs = np.ones(xyz.shape[0], dtype=bool)
    instance_label = self.get_valid_ins_label(instance_label, valid_idxs)
    return xyz, xyz_middle, rgb, semantic_label, instance_label

  def __getitem__(self, idx):
    """
    """
    path = self.targets[idx]
    scan_id = os.path.basename(path)
    data = torch.load(path)

    # augmentation
    if self.phase == tw.phase.train:
      data = self.transform_train(*data)
    else:
      data = self.transform_test(*data)

    # check data
    if data is None:
      return None
    xyz, xyz_middle, rgb, semantic_label, instance_label = data

    # construct instance label
    info = self.get_instance_info(xyz_middle, instance_label.astype(np.int32), semantic_label)
    inst_num, inst_pointnum, inst_cls, pt_offset_label = info
    coord = torch.from_numpy(xyz).long()
    coord_float = torch.from_numpy(xyz_middle)
    feat = torch.from_numpy(rgb).float()

    if tw.phase.train:
      feat += torch.randn(3) * 0.1

    semantic_label = torch.from_numpy(semantic_label)
    instance_label = torch.from_numpy(instance_label)
    pt_offset_label = torch.from_numpy(pt_offset_label)
    return (path, scan_id, coord, coord_float, feat, semantic_label, instance_label, inst_num, inst_pointnum, inst_cls, pt_offset_label)  # nopep8

  def collate_fn(self, batch):
    """
    """
    spatial_shape = self.config['spatial_shape']
    mode = self.config['mode']

    scan_ids = []
    paths = []
    coords = []
    coords_float = []
    feats = []
    semantic_labels = []
    instance_labels = []

    instance_pointnum = []  # (total_nInst), int
    instance_cls = []  # (total_nInst), long
    pt_offset_labels = []

    total_inst_num = 0
    batch_id = 0
    for data in batch:
      if data is None:
        continue
      (path, scan_id, coord, coord_float, feat, semantic_label, instance_label,
       inst_num, inst_pointnum, inst_cls, pt_offset_label) = data  # parse
      instance_label[np.where(instance_label != -100)] += total_inst_num
      total_inst_num += inst_num
      scan_ids.append(scan_id)
      paths.append(path)
      coords.append(torch.cat([coord.new_full((coord.size(0), 1), batch_id), coord], 1))
      coords_float.append(coord_float)
      feats.append(feat)
      semantic_labels.append(semantic_label)
      instance_labels.append(instance_label)
      instance_pointnum.extend(inst_pointnum)
      instance_cls.extend(inst_cls)
      pt_offset_labels.append(pt_offset_label)
      batch_id += 1

    assert batch_id > 0, 'empty batch'
    if batch_id < len(batch):
      tw.logger.info(f'batch is truncated from size {len(batch)} to {batch_id}')

    # merge all the scenes in the batch
    coords = torch.cat(coords, 0)  # long (N, 1 + 3), the batch item idx is put in coords[:, 0]
    batch_idxs = coords[:, 0].int()
    coords_float = torch.cat(coords_float, 0).to(torch.float32)  # float (N, 3)
    feats = torch.cat(feats, 0)  # float (N, C)
    semantic_labels = torch.cat(semantic_labels, 0).long()  # long (N)
    instance_labels = torch.cat(instance_labels, 0).long()  # long (N)
    instance_pointnum = torch.tensor(instance_pointnum, dtype=torch.int)  # int (total_nInst)
    instance_cls = torch.tensor(instance_cls, dtype=torch.long)  # long (total_nInst)
    pt_offset_labels = torch.cat(pt_offset_labels).float()

    spatial_shape = np.clip(coords.max(0)[0][1:].numpy() + 1, spatial_shape[0], None)  # nopep8
    voxel_coords, v2p_map, p2v_map = self.ops3d.voxelization_idx(coords, batch_id, mode)
    return {
        'paths': paths,
        'scan_ids': scan_ids,
        'coords': coords,
        'batch_idxs': batch_idxs,
        'voxel_coords': voxel_coords,
        'p2v_map': p2v_map,
        'v2p_map': v2p_map,
        'coords_float': coords_float,
        'feats': feats,
        'semantic_labels': semantic_labels,
        'instance_labels': instance_labels,
        'instance_pointnum': instance_pointnum,
        'instance_cls': instance_cls,
        'pt_offset_labels': pt_offset_labels,
        'spatial_shape': spatial_shape,
        'batch_size': batch_id,
    }
