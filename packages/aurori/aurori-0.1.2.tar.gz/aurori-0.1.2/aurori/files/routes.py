from aurori.files import files_bp
from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from aurori.logs import logManager
from aurori.users import userManager

from . import fileManager


@files_bp.route('/api/v1/file/download/<uuid_string>', methods=['GET'])
@jwt_required
def file_request(uuid_string):
    jwt_id = get_jwt_identity()
    user = None
    if jwt_id:
        user = (userManager.getUser(jwt_id))

    if user:
        file, file_name, mime_type = fileManager.get_file(uuid_string)
        if file:
            logManager.info('File "{}" downloaded by user {}'.format(
                file_name, user))
            response = Response(file, mimetype=mime_type)
            response.headers.set('Content-Disposition',
                                 'attachment',
                                 filename=file_name)
            return response
        else:
            return 'File not found.', 404
    return 'Not authorized.', 401


@files_bp.route('/api/v1/file/upload', methods=['POST'])
@jwt_required
def upload_request():
    jwt_id = get_jwt_identity()
    user = None
    if jwt_id:
        user = (userManager.getUser(jwt_id))

    try:
        workspace = request.form.get('workspace')
    except Exception:
        workspace = None

    if user:
        logManager.info('File upload for user {}'.format(user))
        uploaded_files = []
        for file in request.files.values():
            success, file_info = fileManager.store_file(file,
                                                        user,
                                                        workspace=workspace)
            if success:
                uploaded_files.append(file_info)
            else:
                return 'Upload failed', 500
        return jsonify(uploaded_files), 200
    return 'Not authorized.', 401


@files_bp.route('/api/v1/file/delete/<uuid_string>', methods=['GET'])
@jwt_required
def delete_request(uuid_string):
    jwt_id = get_jwt_identity()
    user = None
    if jwt_id:
        user = (userManager.getUser(jwt_id))

    if user:
        status, file_name = fileManager.delete_file(uuid_string)
        if status == 'SUCCESS':
            logManager.info('File "{}" deleted by user {}'.format(
                file_name, user))
            return 'Successfully deleted', 200
        else:
            return 'Deletion failed', 500
    return 'Not authorized.', 401
