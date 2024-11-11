import network
from config import config, set_config, save_config
from logger import scope
import uasyncio as asyncio
from utils import hw_id, status_led

log = scope("wifi")
WIFI_STA = None
WIFI_AP = None

def start_access_point():
	global WIFI_AP

	name = config("name") + f" - {hw_id()}"
	ip = config("apIp")
	log("INFO", f"Starting access point \"{name}\" with no password...")

	if not WIFI_AP:
		WIFI_AP = network.WLAN(network.AP_IF)
		WIFI_AP.config(essid=name, authmode=network.AUTH_OPEN)
		WIFI_AP.ifconfig((ip, "255.255.255.0", ip, ip))

	WIFI_AP.active(True)

	log("OKAY", "Access point started")
	print_ifconfig(WIFI_AP.ifconfig())

def stop_access_point():
	log("INFO", "Turning off access point...")
	WIFI_AP.active(False)

def get_ap_ip():
	global WIFI_AP
	return WIFI_AP.ifconfig()[0]

def start_wifi():
	global WIFI_STA
	if not WIFI_STA:
		log("INFO", f"Starting station wifi...")
		WIFI_STA = network.WLAN(network.STA_IF)
		WIFI_STA.active(True)

def stop_wifi():
	global WIFI_STA
	log("INFO", f"Stopping station wifi...")
	WIFI_STA.active(False)
	WIFI_STA = None

async def disconnect_wifi():
	global WIFI_STA

	if WIFI_STA and WIFI_STA.isconnected():
		log("INFO", f"Disconnecting current wifi connection...")
		WIFI_STA.disconnect()

		while WIFI_STA.isconnected():
			await asyncio.sleep(1)

		stop_wifi()
		start_wifi()
		set_config("ssid", None)
		set_config("password", None)

async def connect_wifi(ssid: str = None, password: str = None):
	global WIFI_STA
	status = status_led()

	if not ssid:
		ssid = config("ssid")
		password = config("password")

	log("INFO", f"Trying to connect to wifi [{ssid}] (password={password})...")
	status.start_animation("blink", color=(0, 255, 0), duration=0.1)

	if (WIFI_STA.isconnected()):
		await disconnect_wifi()

	if password:
		WIFI_STA.connect(ssid, password)
	else:
		WIFI_STA.connect(ssid)

	failed = False
	tries = 1

	while not WIFI_STA.isconnected():
		status = get_wifi_status()

		if (status == "WRONG_PASSWORD" or status == "NO_AP_FOUND"):
			failed = True
			log("ERRR", f"Connection failed: {status}")
			break

		if (status == "GOT_IP"):
			break

		if (tries >= 20):
			log("WARN", f"Wifi connection timed out after {tries} tries. Aborting...")
			failed = True
			break

		log("DEBG", f"Connection status: {status}, tries {tries}/20")
		tries += 1
		await asyncio.sleep(1)

	if (failed):
		log("ERRR", f"Connection to \"{ssid}\" failed")
		status.start_animation("blink", color=(255, 0, 0), duration=0.5)
		return False

	log("OKAY", f"Successfully connected to wifi {ssid}")
	status.stop_animation()
	status.set_color((0, 255, 0))
	print_ifconfig(WIFI_STA.ifconfig())

	set_config("ssid", ssid)
	set_config("password", password)
	save_config()

	return True

def get_wifi_ip():
	global WIFI_STA
	return WIFI_STA.ifconfig()[0]

def get_wifi_if() -> network.WLAN:
	global WIFI_STA
	return WIFI_STA

def scan_wifi():
	global WIFI_STA
	return WIFI_STA.scan()

def get_wifi_status():
	global WIFI_STA
	status = "UNKNOWN"

	if (WIFI_STA.status() == network.STAT_IDLE):
		status = "IDLE"
	elif (WIFI_STA.status() == network.STAT_CONNECTING):
		status = "CONNECTING"
	elif (WIFI_STA.status() == network.STAT_WRONG_PASSWORD):
		status = "WRONG_PASSWORD"
	elif (WIFI_STA.status() == network.STAT_GOT_IP):
		status = "GOT_IP"
	elif (WIFI_STA.status() == network.STAT_NO_AP_FOUND):
		status = "NO_AP_FOUND"

	return status

def print_ifconfig(data):
	log("INFO", f"  ip address = {data[0]}")
	log("INFO", f" subnet mask = {data[1]}")
	log("INFO", f"     gateway = {data[2]}")
	log("INFO", f"         dns = {data[3]}")
