import re
import sys

from utils import Room
from utils import Colors

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'


class Parser:
	def __init__(self, filename, verbose=True):
		with open(filename, encoding='utf-8') as fd:
			self._file = fd.read().splitlines()
		self._line_id = 0
		self._re_room = re.compile(r"^(\w+) (\d+) (\d+)$")
		self._re_link = re.compile(r"^(\w+)-(\w+)$")
		self._room_dict = {}
		self.allowed_commands = ('start', 'end')
		self.verbose = verbose
		self.ants_num = None
		self.start = None
		self.end = None
		self.rooms = []

	def _check_room(self, new_room):
		if new_room.name.startswith('L'):
			raise SyntaxError(f'Line {self._line_id + 1} | Room name cannot start with L letter')
		if new_room.name in self._room_dict:
			raise SyntaxError(f'Line {self._line_id + 1} | Room with this name already exists')

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

	def _link_rooms(self, room1_name, room2_name):
		room1 = self._room_dict.get(room1_name)
		room2 = self._room_dict.get(room2_name)
		if room1 is None or room2 is None:
			raise SyntaxError(f"Line {self._line_id + 1} | Link with unknown room")
		if room1 in room2.halls or room2 in room1.halls:
			raise SyntaxError(f"Line {self._line_id + 1} | Double linkage")
		room1.halls.append(room2)
		room2.halls.append(room1)

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
				assert command is None, f"Line {self._line_id + 1} | It must be a room after command"
				return
			room = Room(name=match.group(1), x=match.group(2), y=match.group(3))
			self._check_room(room)
			self.rooms.append(room)
			self._room_dict[room.name] = room
			self._apply_command(command, room)
			command = None

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
			match = self._re_link.search(line)
			assert match, f'Line number: {self._line_id + 1} | Wrong format for link'
			self._link_rooms(match.group(1), match.group(2))

	def parse_file(self):
		self._parse_ants_num()
		self._parse_rooms()
		self._parse_links()
		if not self.start or not self.end:
			raise SyntaxError("It must be a start and an end room")
		if self.verbose:
			print(f"{Colors.BOLD}Number of ants: {self.ants_num}{Colors.ENDC}")
			for room in self.rooms:
				print(f"{Colors.HEADER}{room.name} => {[hall.name for hall in room.halls]}{Colors.ENDC}")
			print(f"{Colors.BOLD}Start room: {self.start.name}")
			print(f"{Colors.BOLD}End room: {self.end.name}{Colors.ENDC}")
		self.start.ants_in_room = self.ants_num
