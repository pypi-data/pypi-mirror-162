from typing import Tuple
from aurori.logs import logManager


class FileManager(object):
    """ The FileManager ...
    """
    def __init__(self, ):
        # preparation to instanciate
        self.config = None
        self.app = None
        self.db = None
        self.filestorages = None
        self.default_storage = None

    def init_manager(self, app, db, config):
        self.config = config
        self.app = app
        self.db = db

        logManager.info('Loading filestorages …')

    def get_file(self, uuid_string) -> Tuple[bytes, str, str]:
        from .models import File

        file_object = File.query.filter_by(uuid_string=uuid_string).first()
        if file_object:
            return file_object.file_data, file_object.file_name, file_object.mime_type
        else:
            return None, None, None

    def store_file(self, file, user, filestorage_id=None, workspace=None):
        # fixme: only uploads to the default storage now
        return self.default_storage.store_file(file, user, workspace=workspace)

    def delete_file(self, uuid_string) -> Tuple[str, str]:
        from .models import File

        file_object = File.query.filter_by(uuid_string=uuid_string).first()
        if file_object:
            file_name = file_object.file_name
            if file_object.delete():
                return 'SUCCESS', file_name
            else:
                return 'DELETION FAILED', file_name
        else:
            return 'NOT FOUND', None
