from logger import scope
import json

log = scope("config")
CONFIG_UPDATED = False
CONFIG = {}

def load_config():
	global CONFIG, CONFIG_UPDATED

	with open("config.json") as file:
		log("INFO", "Reading configuration file...")
		CONFIG = json.loads(file.read())

		for key, value in CONFIG.items():
			log("INFO", f"{key:>12} = {value}")

	CONFIG_UPDATED = False

def set_config(key: str, value: str|None):
	global CONFIG, CONFIG_UPDATED

	if (config(key) == value):
		return

	log("INFO", f"{key:>12} = {value}")
	CONFIG[key] = value
	CONFIG_UPDATED = True

def save_config():
	global CONFIG, CONFIG_UPDATED

	if (CONFIG_UPDATED):
		log("INFO", "No config were changed, save_config() aborted.")
		return

	log("INFO", "Saving configuration file...")
	with open("config.json", "w") as file:
		file.write(json.dumps(CONFIG))

	log("OKAY", "Configuration file saved!")

def config(key: str, default = None) -> str|None:
	global CONFIG
	return CONFIG.get(key, default)

load_config()
