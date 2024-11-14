import os
import machine
from components import RGBLed, Buzzer
from logger import log
import client

HARDWARE_ID = None

statled = RGBLed(0, 2, 15)
statled.start_animation("blink", color=(0, 0, 255))
statbuz = Buzzer(5)

def status_led():
	global statled
	return statled

def status_buzz():
	global statbuz
	return statbuz

def uuidv4():
    random_bytes = bytearray(os.urandom(16))
    random_bytes[6] = (random_bytes[6] & 0x0F) | 0x40
    random_bytes[8] = (random_bytes[8] & 0x3F) | 0x80
    return "{:02x}{:02x}{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
        *random_bytes
	)

def hw_id():
	global HARDWARE_ID

	if HARDWARE_ID:
		return HARDWARE_ID

	HARDWARE_ID = machine.unique_id().hex()
	return HARDWARE_ID

def path_exists(path):
	try:
		# Try to list the directory or open the file
		os.stat(path)
		return True
	except OSError:
		return False

async def send_response_in_chunks(writer, response_body, chunk_size=512):
	response_view = memoryview(response_body)

	# Send data in chunks
	for i in range(0, len(response_body), chunk_size):
		chunk = response_view[i:i + chunk_size]
		writer.write(chunk)
		await writer.drain()

	# Close the connection
	writer.close()

def uri_decode(s):
	decoded = ''
	i = 0
	while i < len(s):
		if s[i] == '%':
			decoded += chr(int(s[i+1:i+3], 16))
			i += 3
		else:
			decoded += s[i]
			i += 1
	return decoded

async def reset_device():
	log("WARN", "RESETTING DEVICE...")
	log("WARN", "RESETTING DEVICE...")
	log("WARN", "RESETTING DEVICE...")
	await client.ws_stop_loop()
	machine.reset()
