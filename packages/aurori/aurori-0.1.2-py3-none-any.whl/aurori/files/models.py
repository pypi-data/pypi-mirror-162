from aurori import db
from sqlalchemy import and_
from datetime import datetime
import enum
import uuid
import sys
from importlib.machinery import SourceFileLoader
from urllib.parse import quote
#from werkzeug.utils import secure_filename


class FileStorageType(enum.IntFlag):
    LOCAL = 1
    NETWORK = 2


class FileStorage(db.Model):
    __tablename__ = 'files_filestorages'

    # "server_default" is set on database by migration
    id = db.Column(db.Integer, primary_key=True)
    storage_type = db.Column(db.Enum(FileStorageType),
                             nullable=False,
                             server_default='LOCAL')
    path = db.Column(db.String, default='')
    is_default = db.Column(db.Boolean, nullable=False, server_default='0')

    def __init__(self, storage_type=None, path=None, is_default=False):
        if storage_type:
            self.storage_type = storage_type
        if path:
            self.path = path
        if is_default:
            self.set_default()

    def __repr__(self):
        return '<{} of type {} with path: {} (is default: {})>'.format(
            self.id,
            self.storage_type.name,
            self.path,
            self.is_default,
        )

    def set_default(self):
        # unset others before setting self
        storages = FileStorage.query.filter(
            and_(
                FileStorage.is_default == True,  # NOQA: E712
                FileStorage.id != self.id,
            )).all()
        for storage in storages:
            storage.is_default = False
        self.is_default = True
        # fixme: when changing the default storage, app reload is required
        # we should update the default in the fileManager

    def store_file(self, file, user, display_name=None, workspace=None):
        try:
            file_object = File(self.id)
            # fixme: we shoudl use secure_filename(file.filename) and store the original name in display_name
            file_object.file_name = file.filename
            file_object.user_id = user.id
            file_object.size = sys.getsizeof(file)
            if display_name:
                file_object.display_name = display_name
            if workspace:
                file_object.workspace = workspace

            backend_name = self.storage_type.name.lower()
            storage_backend = SourceFileLoader(
                'storage_backend',
                f'core/files/storage_backends/{backend_name}.py').load_module(
                )
            storage = storage_backend.Storage()
            if storage.store_file(self, file, file_object) is not True:
                return False, {}

            db.session.add(file_object)
            db.session.commit()

            return True, {
                'id': file_object.id,
                'file_name': file_object.file_name,
            }
        except Exception:
            return False, {}

    def load_file(self, file_object):
        try:
            backend_name = self.storage_type.name.lower()
            storage_backend = SourceFileLoader(
                'storage_backend',
                f'core/files/storage_backends/{backend_name}.py').load_module(
                )
            storage = storage_backend.Storage()
            file_data = storage.load_file(file_object)
            return file_data
        except Exception:
            return None

    def delete_file(self, file_object):
        try:
            backend_name = self.storage_type.name.lower()
            storage_backend = SourceFileLoader(
                'storage_backend',
                f'core/files/storage_backends/{backend_name}.py').load_module(
                )
            storage = storage_backend.Storage()
            storage.remove_file(file_object)
            db.session.delete(file_object)
            db.session.commit()
            return True
        except Exception:
            return False


class File(db.Model):
    __tablename__ = 'files_files'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String, nullable=False)
    display_name = db.Column(db.String, default='')
    workspace = db.Column(db.String, default='')
    uuid_string = db.Column(db.String)
    date_added = db.Column(db.DateTime, nullable=False)
    size_in_bytes = db.Column(db.Integer, default=0)
    filestorage_id = db.Column(db.Integer,
                               db.ForeignKey(FileStorage.id),
                               nullable=False)
    filestorage = db.relationship(
        FileStorage,
        backref='files',
        foreign_keys=filestorage_id,
    )
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='SET NULL'))
    user = db.relationship(
        'User',
        backref='files',
        foreign_keys=user_id,
    )
    path = db.Column(db.String)
    mime_type = db.Column(db.String)

    def __init__(self, filestorage_id):
        self.filestorage_id = filestorage_id
        self.date_added = datetime.utcnow()
        self.uuid_string = str(uuid.uuid4())

    def __repr__(self):
        return 'File {} on file storage [{}], added {} by user with id [{}]'.format(
            self.file_name,
            self.filestorage_id,
            self.date_added.strftime('%Y-%m-%d %H:%M:%s'),
            self.user_id,
        )

    @property
    def file_data(self):
        return self.filestorage.load_file(self)

    @property
    def link(self):
        # this kind of links has to be handled by the webserver
        # fixme: this works for local files only
        if self.filestorage.storage_type.name == 'LOCAL':
            link = '/uploads/{}/{}/{}/{}/{}'.format(
                self.workspace or 'generic',
                self.uuid_string[0:2],
                self.uuid_string[2:4],
                self.uuid_string,
                self.file_name,
            )
            return quote(link)
        else:
            return False

    def delete(self):
        return self.filestorage.delete_file(self)
