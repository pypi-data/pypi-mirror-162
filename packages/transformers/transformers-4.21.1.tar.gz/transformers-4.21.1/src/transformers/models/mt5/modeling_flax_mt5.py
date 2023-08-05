# coding=utf-8
# Copyright 2021 Mesh TensorFlow authors, T5 Authors and HuggingFace Inc. team.
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
""" Flax mT5 model."""

import numpy as np

from ...utils import logging
from ..t5.modeling_flax_t5 import FlaxT5EncoderModel, FlaxT5ForConditionalGeneration, FlaxT5Model
from .configuration_mt5 import MT5Config


logger = logging.get_logger(__name__)

_CONFIG_FOR_DOC = "T5Config"
_TOKENIZER_FOR_DOC = "T5Tokenizer"


# Copied from transformers.models.bart.modeling_flax_bart.shift_tokens_right
def shift_tokens_right(input_ids: np.array, pad_token_id: int, decoder_start_token_id: int) -> np.ndarray:
    """
    Shift input ids one token to the right.
    """
    shifted_input_ids = np.zeros_like(input_ids)
    shifted_input_ids[:, 1:] = input_ids[:, :-1]
    shifted_input_ids[:, 0] = decoder_start_token_id

    shifted_input_ids = np.where(shifted_input_ids == -100, pad_token_id, shifted_input_ids)
    return shifted_input_ids


class FlaxMT5Model(FlaxT5Model):
    r"""
    This class overrides [`FlaxT5Model`]. Please check the superclass for the appropriate documentation alongside usage
    examples.

    Examples:

    ```python
    >>> from transformers import FlaxMT5Model, T5Tokenizer

    >>> model = FlaxMT5Model.from_pretrained("google/mt5-small")
    >>> tokenizer = T5Tokenizer.from_pretrained("google/mt5-small")

    >>> article = "UN Offizier sagt, dass weiter verhandelt werden muss in Syrien."
    >>> summary = "Weiter Verhandlung in Syrien."
    >>> inputs = tokenizer(article, return_tensors="np")

    >>> with tokenizer.as_target_tokenizer():
    ...     decoder_input_ids = tokenizer(summary, return_tensors="np").input_ids

    >>> outputs = model(input_ids=inputs["input_ids"], decoder_input_ids=decoder_input_ids)
    >>> hidden_states = outputs.last_hidden_state
    ```"""
    model_type = "mt5"
    config_class = MT5Config


class FlaxMT5EncoderModel(FlaxT5EncoderModel):
    r"""
    This class overrides [`FlaxT5EncoderModel`]. Please check the superclass for the appropriate documentation
    alongside usage examples.

    Examples:

    ```python
    >>> from transformers import FlaxT5EncoderModel, T5Tokenizer

    >>> model = FlaxT5EncoderModel.from_pretrained("google/mt5-small")
    >>> tokenizer = T5Tokenizer.from_pretrained("google/mt5-small")

    >>> article = "UN Offizier sagt, dass weiter verhandelt werden muss in Syrien."
    >>> summary = "Weiter Verhandlung in Syrien."
    >>> inputs = tokenizer(article, return_tensors="np")

    >>> with tokenizer.as_target_tokenizer():
    ...     decoder_input_ids = tokenizer(summary, return_tensors="np").input_ids

    >>> outputs = model(input_ids=inputs["input_ids"])
    >>> hidden_states = outputs.last_hidden_state
    ```"""
    model_type = "mt5"
    config_class = MT5Config


class FlaxMT5ForConditionalGeneration(FlaxT5ForConditionalGeneration):
    r"""
    This class overrides [`FlaxT5ForConditionalGeneration`]. Please check the superclass for the appropriate
    documentation alongside usage examples.

    Examples:

    ```python
    >>> from transformers import FlaxMT5ForConditionalGeneration, T5Tokenizer

    >>> model = FlaxMT5ForConditionalGeneration.from_pretrained("google/mt5-small")
    >>> tokenizer = T5Tokenizer.from_pretrained("google/mt5-small")

    >>> article = "UN Offizier sagt, dass weiter verhandelt werden muss in Syrien."
    >>> summary = "Weiter Verhandlung in Syrien."
    >>> inputs = tokenizer(article, return_tensors="np")

    >>> with tokenizer.as_target_tokenizer():
    ...     decoder_input_ids = tokenizer(summary, return_tensors="np").input_ids

    >>> outputs = model(**inputs, decoder_input_ids=decoder_input_ids)
    >>> logits = outputs.logits
    ```"""

    model_type = "mt5"
    config_class = MT5Config
