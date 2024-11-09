from logger import scope
from wifi import get_ap_ip
import socket
import uasyncio as asyncio
import gc

log = scope("dns")

class DNSQuery:
	def __init__(self, data):
		self.data = data
		self.domain = ""
		tipo = (data[2] >> 3) & 15  # Opcode bits

		if tipo == 0:  # Standard query
			ini = 12
			lon = data[ini]
			while lon != 0:
				self.domain += data[ini + 1:ini + lon + 1].decode("utf-8") + "."
				ini += lon + 1
				lon = data[ini]

		log("INFO", f"Searched domain: {self.domain}")

	def response(self, ip):
		log("INFO", f"Response {self.domain} == {ip}")

		if self.domain:
			packet = self.data[:2] + b'\x81\x80'
			packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'  # Questions and Answers Counts
			packet += self.data[12:]  # Original Domain Name Question
			packet += b'\xC0\x0C'  # Pointer to domain name
			packet += b'\x00\x01\x00\x01\x00\x00\x00\x3C\x00\x04'  # Response type, ttl and resource data length -> 4 bytes
			packet += bytes(map(int, ip.split('.')))  # 4bytes of IP

		return packet

async def start_dns_server():
	apIp = get_ap_ip()
	udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# set non-blocking otherwise execution will stop at 'recvfrom' until a connection is received
	# and this will prevent the other async threads from running
	udps.setblocking(False)

	# bind to port 53 on all interfaces
	udps.bind(("0.0.0.0", 53))
	log("OKAY", "DNS server started")

	while True:
		try:
			gc.collect()

			data, addr = udps.recvfrom(4096)
			log("INFO", "Incoming data...")

			DNS = DNSQuery(data)
			udps.sendto(DNS.response(apIp), addr)

			log("OKAY", "Replying: {:s} -> {:s}".format(DNS.domain, apIp))
			await asyncio.sleep_ms(100)

		except Exception as excp:
			await asyncio.sleep_ms(3000)
