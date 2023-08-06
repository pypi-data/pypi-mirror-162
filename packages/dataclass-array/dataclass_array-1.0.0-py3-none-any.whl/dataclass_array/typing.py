# Copyright 2022 The dataclass_array Authors.
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

"""Types utils."""

from __future__ import annotations

import typing
from typing import Tuple, Type, TypeVar, Union

from etils.array_types import FloatArray

if typing.TYPE_CHECKING:
  from dataclass_array import array_dataclass

Shape = Tuple[int, ...]
# One or multiple axis. `None` indicate all axes. This is the type of
# .mean(axis=...)
Axes = Union[None, Shape, int]

# pyformat: disable
DTypeArg = Type[Union[
    int,
    float,
    # TODO(epot): Add `np.typing.DTypeLike` once numpy version is updated
    'array_dataclass.DataclassArray',
]]
# pyformat: enable

DcT = TypeVar('DcT', bound='array_dataclass.DataclassArray')

# Typing representing `xnp.ndarray` or `dca.DataclassArray`
DcOrArray = Union[FloatArray[...], 'array_dataclass.DataclassArray']
DcOrArrayT = TypeVar('DcOrArrayT')
