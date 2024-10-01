import string
from random import random

from legacy.models import WebUsers





def generate_random_name(length=20):
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return random_name

