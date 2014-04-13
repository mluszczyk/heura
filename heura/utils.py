import random
import string
from hashlib import sha256

def getints(line):
	return map(int, line.split())

def random_string(len):
	return ''.join(random.choice(string.digits+string.ascii_letters) for _ in range(len))

def hash_string(x):
	return sha256((x).encode()).hexdigest()


