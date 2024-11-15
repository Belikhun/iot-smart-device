
SYSLOGS = []
SYSLOGS_OFFSET = 0

def log(level: str, message: str, end="\n"):
	global SYSLOGS, SYSLOGS_OFFSET

	level = level.upper()
	line = f"{level:>5} > {message}"
	SYSLOGS.append(line)
	print(line, end=end)

	if len(SYSLOGS) > 100:
		SYSLOGS.pop(0)
		SYSLOGS_OFFSET += 1

def get_logs(from_index: int = 0):
	global SYSLOGS, SYSLOGS_OFFSET

	if (from_index == 0):
		return SYSLOGS

	from_index -= SYSLOGS_OFFSET
	return SYSLOGS[from_index:]

def scope(scope: str):
	def scope_logger(level: str, message: str, end="\n") -> None:
		log(level, f"[{scope:>16}] {message}", end=end)

	return scope_logger
