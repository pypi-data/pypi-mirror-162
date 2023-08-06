"""
The aurori project

Copyright (C) 2022  Marcus Drobisch,

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__authors__ = ["Marcus Drobisch"]
__contact__ = "aurori@fabba.space"
__credits__ = []
__license__ = "AGPLv3+"

import subprocess

version = "0.1.2"
# WARNING: will be overwritten by CI, see docker/.gitlab-ci.yml
# try:
#    label = subprocess.check_output(["git", "describe"]).strip()
#    version = label.decode(encoding='UTF-8')
# except Exception as e:
#    print("Unable to get version", e)
# WARNING: will be overwritten by CI, see docker/.gitlab-ci.yml
