"""
This is the development environment configuration file.
Rename it to config_prod.py for the production environment.

config_prod.py wil **not** be pushed to the repository for
security reasons.
"""
import os

_WORK_DIR = '/Users/samuel/devl/crmapi'
_DATABASE_NAME = 'app.sqlite'
SECRET_KEY = 'XAhR5ffu0jGy2dPPSiFSEJYRplJvlaImzV4GZQN7nIk'
DATABASE = os.path.join(_WORK_DIR, '/data/', _DATABASE_NAME)
IMG_UPLOAD_FOLDER_RELATIVE_STATIC = 'images',
IMG_UPLOAD_FOLDER = os.path.join(
    _WORK_DIR, 'static', IMG_UPLOAD_FOLDER_RELATIVE_STATIC)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'},
JSON_SORT_KEYS = False
