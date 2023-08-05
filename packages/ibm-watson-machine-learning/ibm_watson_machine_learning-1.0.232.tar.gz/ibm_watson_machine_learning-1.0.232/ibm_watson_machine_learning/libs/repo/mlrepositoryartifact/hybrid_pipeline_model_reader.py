#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import shutil
import logging

from ibm_watson_machine_learning.libs.repo.mlrepository.artifact_reader import ArtifactReader
from ibm_watson_machine_learning.libs.repo.util.compression_util import CompressionUtil
from ibm_watson_machine_learning.libs.repo.util.unique_id_gen import uid_generate
from ibm_watson_machine_learning.libs.repo.base_constants import *


logger = logging.getLogger('HybridPipelineReader')


class HybridPipelineReader(ArtifactReader):
    def __init__(self, scikit_pipeline):
        self.archive_path = None
        self.hybrid_pipeline = scikit_pipeline
        self.type_name = 'model'

    def read(self):
        return self._open_stream()

    def close(self):
        os.remove(self.archive_path)
        self.archive_path = None

    def _save_pipeline_archive(self):
        id_length = 20
        gen_id = uid_generate(id_length)
        temp_dir_name = '{}'.format(self.type_name + gen_id)
        temp_dir = os.path.join('.', temp_dir_name)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        self.ml_pipeline.write().overwrite().save(temp_dir)
        archive_path = self._compress_artifact(temp_dir)
        shutil.rmtree(temp_dir)
        return archive_path

    def _compress_artifact(self, compress_artifact):
        tar_filename = '{}_content.tar'.format(self.type_name)
        gz_filename = '{}.gz'.format(tar_filename)
        CompressionUtil.create_tar(compress_artifact, '.', tar_filename)
        CompressionUtil.compress_file_gzip(tar_filename, gz_filename)
        os.remove(tar_filename)
        return gz_filename

    def _open_stream(self):
        if self.archive_path is None:
            self.archive_path = self._save_pipeline_archive()
        return open(self.archive_path, 'rb')
