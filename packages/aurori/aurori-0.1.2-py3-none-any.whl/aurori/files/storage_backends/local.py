from aurori.files.storage_backends.base import BaseStorage

import os


class Storage(BaseStorage):
    def store_file(self, file_storage, file, file_object):
        try:
            path = os.path.join(
                file_storage.path,
                file_object.workspace or 'generic',
                file_object.uuid_string[0:2],
                file_object.uuid_string[2:4],
                file_object.uuid_string,
            )

            os.makedirs(path, exist_ok=True)
            file.save(os.path.join(path, file_object.file_name))
            file_object.path = path
            file_object.mime_type = file.content_type
            file_object.size_in_bytes = os.path.getsize(
                os.path.join(path, file_object.file_name))
            return True
        except Exception:
            return False

    def load_file(self, file_object):
        try:
            return open(os.path.join(file_object.path, file_object.file_name),
                        'r+b').read()
        except Exception:
            return None

    def remove_file(self, file_object):
        try:
            file_path = os.path.join(file_object.path, file_object.file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                os.removedirs(file_object.path)
            return True
        except Exception:
            return False
