import re
from Room import Room

class Parser:
	def __init__(self, filename):
		self.fd = open(filename, 'r')
		self.file = self.fd.read().splitlines()
		self.line_id = 0
		self.ants_num = None
		self.rooms = []
		self.start = None
		self.end = None

	def parse_ants_num(self):
		for self.line_id in range(len(self.file)):
			line = self.file[self.line_id]
			print(line)
			if line.isdigit():
				self.ants_num = int(line)
				return
			elif not line or line[0] != '#':
				raise Exception(f'Line number: {self.line_id + 1}\nInvalid number of ants')

	def parse_rooms(self):
		for self.line_id in range(self.line_id + 1, len(self.file)):
			line = self.file[self.line_id]
			print(line)
			if not line:
				raise Exception("Line number: {self.line_id + 1}\nEmpty line")
			if line[0] == '#':
				if line[1] == '#':
					self.parse_command(line)
				continue
			match = re.search(r"^(\w+)(\d+) (\d+)$", line)
			if not match:
				self.line_id -= 1
				return
			room = Room(name=match.group(1), x=match.group(2), y=match.group(3))
			self.rooms.append(room)

	def parse_command(self, command):
		if command != "##start" and command != "##end":
			raise Exception("Line number: {self.line_id + 1}\nUnknown command")
		line = self.file[self.line_id + 1]
		print(line)
		match = re.search(r"^(\w+)(\d+) (\d+)$", line)
		if not match:
			Exception("Line number: {self.line_id + 1}\nIt must be a room after command")
		room = Room(name=match.group(1), x=match.group(2), y=match.group(3))
		self.rooms.append(room)
		if command == "##start":
			if self.start:
				raise Exception("Line number: {self.line_id + 1}\nIt can be only one start room")
			self.start = room
		elif command == "##end":
			if self.end:
				raise Exception("Line number: {self.line_id + 1}\nIt can be only one end room")
			self.end = room

	def parse_file(self):
		self.parse_ants_num()
		print(f"Number of ants: {self.ants_num}")
		self.parse_rooms()
		for room in self.rooms:
			print(f"ROOM {room.name}")