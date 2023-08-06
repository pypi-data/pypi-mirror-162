"""
   Copyright 2015 University of Auckland

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from opencmiss.argon import __version__

_split_version = __version__.split('.')

VERSION_MAJOR = _split_version[0]
VERSION_MINOR = _split_version[1]
VERSION_PATCH = _split_version[2]
VERSION_STRING = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
VERSION_LIST = [VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH]

FLOAT_STRING_FORMAT = '{:.5g}'
