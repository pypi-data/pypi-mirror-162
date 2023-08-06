from os.path import splitext, basename, join
import uuid
import random
import string
import re
from django.contrib.auth.hashers import make_password
from random import randint


def randomString(stringLength=8):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def notificaion_unique_file_path(instance, filename):
    # Get new file name/upload path
    base, ext = splitext(filename)
    newname = "%s%s%s" % (randomString(), '-' + base, ext)
    upload_dir = 'notification_media'
    return join(upload_dir, newname)
