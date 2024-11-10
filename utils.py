import os

def path_exists(path):
	try:
		# Try to list the directory or open the file
		os.stat(path)
		return True
	except OSError:
		return False
