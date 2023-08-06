import datetime
import os
import pathlib
import sqlite3
import subprocess
import sys
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Literal, Optional
from urllib.parse import urljoin as uj

import requests


class FileNotSyncedError(Exception):
    def __init__(self, file):
        self.file = file


class SeafileConfigFileMissing(Exception):
    def __init__(self, file):
        self.file = file


class MatchingLocalLibraryError(Exception):
    def __init__(self, local_library):
        self.local_library = local_library


@dataclass()
class Permissions:
    can_edit: bool = False
    can_download: bool = True
    can_upload: bool = False

    @staticmethod
    def _s(b):
        return str(b).lower()

    def __repr__(self):
        return f'Permissions(can_edit={self.can_edit}, can_download={self.can_download}, can_upload={self.can_upload})'

    def __str__(self):
        return f'{{"can_edit": {self._s(self.can_edit)},' \
               f'  "can_download": {self._s(self.can_download)},' \
               f'  "can_upload": {self._s(self.can_upload)}}}'


@dataclass()
class Details:
    ...


@dataclass()
class ElementDetails(Details):
    name: str = None
    permission: str = None
    mtime: int = None


@dataclass()
class FileDetails(ElementDetails):
    type: str = None
    id: str = None
    last_modified: datetime.datetime = None
    last_modifier_email: str = None
    last_modifier_name: str = None
    last_modifier_contact_email: str = None
    size: int = None
    starred: bool = False
    comment_total: int = None
    can_edit: bool = False

    def __post_init__(self):
        if self.last_modified and isinstance(self.last_modified, str):
            try:
                self.last_modified = datetime.datetime.fromisoformat(self.last_modified)
            except ValueError:
                pass


@dataclass()
class DirectoryDetails(ElementDetails):
    repo_id: str = None
    path: str = None


@dataclass()
class InternalLinkDetails(Details):
    smart_link: str = None
    smart_link_token: str = None
    name: str = None

    def __post_init__(self):
        self.link = self.smart_link
        del self.smart_link
        self.link_token = self.smart_link_token
        del self.smart_link_token


@dataclass()
class UploadLinkDetails(Details):
    username: str = None
    repo_id: str = None
    repo_name: str = None
    path: str = None
    obj_name: str = None
    token: str = None
    link: str = None
    view_cnt: int = 0
    ctime: datetime.datetime = None
    expire_date: datetime.datetime = None
    is_expired: bool = False
    can_edit: bool = False

    def __post_init__(self):
        if self.ctime and isinstance(self.ctime, str):
            try:
                self.ctime = datetime.datetime.fromisoformat(self.ctime)
            except ValueError:
                pass
        if self.expire_date and isinstance(self.expire_date, str):
            try:
                self.expire_date = datetime.datetime.fromisoformat(self.expire_date)
            except ValueError:
                pass


@dataclass()
class ShareLinkDetails(UploadLinkDetails):
    is_dir: bool = False
    permissions: Permissions = None
    repo_folder_permission: str = None

    def __post_init__(self):
        if isinstance(self.permissions, dict):
            self.permissions = Permissions(**self.permissions)
        super(ShareLinkDetails, self).__post_init__()


