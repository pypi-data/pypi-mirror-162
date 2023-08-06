# -*- python -*-
#
# Copyright 2021, 2022 Xingeng Chen
# Copyright 2018, 2019, 2020, 2021 Liang Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# dmprj.engineering.chore.job

from dmprj.base.messages import MSG_NOT_IMPLEMENTED


class JobCommand(object):
    '''
    job commmand specification
    '''

    @property
    def job_name(self):
        '''
        :return: (string)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def job_dir(self):
        '''
        :return: (string)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def job_script(self):
        '''
        :return: (string)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def depend_on_job(self):
        '''
        :return: (string or none)
        '''
        return None

    @property
    def queue_name(self):
        '''
        :return: (string)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def n_thread(self):
        '''
        :return: (integer or none)
        '''
        return None

    @property
    def wall_time(self):
        '''
        :return: (integer or none)
        '''
        return None

    @property
    def checkpoint_dir(self):
        '''
        :return: (string or none)
        '''
        return None

    @property
    def priority(self):
        '''
        :return: (integer or none)
        '''
        return None


class JobDefinition(object):
    '''
    job specification with dependency field

    This class SHOULD be sub-classed for the actual use.

    NOTE: the three command attributes (pre/main/post) SHOULD NOT reference each other within its own logic.
    '''

    SUFFIX_JOB_PREEXEC  = '.pre-job'
    SUFFIX_JOB_POSTEXEC = '.post-job'

    LABEL_LOCAL_FILE  = 'localtmp'
    LABEL_REMOTE_FILE = 'remote'
    LABEL_FILE_MODE   = 'mode'

    def __init__(self, **kwargs):
        self._job_def_kwargs = kwargs

    @property
    def job_dir(self):
        '''
        the working directory on HPC

        :return: '/path/to/job/dir' (string)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def upload_fileset(self):
        '''
        spec: rvalue datatype
        ```python
        [
            {
                'localtmp': 'local_file.dat',
                'remote': '{job_dir}/dir/file.dat',
            },
            {
                'localtmp': 'local_script.sh',
                'remote': '{job_dir}/run.sh',
                'mode': 0755,
            },
            ..
        ]```
        :return: (list)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def preexec_command(self):
        '''
        :return: (obj)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def main_command(self):
        '''
        :return: (obj)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def postexec_command(self):
        '''
        :return: (obj)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def checkpoint_command(self):
        '''
        use for registering checkpoint in job scheduler

        :return: (obj)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)
