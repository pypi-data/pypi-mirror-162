from flask import Blueprint
from aurori.files.fileManager import FileManager

files_bp = Blueprint('files', __name__)

fileManager = FileManager()

from aurori.files import routes  # NOQA: F401