@dataclass
class RemoteLibrary:
    url: str = ""
    token: str = ""
    encrypted: str = ""
    head_commit_id: str = ""
    id: str = ""
    modifier_contact_email: str = ""
    modifier_email: str = ""
    modifier_name: str = ""
    mtime: str = ""
    mtime_relative: str = ""
    name: str = ""
    owner: str = ""
    owner_contact_email: str = ""
    owner_name: str = ""
    permission: str = ""
    root: str = ""
    salt: str = ""
    size: str = ""
    size_formatted: str = ""
    type: str = ""
    version: str = ""
    virtual: str = ""

    def __hash__(self):
        return hash('RemoteLibrary' + self.id)

    def __repr__(self):
        return f"<RemoteLibrary> id={self.id} name={self.name}"

    @property
    def _auth_header(self) -> dict:
        return {"Authorization": 'token ' + self.token}

    def get_file_details(self, file) -> FileDetails:
        return FileDetails(**requests.get(uj(self.url, f'/api2/repos/{self.id}/file/detail/?'
                                                       f'p={urllib.parse.quote(file)}'),
                                          headers=self._auth_header).json())

    def get_directory_details(self, file) -> DirectoryDetails:
        return DirectoryDetails(**requests.get(uj(self.url, f'/api/v2.1/repos/{self.id}/dir/detail/?'
                                                            f'path={urllib.parse.quote(file)}'),
                                               headers=self._auth_header).json())

    def get_share_links(self, file) -> List[ShareLinkDetails]:
        results = requests.get(uj(self.url, f'api/v2.1/share-links/?'
                                            f'repo_id={self.id}&'
                                            f'path={urllib.parse.quote(file)}'), headers=self._auth_header).json()
        return [ShareLinkDetails(**link_details) for link_details in results]

    def get_upload_links(self, file) -> List[UploadLinkDetails]:
        results = requests.get(uj(self.url, f'api/v2.1/upload-links/?'
                                            f'repo_id={self.id}&'
                                            f'path={urllib.parse.quote(file)}'), headers=self._auth_header).json()
        return [UploadLinkDetails(**link_details) for link_details in results]

    def get_internal_link(self, file, isdir) -> InternalLinkDetails:
        return InternalLinkDetails(**requests.get(uj(self.url, f'api/v2.1/smart-link/?'
                                                               f'repo_id={self.id}&'
                                                               f'path={urllib.parse.quote(file)}&'
                                                               f'is_dir={str(isdir)}'),
                                                  headers=self._auth_header).json())

    def _create_link(self, kind: Literal['share', 'upload'], data) -> Dict:
        return requests.post(uj(self.url, f'api/v2.1/{kind}-links/'), headers=self._auth_header, data=data).json()

    def create_share_link(self, file, permissions: Permissions = None) -> ShareLinkDetails:
        return ShareLinkDetails(**self._create_link('share', {"repo_id": self.id,
                                                              "path": file,
                                                              "permissions": permissions or Permissions()}))

    def create_upload_link(self, file) -> UploadLinkDetails:
        return UploadLinkDetails(**self._create_link('upload', {"repo_id": self.id,
                                                                "path": file}))

    def _delete_link(self, kind: Literal['share', 'upload'], file_token) -> bool:
        return requests.delete(uj(self.url, f'api/v2.1/{kind}-links/{file_token}'),
                               headers=self._auth_header).json()['success']

    def delete_share_link(self, file_token) -> bool:
        return self._delete_link('share', file_token)

    def delete_upload_link(self, file_token) -> bool:
        return self._delete_link('upload', file_token)

    def set_share_link_permissions(self, file_token, permissions: Permissions) -> ShareLinkDetails:
        return requests.put(uj(self.url, f'/api/v2.1/share-links/{file_token}/'),
                            headers=self._auth_header,
                            data={"permissions": permissions}).json()


@dataclass()
class LocalLibrary:
    id: str = ""
    download_head: str = ""
    token: str = ""
    email: str = ""
    relay_address: str = ""
    relay_port: str = ""
    server_url: str = ""
    worktree: str = ""
    sync_worktree_name: str = ""
    remote_head: str = ""
    local_head: str = ""

    def __hash__(self):
        return hash('LocalLibrary' + self.id)

    def __repr__(self):
        return f"<LocalLibrary> id={self.id} name={self.worktree}"

    def contains_file(self, file: str) -> bool:
        if not (os.path.isdir(file) or os.path.isfile(file)):
            return False
        return os.path.samefile(self.worktree, os.path.commonpath([file, self.worktree]))

    def internal_file_path(self, file: str) -> Optional[str]:
        if self.contains_file(file):
            if os.path.relpath(file, self.worktree) == '.':
                return '/'
            else:
                return '/' + os.path.relpath(file, self.worktree)


class RemoteRepository:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def __repr__(self):
        return f"RemoteRepository(url={self.url})"

    def is_reachable(self) -> bool:
        return requests.post(uj(self.url, 'api2/ping')).text == '"pong"'

    @property
    def authorization(self) -> dict:
        return {"Authorization": 'token ' + self.token}

    def match_local_library(self, local_library: LocalLibrary) -> RemoteLibrary:
        try:
            return [rem_lib for rem_lib in self.get_libs() if rem_lib.id == local_library.id][0]
        except IndexError:
            raise MatchingLocalLibraryError(local_library)

    def get_libs(self) -> Set[RemoteLibrary]:
        return {RemoteLibrary(self.url, self.token, **lib)
                for lib in requests.get(uj(self.url, 'api2/repos/?type=mine'), headers=self.authorization).json()}

    def get_libs_as_dict(self) -> Dict[str, RemoteLibrary]:
        return {lib.id: lib for lib in self.get_libs()}


