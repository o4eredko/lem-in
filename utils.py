class Room:
	def __init__(self, name, x, y):
		self.name = name
		self.x = int(x)
		self.y = int(y)
		self.ants_in_room = 0
		self.halls = []
		self.added_by = None
		self.input = None
		self.output = None


class Colors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
