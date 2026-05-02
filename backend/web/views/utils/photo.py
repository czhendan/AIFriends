import os

from backend import settings


def remove_old_photo(photo):
    if photo and photo.name != 'user/photos/favicon.ico':
        old_path = os.path.join(settings.MEDIA_ROOT, photo.name)
        if os.path.exists(old_path):
            os.remove(old_path)