class LocalRepository:
    def __init__(self, file):
        self._file = file
        assert os.path.isfile(self._file)
        self._connection = sqlite3.connect(self._file)
        self._connection.row_factory = sqlite3.Row
        self._cursor = self._connection.cursor()
        self._local_libraries: Set[LocalLibrary] = set()

    def __repr__(self):
        return f"LocalRepository(file={self._file})"

    @property
    def local_libraries(self) -> Set[LocalLibrary]:
        """Finds all local libraries contained by this local repository.

        :return: a set of local libraries
        """
        self._cursor.execute("SELECT * FROM RepoProperty")
        d = defaultdict(dict)
        for row in self._cursor:
            d[row['repo_id']][row['key'].replace('-', '_')] = row['value']
        self._local_libraries = {LocalLibrary(**item, id=_id) for _id, item in d.items()}
        return self._local_libraries

    def match_file(self, file) -> Optional[LocalLibrary]:
        """Finds the local library that contains a file.

        :param file: the file of interest
        :return: the local library containing the file
        """
        for local_lib in self.local_libraries:
            if local_lib.internal_file_path(file):
                return local_lib


class SeafileAccount:
    def __init__(self):
        if sys.platform == 'win32':
            self.ini_file = os.path.join(os.environ["HOMEPATH"], "ccnet", "seafile.ini")
        else:
            self.ini_file = os.path.join(os.environ["HOME"], ".ccnet", "seafile.ini")
        try:
            assert os.path.isfile(self.ini_file)
        except AssertionError:
            raise SeafileConfigFileMissing(self.ini_file)

        with open(self.ini_file, 'r') as f:
            self._seafile_data = f.readline().strip()

        self.accounts_file = os.path.join(self._seafile_data, "accounts.db")
        try:
            assert os.path.isfile(self.accounts_file)
        except AssertionError:
            raise SeafileConfigFileMissing(self.accounts_file)

        self.repo_file = os.path.join(self._seafile_data, "repo.db")
        try:
            assert os.path.isfile(self.repo_file)
        except AssertionError:
            raise SeafileConfigFileMissing(self.repo_file)

        self.url, self.username, self.token = self._get_account_keys()
        self.remote_repository = RemoteRepository(self.url, self.token)
        self.local_repository = LocalRepository(self.repo_file)

    def _get_account_keys(self) -> Tuple[str, str, str]:
        connection = sqlite3.connect(self.accounts_file)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Accounts")
        for row in cursor:
            return row['url'], row['username'], row['token']

    def __repr__(self):
        return f"SeafileAccount(url='{self.url}', username='{self.username}', token='{self.token}')"


