"""
This is the development environment configuration file.
Rename it to config_prod.py for the production environment.

config_prod.py wil **not** be pushed to the repository for
security reasons.
"""
import os

ROOT_FOLDER = '/var/www/crmapi'
# Change the SECRET_KEY
SECRET_KEY = 'XAhR5ffu0jGy2dPPSiFSEJYRplJvlaImzV4GZQN7nIk'
# Change the administrator password
# for the user marduk
ADMIN_PROD_PASSWORD = 'exampleAdminProductionPassword'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
JSON_SORT_KEYS = False

_DATABASE_NAME = 'app.sqlite'
_DATABASE_FOLDER = 'data'
DATABASE = os.path.join(ROOT_FOLDER, _DATABASE_FOLDER, _DATABASE_NAME)

IMG_UPLOAD_FOLDER_RELATIVE_STATIC = 'images'
IMG_UPLOAD_FOLDER = os.path.join(
    ROOT_FOLDER, 'static', IMG_UPLOAD_FOLDER_RELATIVE_STATIC)
