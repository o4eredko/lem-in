class Room:
	def __init__(self, name, x, y):
		self.name = name
		self.x = int(x)
		self.y = int(y)
		self.halls = []
