#
# Copyright (c) 2023 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Consts for distilbert inf."""

ACC = {
    "type": "total",
    "pattern": r"'acc': (.*),",
    "unit": "acc",
}

PERF = {
    "type": "total",
    "pattern": r"perf (\d+.\d+) sentences/s",
    "inverse": False,
    "multiply": False,
    "use_batch_size": False,
    "unit": "sent/s",
}

FUNCTIONAL = {
    "pattern": r"perf (\d+.\d+) sentences/s",
}