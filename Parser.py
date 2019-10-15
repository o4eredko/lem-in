import re
import sys

from Room import Room

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'


class Parser:
	def __init__(self, filename, verbose=True):
		with open(filename, encoding='utf-8') as fd:
			self._file = fd.read().splitlines()
		self._line_id = 0
		self._re_room = re.compile(r"^(\w+) (\d+) (\d+)$")
		self._re_link = re.compile(r"")
		self.ants_num = None
		self.start = None
		self.end = None
		self.rooms = []
		self.allowed_commands = ('start', 'end')
		self.verbose = verbose

	def _check_room(self, new_room):
		if new_room.name.startswith('L'):
			raise SyntaxError(f'Line {self._line_id + 1} | Room name cannot start with L letter')
		for room in self.rooms:
			if room.name == new_room.name:
				raise SyntaxError(f'Line {self._line_id + 1} | Room with this name already exists')
			elif room.x == new_room.x and room.y == new_room.y:
				raise SyntaxError(f'Line {self._line_id + 1} | Room with such coordinates already exists')

	def _parse_ants_num(self):
		for self._line_id in range(self._line_id, len(self._file)):
			line = self._file[self._line_id]
			if self.verbose:
				print(line)
			assert line, f"Line {self._line_id + 1} | Empty line"
			if line.isdigit():
				self.ants_num = int(line)
				self._line_id += 1
				return
			elif line.startswith('##'):
				raise SyntaxError(f'Line number: {self._line_id + 1} | Commands are not allowed in this section')
			elif not line.startswith('#'):
				raise SyntaxError(f'Line number: {self._line_id + 1} | Invalid number of ants')

	def _parse_rooms(self):
		command = None
		for self._line_id in range(self._line_id, len(self._file)):
			line = self._file[self._line_id]
			if self.verbose:
				print(line)
			assert line, f"Line {self._line_id + 1} | Empty line"
			if line.startswith('#'):
				if line.startswith('##'):
					assert command is None, f"Line {self._line_id + 1} | 2 commands in a row"
					command = self._check_command(line)
				continue
			match = re.search(self._re_room, line)
			if not match:
				return
			room = Room(name=match.group(1), x=match.group(2), y=match.group(3))
			self._check_room(room)
			self.rooms.append(room)
			self._apply_command(command, room)
			command = None

	def _check_command(self, line):
		command = line[2:]
		if command not in self.allowed_commands:
			raise SyntaxError(f"Line {self._line_id + 1} | Unknown command")
		return command

	def _apply_command(self, command, room):
		if command == 'start':
			assert not self.start, f"Line {self._line_id + 1} | Start room is already exist"
			self.start = room
		elif command == "end":
			assert not self.end, f"Line {self._line_id + 1} | End room is already exist"
			self.end = room

	def _parse_links(self):
		sys.stdout.write("\033[F")
		sys.stdout.write("\033[K")
		for self._line_id in range(self._line_id, len(self._file)):
			line = self._file[self._line_id]
			if self.verbose:
				print(line)
			assert line, f"Line {self._line_id + 1} | Empty line"
			if line.startswith('#'):
				if line.startswith('##'):
					raise SyntaxError(f'Line number: {self._line_id + 1} | Commands are not allowed in this section')
				continue
			rooms = line.split('-')
			self.append_halls(rooms[0], rooms[1])

	def parse_file(self):
		self._parse_ants_num()
		self._parse_rooms()
		self._parse_links()
		if not self.start or not self.end:
			raise SyntaxError("It must be a start and an end room")
		if self.verbose:
			print(f"\nNumber of ants: {self.ants_num}")
			for room in self.rooms:
				print(f"{room.name}:")
				for hall in room.halls:
					print(f"---->{hall.name}")
			print(f"Start room: {self.start.name}")
			print(f"Start room: {self.end.name}")
		self.start.ants_in_room = self.ants_num

	def append_halls(self, room_to_link, linked_room):
		room1 = None
		room2 = None
		for room in self.rooms:
			if room.name == room_to_link:
				room1 = room
			elif room.name == linked_room:
				room2 = room
		if not room1 or not room2:
			raise SyntaxError(f"Line {self._line_id + 1} | Link with unknown room")
		if room1 in room2.halls or room2 in room1.halls:
			raise SyntaxError(f"Line {self._line_id + 1} | Double linkage")
		room1.halls.append(room2)
		room2.halls.append(room1)
