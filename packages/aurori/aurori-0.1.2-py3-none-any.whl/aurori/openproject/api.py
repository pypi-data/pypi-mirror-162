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

import requests
import math
from concurrent.futures import ThreadPoolExecutor
from requests.auth import HTTPBasicAuth
import json
from aurori.exceptions import NotFoundError


def patch_workpackage(base_url,
                      api_url_prefix,
                      key,
                      workpackage_id,
                      patch_dict,
                      notify=False):
    headers = {'content-type': 'application/json'}
    auth = HTTPBasicAuth('apikey', key)
    get_response = requests.get(base_url + api_url_prefix +
                                '/api/v3/work_packages/' + str(workpackage_id),
                                auth=auth).content
    get_response = json.loads(get_response)

    if get_response[
            'errorIdentifier'] == 'urn:openproject-org:api:v3:errors:NotFound':
        raise NotFoundError(
            f"Patching /api/v3/work_packages/{str(workpackage_id)} failed")

    if notify is True:
        notify_string = '?notify=true'
    else:
        notify_string = '?notify=false'

    patch_dict['lockVersion'] = get_response['lockVersion']
    patch_response = requests.patch(base_url + api_url_prefix +
                                    '/api/v3/work_packages/' +
                                    str(workpackage_id) + notify_string,
                                    data=json.dumps(patch_dict),
                                    headers=headers,
                                    auth=auth).content
    patch_response = json.loads(patch_response)
    pass


def getWorkpackagesOfProject(base_url,
                             api_url_prefix,
                             id,
                             key,
                             filter_string=None,
                             include_closed_packages=False):
    def get_partial_request(request, offset, auth):
        response = requests.get(request + '&offset=' + str(offset),
                                auth=auth).content
        response = json.loads(response)
        print(
            f"Got packages {offset} [{len( response['_embedded']['elements'] )}]"
        )

        return response['_embedded']['elements']

    auth = HTTPBasicAuth('apikey', key)
    if include_closed_packages is True:
        if filter_string is None:
            full_filter_string = '?filters=[ { "status_id": { "operator": "*", "values": null } }]&'
        else:
            full_filter_string = '?filters=[' + filter_string + ' , { "status_id": { "operator": "o", "values": null } }]&'
    else:
        if filter_string is None:
            full_filter_string = '?'
        else:
            full_filter_string = '?filters=[' + filter_string + ']&'

    packages = []
    pagesize = 150
    base_request_string = base_url + api_url_prefix + '/api/v3/projects/' + str(
        id) + '/work_packages' + full_filter_string + 'pageSize=' + str(
            pagesize)

    first_response = requests.get(base_request_string + '&offset=1',
                                  auth=auth).content
    first_response = json.loads(first_response)
    packages.extend(first_response['_embedded']['elements'])

    pages = math.ceil(first_response['total'] / pagesize) + 1
    with ThreadPoolExecutor() as executor:
        partials = []
        for offset in range(2, pages):
            partials.append(
                executor.submit(get_partial_request, base_request_string,
                                offset, auth))
    for p in partials:
        packages.extend(p.result())
    return packages


def get_user_by_mail(base_url, api_url_prefix, key, email):
    auth = HTTPBasicAuth('apikey', key)
    response = requests.get(
        base_url + api_url_prefix + '/api/v3/users' + '?filters=[ ' +
        '{ "name": { "operator": "=", "values": ["' + email + '" ] } } ,' +
        '{ "status": { "operator": "=", "values": [ "active" ] } } ]',
        auth=auth).content
    response = json.loads(response)
    users = {}
    # return only the first
    for u in response['_embedded']['elements']:
        return u


def get_user_list(base_url, api_url_prefix, key):
    auth = HTTPBasicAuth('apikey', key)
    response = requests.get(base_url + api_url_prefix + '/api/v3/users' +
                            '?pageSize=500',
                            auth=auth).content
    response = json.loads(response)
    users = {}
    for u in response['_embedded']['elements']:
        users[int(u['id'])] = u

    return users


def get_workpackages_by_filter(base_url,
                               api_url_prefix,
                               key,
                               filter_string,
                               include_closed_packages=False):
    auth = HTTPBasicAuth('apikey', key)
    if include_closed_packages is True:
        full_filter_string = '?filters=[' + filter_string + ' , { "status_id": { "operator": "*", "values": null } }]'
    else:
        full_filter_string = '?filters=[' + filter_string + ']'

    packages = []
    offset = 1
    while True:
        response = requests.get(base_url + api_url_prefix +
                                '/api/v3/work_packages' + full_filter_string +
                                '&pageSize=500' + '&offset=' + str(offset),
                                auth=auth).content
        response = json.loads(response)

        packages.extend(response['_embedded']['elements'])
        if response['count'] == response['pageSize']:
            offset += 1
        else:
            break
    return packages


def get_responsible_of_workpackage(workpackage):
    if 'responsible' not in workpackage['_links']:
        return None
    else:
        if workpackage['_links']['responsible']['href'] is None:
            return None
        else:
            workpackage['_links']['responsible']['id'] = int(
                workpackage['_links']['responsible']['href'].split('/')[-1])
            return workpackage['_links']['responsible']


def get_assignee_of_workpackage(workpackage):
    if 'assignee' not in workpackage['_links']:
        return None
    else:
        if workpackage['_links']['assignee']['href'] is None:
            return None
        else:
            workpackage['_links']['assignee']['id'] = int(
                workpackage['_links']['assignee']['href'].split('/')[-1])
            return workpackage['_links']['assignee']


def get_parent_of_workpackage(workpackage):
    if 'parent' not in workpackage['_links']:
        return None
    else:
        if workpackage['_links']['parent']['href'] is None:
            return None
        else:
            workpackage['_links']['parent']['id'] = int(
                workpackage['_links']['parent']['href'].split('/')[-1])
            return workpackage['_links']['parent']


def get_children_of_workpackage(workpackage):
    if 'children' not in workpackage['_links']:
        return []
    else:
        return workpackage['_links']['children']


def get_relations_of_workpackage(base_url, api_url_prefix, key, workpackage):
    headers = {'content-type': 'application/json'}
    auth = HTTPBasicAuth('apikey', key)
    relation_relative_url = workpackage['_links']['relations']['href']
    request_url = base_url + relation_relative_url
    data = {}
    response = requests.get(request_url,
                            auth=auth,
                            data=json.dumps(data),
                            headers=headers)
    response = json.loads(response.content)
    if ('_embedded' in response) and ('elements' in response['_embedded']):
        print(f"Got {len(response['_embedded']['elements'])} relations for",
              workpackage['id'])
        return response['_embedded']['elements']
    else:
        print("Got no relations for", workpackage['id'])
        return []


def get_activities_of_workpackage(base_url, api_url_prefix, key, workpackage):
    headers = {'content-type': 'application/json'}
    auth = HTTPBasicAuth('apikey', key)
    relation_relative_url = workpackage['_links']['activities']['href']
    request_url = base_url + relation_relative_url
    data = {}
    response = requests.get(request_url,
                            auth=auth,
                            data=json.dumps(data),
                            headers=headers)
    response = json.loads(response.content)
    if ('_embedded' in response) and ('elements' in response['_embedded']):
        return response['_embedded']['elements']
    else:
        return []