class SyncedElement:
    """ This class represents a synchronized element (file or folder) which belongs to both
    one local library and one remote library sharing the same identifier (id).
    Some convenient attributes like 'isdir', 'isroot', 'parent', 'internal_path' or 'shortname' are defined.
    'shortname' represents the file name or the folder name.

    The instance initialisation takes 2 arguments
     + 'account': a SeafileAccount
     + 'file': a path to the file/folder of interest.

    The following exceptions can be raised:
     + FileNotFoundError: if the provided local path is not valid;
     + FileNotSyncedError: if the file/folder is part of no LocalLibrary (owned by 'account');
     + MatchingLocalLibraryError: if the local library has no remote library equivalence (though should never happen).
    """

    def __init__(self, account: SeafileAccount, file: str):
        self.account = account
        self.file = file
        self.short_name = os.path.basename(os.path.normpath(self.file))
        try:
            assert os.path.exists(self.file)
        except AssertionError:
            raise FileNotFoundError(file)
        self.parent = pathlib.Path(file).parent.absolute()
        self.isdir = os.path.isdir(file)
        self.local_library = self.account.local_repository.match_file(self.file)
        try:
            assert isinstance(self.local_library, LocalLibrary)
        except AssertionError:
            raise FileNotSyncedError(file)
        self.internal_file_path = self.local_library.internal_file_path(self.file)
        self.isroot = self.internal_file_path == '/'
        try:
            self.remote_library = self.account.remote_repository.match_local_library(self.local_library)
        except MatchingLocalLibraryError as e:
            raise e

    def __repr__(self):
        return f"SyncedElement(file='{self.file}')"

    @property
    def share_token(self):
        return self.get_share_link_details().token

    @property
    def upload_token(self):
        return self.get_upload_link_details().token

    @property
    def file_details(self) -> Optional[FileDetails]:
        """Gets the details about the file pointed by self.

        :return: a FileDetails object if the element pointed by self is a folder AND is not the library root.
        """
        if not self.isdir:
            return self.remote_library.get_file_details(self.internal_file_path)

    @property
    def dir_details(self) -> Optional[DirectoryDetails]:
        """Gets the details about the folder pointed by self.

        :return: a DirectoryDetails object if the element pointed by self is a folder AND is not the library root.
        """
        if self.isdir and not self.isroot:
            return self.remote_library.get_directory_details(self.internal_file_path)

    def get_share_link_details(self) -> Optional[ShareLinkDetails]:
        """Gets the details about the share link associated to the file/folder pointed by self.
        
        :return: a ShareLinkDetails when link exists, None otherwise.
        """
        if share_link_details := self.remote_library.get_share_links(self.internal_file_path):
            return share_link_details[0]
        else:
            return None

    def get_internal_link_details(self) -> Optional[InternalLinkDetails]:
        """Gets the details about the internal link associated to the file/folder pointed by self.
        
        :return: a ShareLinkDetails when link exists, None otherwise. Internal link SHOULD always exist !
        """
        return self.remote_library.get_internal_link(self.internal_file_path, self.isdir)

    def get_upload_link_details(self) -> Optional[UploadLinkDetails]:
        """Gets the details about the upload link associated to the file/folder pointed by self.

        :return: a ShareLinkDetails when link exists, None otherwise.
        """
        if not self.isdir:
            return None
        if links_details := self.remote_library.get_upload_links(self.internal_file_path):
            return links_details[0]
        else:
            return None

    def get_share_link_url(self) -> Optional[str]:
        """Gets share link url associated to the file/folder pointed by self.

        :return: url if share link exists, None otherwise.
        """
        details = self.get_share_link_details()
        return details.link if details else None

    def get_internal_link_url(self) -> Optional[str]:
        """Gets internal link url associated to the file/folder pointed by self.

        :return: url if internal link exists, None otherwise. Internal link SHOULD always exist!
        """
        details = self.get_internal_link_details()
        return details.link if details else None

    def get_upload_link_url(self) -> Optional[str]:
        """Gets upload link url associated to the folder pointed by self.

        :return: url if upload link exists, None otherwise.
        """
        details = self.get_upload_link_details()
        return details.link if details else None

    def create_share_link(self, permissions: Permissions = None) -> ShareLinkDetails:
        """Requests the creation of a share link to the file/folder.

        :return: link details dictionary
        """
        return self.remote_library.create_share_link(self.internal_file_path, permissions)

    def create_upload_link(self) -> UploadLinkDetails:
        """Requests the creation of an upload link to the folder.

        :return: link details dictionary
        """
        return self.remote_library.create_upload_link(self.internal_file_path)

    def delete_share_link(self) -> bool:
        """Requests the destruction of the share link to the file/folder.

        :return: True if successful
        """
        return self.remote_library.delete_share_link(self.share_token)

    def delete_upload_link(self) -> bool:
        """Requests the destruction of the upload link to the folder.

        :return: True if successful
        """
        return self.remote_library.delete_upload_link(self.upload_token)

    def set_share_link_permissions(self, permissions: Permissions) -> ShareLinkDetails:
        """Requests the modification of a share link permissions.

        :param permissions: permissions object to set
        :return: link details dictionary
        """
        return self.remote_library.set_share_link_permissions(self.share_token, permissions)

    def show_on_cloud(self) -> int:
        """Opens a new tab in the system default web browser and shows the folder content (if a folder)
        or the parent folder content (if a file) in the cloud.

        :return: subprocess.call() return code
        """
        rem_lib = self.remote_library
        loc_lib = self.local_library

        this_object = self.file if self.isdir else self.parent
        url = uj(self.account.url,
                 f'library/{loc_lib.id}/{rem_lib.name}{loc_lib.internal_file_path(this_object)}')
        return subprocess.call(f'xdg-open "{url}"', shell=True)
