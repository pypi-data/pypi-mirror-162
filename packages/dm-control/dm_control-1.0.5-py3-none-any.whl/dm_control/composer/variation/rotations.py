# Copyright 2018 The dm_control Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or  implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""Variations in 3D rotations."""


from dm_control.composer.variation import base
from dm_control.composer.variation import variation_values
import numpy as np

IDENTITY_QUATERNION = np.array([1., 0., 0., 0.])


class UniformQuaternion(base.Variation):
  """Uniformly distributed unit quaternions."""

  def __call__(self, initial_value=None, current_value=None, random_state=None):
    random_state = random_state or np.random
    u1, u2, u3 = random_state.uniform([0.] * 3, [1., 2. * np.pi, 2. * np.pi])
    return np.array([np.sqrt(1. - u1) * np.sin(u2),
                     np.sqrt(1. - u1) * np.cos(u2),
                     np.sqrt(u1) * np.sin(u3),
                     np.sqrt(u1) * np.cos(u3)])


class QuaternionFromAxisAngle(base.Variation):
  """Quaternion variation specified in terms of variations in axis and angle."""

  def __init__(self, axis, angle):
    self._axis = axis
    self._angle = angle

  def __call__(self, initial_value=None, current_value=None, random_state=None):
    random_state = random_state or np.random
    axis = variation_values.evaluate(
        self._axis, initial_value, current_value, random_state)
    angle = variation_values.evaluate(
        self._angle, initial_value, current_value, random_state)
    sine, cosine = np.sin(angle / 2), np.cos(angle / 2)
    return np.array([cosine, axis[0] * sine, axis[1] * sine, axis[2] * sine])


class QuaternionPreMultiply(base.Variation):
  """A variation that pre-multiplies an existing quaternion value.

  This variation takes a quaternion value generated by another variation and
  pre-multiplies it to an existing value. In cumulative mode, the new quaternion
  is pre-multiplied to the current value being varied. In non-cumulative mode,
  the new quaternion is pre-multiplied to a fixed initial value.
  """

  def __init__(self, quat, cumulative=False):
    self._quat = quat
    self._cumulative = cumulative

  def __call__(self, initial_value=None, current_value=None, random_state=None):
    random_state = random_state or np.random
    q1 = variation_values.evaluate(self._quat, initial_value, current_value,
                                   random_state)
    q2 = current_value if self._cumulative else initial_value
    return np.array([
        q1[0]*q2[0] - q1[1]*q2[1] - q1[2]*q2[2] - q1[3]*q2[3],
        q1[0]*q2[1] + q1[1]*q2[0] + q1[2]*q2[3] - q1[3]*q2[2],
        q1[0]*q2[2] - q1[1]*q2[3] + q1[2]*q2[0] + q1[3]*q2[1],
        q1[0]*q2[3] + q1[1]*q2[2] - q1[2]*q2[1] + q1[3]*q2[0]])
