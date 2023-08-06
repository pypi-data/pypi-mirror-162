# -*- python -*-
#
# Copyright 2021, 2022 Xingeng Chen
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
# dmprj.concept.structural.entity


class Attribute():
    '''
    base class
    '''


class AttributeWithValue(Attribute):
    '''
    atribute that can store a value
    '''


class MultiValueAttribute(AttributeWithValue):
    '''
    a composition of multiple values under the same name
    '''
