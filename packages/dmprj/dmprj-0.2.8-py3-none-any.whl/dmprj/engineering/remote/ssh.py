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
# dmprj.engineering.remote.ssh


from dmprj.base.messages import MSG_NOT_IMPLEMENTED


class SSHAction(object):
    """
    remote SSH actions
    """

    def download_single_file(self, src, target, **kwargs):
        '''
        download a single file from remote host via SFTP

        :param src: file path on remote SSH server (string)
        :param target: local directory for storing the transferred file (string)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    def upload_single_file(self, src, target, **kwargs):
        '''
        upload a single file to remote host via SFTP

        :param src: local file path (string)
        :param target: remote file path (string)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    def execute_command(self, command_line, **kwargs):
        '''
        execute a command on remote host

        :param command_line: (string)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

