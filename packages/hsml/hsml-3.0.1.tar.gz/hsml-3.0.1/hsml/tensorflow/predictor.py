#
#   Copyright 2022 Logical Clocks AB
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from hsml.constants import PREDICTOR
from hsml.predictor import Predictor


class Predictor(Predictor):
    """Configuration for a predictor running a tensorflow model."""

    def __init__(self, **kwargs):
        if kwargs["model_server"] != PREDICTOR.MODEL_SERVER_TF_SERVING:
            msg_end = (
                "on KServe"
                if kwargs["serving_tool"] == PREDICTOR.SERVING_TOOL_KSERVE
                else "to run the model"
            )
            print(f"Setting up a Tensorflow Serving server {msg_end}")
            kwargs["model_server"] = PREDICTOR.MODEL_SERVER_TF_SERVING
        super().__init__(**kwargs)
