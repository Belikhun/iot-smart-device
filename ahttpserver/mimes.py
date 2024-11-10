# Dictionary of common file extensions and their MIME types
MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".txt": "text/plain",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".xml": "application/xml"
}

def get_mime_type(filename):
    # Extract the file extension
    ext = filename[filename.rfind("."):].lower()
    # Return the matching MIME type or a default type
    return MIME_TYPES.get(ext, "application/octet-stream")
