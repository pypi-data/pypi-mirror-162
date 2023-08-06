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
# dmprj.engineering.versioncontrol.base


from dmprj.base.messages import MSG_NOT_IMPLEMENTED

__UML_CLASS_RELATION__ = '''
@startuml
class Entity {
  data
  hash
  path
}
class EntityContent {
  checksum
  getContent()
}
class EntitySet {
  hash
  getIterator()
}
class Snapshot {
  timestamp
  caption
  comment
  parents
}

Entity -|> EntityContent
EntitySet -|> Entity
Snapshot -|> EntitySet
@enduml
'''

class Entity(object):
    '''
    the tracking target

    This class represents each individual object that is under version control.
    The objects MUST be uniquely identified.
    '''

    @property
    def path(self):
        '''
        the unique identifying path within the entity domain

        :return: (string)
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def hash(self):
        '''
        :return: (string)
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def data(self):
        '''
        the actual content of the tracking target

        :return: (object)
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)


class EntityContent(object):
    '''
    the data container for individual entity
    '''

    @property
    def checksum(self):
        '''
        :return: (string)
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)

    def getContent(self):
        '''
        :return: (object)
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)


class EntitySet(object):
    '''
    the collection of entities
    '''

    @property
    def hash(self):
        '''
        :return: (string)
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)

    def getIterator(self):
        '''
        :return: (object)
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)


class Snapshot(object):
    '''
    the reference to the view of a specific point-of-time
    '''

    @property
    def timestamp(self):
        '''
        the point of time
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def caption(self):
        '''
        :return: (string)
        '''
        raise NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def comment(self):
        '''
        this value MAY be empty.

        :return: (string)
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)

    @property
    def parents(self):
        '''
        get chronological ancestors.

        this value MAY be empty.

        :return: (objects)
        '''
        return NotImplementedError(MSG_NOT_IMPLEMENTED)
