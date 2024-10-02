import string
import random

def generate_random_name(length=20):
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return random_name

