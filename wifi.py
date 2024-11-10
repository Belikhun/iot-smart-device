import network
from config import config, set_config, save_config
from logger import scope
import uasyncio as asyncio

log = scope("wifi")
station = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)

def start_access_point():
	name = config("apName")
	ip = config("apIp")
	log("INFO", f"Starting access point \"{name}\" with no password...")

	ap.config(essid=name, authmode=network.AUTH_OPEN)
	ap.ifconfig((ip, "255.255.255.0", ip, ip))
	ap.active(True)

	log("OKAY", "Access point started")
	print_ifconfig(ap.ifconfig())

def stop_access_point():
	log("INFO", "Turning off access point...")
	ap.active(False)

def get_ap_ip():
	return ap.ifconfig()[0]

async def connect_wifi(ssid: str = None, password: str = None):
	if (ssid == None):
		ssid = config("ssid")

	if (password == None):
		password = config("password")

	log("INFO", f"Trying to connect to wifi [{ssid}] (password={password})...")
	station.active(True)
	station.connect(ssid, password)

	failed = False
	tries = 1

	while not station.isconnected():
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
		return False
	
	log("OKAY", f"Successfully connected to wifi {ssid}")
	print_ifconfig(station.ifconfig())

	set_config("ssid", ssid)
	set_config("password", password)
	save_config()

	return True

def get_wifi_ip():
	return station.ifconfig()[0]

def get_wifi_if() -> network.WLAN:
	return station

def scan_wifi():
	return station.scan()

def get_wifi_status():
	status = "UNKNOWN"

	if (station.status() == network.STAT_IDLE):
		status = "IDLE"
	elif (station.status() == network.STAT_CONNECTING):
		status = "CONNECTING"
	elif (station.status() == network.STAT_WRONG_PASSWORD):
		status = "WRONG_PASSWORD"
	elif (station.status() == network.STAT_GOT_IP):
		status = "GOT_IP"
	elif (station.status() == network.STAT_NO_AP_FOUND):
		status = "NO_AP_FOUND"

	return status

def print_ifconfig(data):
	log("INFO", f"  ip address = {data[0]}")
	log("INFO", f" subnet mask = {data[1]}")
	log("INFO", f"     gateway = {data[2]}")
	log("INFO", f"         dns = {data[3]}")
