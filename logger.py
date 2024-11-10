
SYSLOGS = []

def log(level: str, message: str):
	global SYSLOGS

	level = level.upper()
	line = f"{level:>5} > {message}"
	SYSLOGS.append(line)
	print(line)

def get_logs(from_index: int = 0):
	global SYSLOGS

	if (from_index == 0):
		return SYSLOGS

	return SYSLOGS[from_index:]

def scope(scope: str):
	def scope_logger(level: str, message: str) -> None:
		log(level, f"[{scope:>16}] {message}")

	return scope_logger
