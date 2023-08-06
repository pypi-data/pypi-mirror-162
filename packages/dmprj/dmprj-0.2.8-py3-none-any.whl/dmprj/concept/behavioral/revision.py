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
# dmprj.concept.behavioral.revision


from dmprj.base.messages import MSG_NOT_IMPLEMENTED


class RevisionControl(object):
    '''
    base-class
    '''

    def checkout(self, ref, **kwargs):
        return NotImplementedError(MSG_NOT_IMPLEMENTED)

    def commit(self, data, **kwargs):
        return NotImplementedError(MSG_NOT_IMPLEMENTED)


class LinearRC(RevisionControl):
    '''
    linear history model
    '''


class GraphRC(RevisionControl):
    '''
    graph based history model
    '''
