import re
from Room import Room


class Parser:
	def __init__(self, filename):
		self.fd = open(filename, 'r')
		self.file = self.fd.read().splitlines()
		self.file_len = len(self.file)
		self.line_id = 0
		self.ants_num = None
		self.rooms = []
		self.start = None
		self.end = None

	def check_room_existent(self, new_room):
		for room in self.rooms:
			if room.name == new_room.name:
				raise Exception(f'Line {self.line_id + 1}: Room with this name already exists')
			elif room.x == new_room.x and room.y == new_room.y:
				raise Exception(f'Line {self.line_id + 1}: Room with such coordinates already exists')

	def parse_ants_num(self):
		while self.line_id < self.file_len:
			line = self.file[self.line_id]
			print(line)
			if line.isdigit():
				self.ants_num = int(line)
				self.line_id += 1
				return
			elif not line or line[0] != '#':
				raise Exception(f'Line number: {self.line_id + 1}\nInvalid number of ants')
		self.line_id += 1

	def parse_rooms(self):
		while self.line_id < self.file_len:
			line = self.file[self.line_id]
			if not line:
				raise Exception(f"Line {self.line_id + 1}: Empty line")
			if line[0] == '#':
				if line[1] == '#':
					self.parse_command(line)
				print(line)
				self.line_id += 1
				continue
			match = re.search(r"^(\w+) (\d+) (\d+)$", line)
			if not match:
				return
			print(line)
			room = Room(name=match.group(1), x=match.group(2), y=match.group(3))
			self.check_room_existent(room)
			self.rooms.append(room)
			self.line_id += 1

	def parse_command(self, command):
		if command != "##start" and command != "##end":
			raise Exception(f"Line {self.line_id + 1}: Unknown command")
		line = self.file[self.line_id + 1]
		print(line)
		match = re.search(r"^(\w+) (\d+) (\d+)$", line)
		if not match:
			raise Exception(f"Line {self.line_id + 1}: It must be a room after command")
		room = Room(name=match.group(1), x=match.group(2), y=match.group(3))
		self.check_room_existent(room)
		self.rooms.append(room)
		if command == "##start":
			if self.start:
				raise Exception(f"Line {self.line_id + 1}: It can be only one start room")
			self.start = room
		elif command == "##end":
			if self.end:
				raise Exception(f"Line {self.line_id + 1}: It can be only one end room")
			self.end = room
		self.line_id += 1

	def parse_links(self):
		while self.line_id < self.file_len:
			line = self.file[self.line_id]
			if not line:
				raise Exception(f"Line {self.line_id + 1}: Empty line")
			print(line)
			if line[0] == '#':
				self.line_id += 1
				continue
			rooms = line.split('-')
			self.append_halls(rooms[0], rooms[1])
			self.line_id += 1

	def parse_file(self):
		self.parse_ants_num()
		self.parse_rooms()
		self.parse_links()
		if not self.start or not self.end:
			raise Exception("It must be a start and an end room")
		print(f"\nNumber of ants: {self.ants_num}")
		for room in self.rooms:
			print(f"{room.name}:")
			for hall in room.halls:
				print(f"\t{hall.name}")
		print(f"Start room: {self.start.name}")
		print(f"Start room: {self.end.name}")

	def append_halls(self, room_to_link, linked_room):
		room1 = None
		room2 = None
		for room in self.rooms:
			if room.name == room_to_link:
				room1 = room
			elif room.name == linked_room:
				room2 = room
		if not room1 or not room2:
			raise Exception(f"Line {self.line_id + 1}: Link with unknown room")
		if room1 in room2.halls or room2 in room1.halls:
			raise Exception(f"Line {self.line_id + 1}: Double linkage")
		room1.halls.append(room2)
		room2.halls.append(room1)
