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

import argparse
import hashlib
import json
import re

line_splitter_flake8 = re.compile(
    '(.*):([0-9]+):([0-9]+):\s([A-Z][0-9]+)\s(.*)')
eslint_severity_splitter = re.compile('([a-zA-Z]*)\/?(.*)?')

parser = argparse.ArgumentParser()
parser.add_argument('filename_backend')
args = parser.parse_args()

exit_with_failure = False

with open(args.filename_backend) as flake_report, \
        open('code-quality-report.json', 'w') as quality_file:
    issues = []
    for line in flake_report:
        line_match = line_splitter_flake8.match(line)
        if line_match:
            tokens = line_match.groups()

            issue_code = tokens[3]
            issue_text = tokens[4]
            issue_hash = hashlib.md5(line.encode('utf-8')).hexdigest()

            if issue_code[0] in ['C']:
                issue_type = "critical"
            elif issue_code[0] in ['E', 'F']:
                issue_type = "major"
            elif issue_code[0] in ['W', 'N']:
                issue_type = "minor"
            else:
                issue_type = "critical"

            exit_with_failure = True
            i = {}
            i["description"] = "[{}] {}".format(issue_code, issue_text)
            i["fingerprint"] = issue_hash
            i["severity"] = issue_type
            i["location"] = {}
            i["location"]["path"] = tokens[0]
            i["location"]["lines"] = {"begin": int(tokens[1])}
            issues.append(i)

    # dump all the issues
    json.dump(issues, quality_file, indent=2)

if exit_with_failure is True:
    exit(0)
