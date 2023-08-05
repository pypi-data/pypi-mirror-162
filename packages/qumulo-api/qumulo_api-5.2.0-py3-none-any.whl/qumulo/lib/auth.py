# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# qumulo_python_versions = { 3.6, latest }

import errno
import json
import os
import shutil

from tempfile import NamedTemporaryFile
from typing import Any, Mapping, Optional

CREDENTIALS_FILENAME = '.qfsd_cred'
CONTENT_TYPE_BINARY = 'application/octet-stream'
CREDENTIALS_VERSION = 1


class Credentials:
    # If you change the credential structure, bump CREDENTIALS_VERSION above!
    def __init__(self, bearer_token: str) -> None:
        self.bearer_token = bearer_token

    @classmethod
    def from_login_response(cls, obj: Mapping[str, object]) -> 'Credentials':
        bearer_token = obj['bearer_token']
        assert isinstance(bearer_token, str), type(bearer_token)
        return cls(bearer_token)

    METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS')
    BINARY_METHODS = ('PATCH', 'PUT', 'POST')
    NO_CONTENT_METHODS = ('GET', 'DELETE', 'HEAD', 'OPTIONS', 'POST')

    def auth_header(self) -> str:
        return f'Bearer {str(self.bearer_token)}'


def credential_store_filename(path_module: Any = None) -> str:
    if path_module is None:
        path_module = os.path

    home = path_module.expanduser('~')
    if home == '~':
        home = os.environ.get('HOME')

    if home is None or home == '~':
        raise OSError('Could not find home directory for credentials store')

    path = os.path.join(home, CREDENTIALS_FILENAME)
    if os.path.isdir(path):
        raise OSError('Credentials store is a directory: %s' % path)
    return path


def remove_credentials_store(path: str) -> None:
    try:
        os.unlink(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def set_credentials(login_response: Mapping[str, object], path: str) -> None:
    on_disk_creds = {}
    on_disk_creds['bearer_token'] = login_response['bearer_token']
    on_disk_creds['version'] = CREDENTIALS_VERSION
    cred_pre = os.path.basename(path) + '.'
    cred_dir = os.path.dirname(path)
    cred_tmp = NamedTemporaryFile(prefix=cred_pre, dir=cred_dir, delete=False)
    try:
        os.chmod(cred_tmp.name, 0o600)
        cred_tmp.write((json.dumps(on_disk_creds) + '\n').encode('utf-8'))
        cred_tmp.flush()
        # Make sure the file is closed before moving it
        cred_tmp.close()
        shutil.move(cred_tmp.name, path)
    finally:
        # On windows, cred_tmp must be closed before it can be unlinked.
        # Close can safely be called multiple times so we call it again just
        # in case there was an error before it was called above.
        cred_tmp.close()
        if os.path.exists(cred_tmp.name):
            os.unlink(cred_tmp.name)


def get_credentials(path: str) -> Optional[Credentials]:
    if not os.path.isfile(path):
        return None
    store = open(path)
    if os.fstat(store.fileno()).st_size == 0:
        return None
    response = json.load(store)
    store.close()

    if response.get('version') != CREDENTIALS_VERSION:
        remove_credentials_store(path)
        return None

    return Credentials.from_login_response(response)
