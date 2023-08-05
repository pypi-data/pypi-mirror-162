# Copyright 2022 The HuggingFace Team. All rights reserved.
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

from .imports import is_tqdm_available


if is_tqdm_available():
    import tqdm.auto as _tqdm

from ..state import AcceleratorState


def tqdm(main_process_only: bool = True, *args, **kwargs):
    """
    Wrapper around `tqdm.tqdm` that optionally displays only on the main process.

    Args:
        main_process_only (`bool`, *optional*):
            Whether to display the progress bar only on the main process
    """
    if not is_tqdm_available():
        raise ImportError("Accelerate's `tqdm` module requires `tqdm` to be installed. Please run `pip install tqdm`.")
    disable = False
    if main_process_only:
        disable = AcceleratorState().local_process_index == 0
    return _tqdm(*args, **kwargs, disable=disable)
