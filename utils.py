import os

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
