
def log(level: str, message: str):
	level = level.upper()
	print(f"{level:>5} > {message}")

def scope(scope: str):
	def scope_logger(level: str, message: str) -> None:
		log(level, f"[{scope:>16}] {message}")

	return scope_logger
