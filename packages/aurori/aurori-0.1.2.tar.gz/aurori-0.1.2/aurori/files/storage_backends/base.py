class BaseStorage:

    def store_file(self, file, file_object, file_storage=None):
        return NotImplemented

    def load_file(self, file_object):
        return NotImplemented

    def remove_file(self, file_object):
        return NotImplemented
