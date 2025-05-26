#!/bin/bash
# Copyright 2021 DeepMind Technologies Limited. All Rights Reserved.
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
#
# WikiGraphs is licensed under the terms of the Creative Commons
# Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) license.
#
# WikiText-103 data (unchanged) is licensed by Salesforce.com, Inc. under the
# terms of the Creative Commons Attribution-ShareAlike 4.0 International
# (CC BY-SA 4.0) license. You can find details about CC BY-SA 4.0 at:
#
#     https://creativecommons.org/licenses/by-sa/4.0/legalcode
#
# Freebase data is licensed by Google LLC under the terms of the Creative
# Commons CC BY 4.0 license. You may obtain a copy of the License at:
#
#     https://creativecommons.org/licenses/by/4.0/legalcode
#
# ==============================================================================
BASE_DIR=/tmp/data

# wikitext-103
TARGET_DIR=${BASE_DIR}/wikitext-103
mkdir -p ${TARGET_DIR}

# Install datasets library if not already installed
uv pip install datasets --quiet

# Download wikitext-103 using Hugging Face datasets
python3 - <<END
import os
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("Salesforce/wikitext", "wikitext-103-v1")

# Save the dataset files to TARGET_DIR
splits = {'train': 'train', 'validation': 'valid', 'test': 'test'}

for split_name, file_name in splits.items():
    with open(os.path.join('${TARGET_DIR}', f"wiki.{file_name}.tokens"), 'w', encoding='utf-8') as f:
        for line in dataset[split_name]['text']:
            f.write(line + '\n')
END

# wikitext-103-raw
TARGET_DIR=${BASE_DIR}/wikitext-103-raw
mkdir -p ${TARGET_DIR}

# Download wikitext-103-raw using Hugging Face datasets
python3 - <<END
import os
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1")

# Save the dataset files to TARGET_DIR
splits = {'train': 'train', 'validation': 'valid', 'test': 'test'}

for split_name, file_name in splits.items():
    with open(os.path.join('${TARGET_DIR}', f"wiki.{file_name}.raw"), 'w', encoding='utf-8') as f:
        for line in dataset[split_name]['text']:
            f.write(line + '\n')
END

# processed freebase graphs
FREEBASE_TARGET_DIR=/tmp/data
mkdir -p ${FREEBASE_TARGET_DIR}/packaged/
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1uuSS2o72dUCJrcLff6NBiLJuTgSU-uRo' -O ${FREEBASE_TARGET_DIR}/packaged/max256.tar
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1nOfUq3RUoPEWNZa2QHXl2q-1gA5F6kYh' -O ${FREEBASE_TARGET_DIR}/packaged/max512.tar
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1uuJwkocJXG1UcQ-RCH3JU96VsDvi7UD2' -O ${FREEBASE_TARGET_DIR}/packaged/max1024.tar

for version in max1024 max512 max256
do
  output_dir=${FREEBASE_TARGET_DIR}/freebase/${version}/
  mkdir -p ${output_dir}
  tar -xvf ${FREEBASE_TARGET_DIR}/packaged/${version}.tar -C ${output_dir}
done
rm -rf ${FREEBASE_TARGET_DIR}/packaged

