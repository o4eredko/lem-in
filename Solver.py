import collections
import copy

from utils import Colors


def prev_current_next(iterable):
	"""
	Make a generator that yields an (previous, current, next) tuple per element.
	:return None if the value does not make sense (i.e. previous before
	first and next after last).
	"""
	iterable = iter(iterable)
	prev = None
	cur = next(iterable)
	try:
		while True:
			nxt = next(iterable)
			yield (prev, cur, nxt)
			prev = cur
			cur = nxt
	except StopIteration:
		yield (prev, cur, None)


class Solver:
	def __init__(self, src):
		self._round = 0
		self.steps = 0
		self.ants_num = src.ants_num
		self.rooms = src.rooms
		self.start = src.start
		self.end = src.end
		self.routes = []
		self.final_routes = []
		self.best_score = None
		self.ants = [self.start] * self.ants_num
		self.max_routes = min(self.ants_num, len(self.start.halls), len(self.end.halls))

	def _count_steps(self, routes):
		if not len(routes):
			return float('inf')
		steps = 0
		ants_moved = 0
		while ants_moved < self.ants_num:
			steps += 1
			for route in routes:
				if len(route) <= steps:
					ants_moved += 1
		return steps

	def _save_route(self):
		new_route = []
		tmp = self.end
		while tmp.added_by and tmp != self.start:
			new_route.append(tmp)
			try:
				tmp.added_by.halls.remove(tmp)
			except ValueError:
				pass
			tmp = tmp.added_by
		new_route.append(self.start)
		new_route.reverse()
		self.routes.append(new_route)

		for prev, cur, nxt in prev_current_next(new_route):
			if cur == self.start or cur == self.end or cur.input is not None or cur.output is not None:
				continue
			if prev.output is not None:
				prev = prev.output
			if nxt.input is not None:
				nxt = nxt.input

			duplicate = copy.copy(cur)
			duplicate.halls = cur.halls[:]
			duplicate.input = cur
			cur.output = duplicate

			cur.halls = [prev] if prev in cur.halls else []
			try:
				duplicate.halls.remove(prev)
			except ValueError:
				pass
			duplicate.halls.append(cur)

			try:
				nxt.halls[nxt.halls.index(cur)] = duplicate
			except ValueError:
				pass

	def _bfs(self):
		"""
		Breadth-First Search. Finds the shortest path and saves it to self.routes
		:return: bool, True if new route was found, otherwise False
		"""
		self._round += 1
		visited = {self.start}
		queue = collections.deque((self.start,))
		while len(queue):
			room = queue.popleft()
			if room == self.end:
				self._save_route()
				return True
			for hall in room.halls:
				if hall not in visited:
					hall.added_by = room
					visited.add(hall)
					queue.append(hall)
		return False

	def print_routes(self, routes):
		print(f"{Colors.HEADER}Paths found: {Colors.ENDC}")
		if not len(routes):
			print(f"{Colors.WARNING}{Colors.BOLD}No paths{Colors.ENDC}")
			return None
		for route in routes:
			print(f"{Colors.OKBLUE}{self.start.name}{Colors.ENDC}", end='')
			for room in route:
				print(f" ==> {Colors.OKBLUE}{room.name}{Colors.ENDC}", end='')
			print()
		print(f"{Colors.OKGREEN}Efficiency: {self._count_steps(routes)}{Colors.ENDC}")

	def _find_disjoint_routes(self):
		for i in range(self.max_routes):
			if not self._bfs():
				break

		for room in self.rooms:
			room.halls.clear()
			if room.output is not None:
				room.output.halls.clear()

		pairs = []
		for route in self.routes:
			for prev, cur, nxt in prev_current_next(route):
				if cur.input is not None:
					cur = cur.input
				if nxt is not None:
					if nxt.input is not None:
						nxt = nxt.input
					cur.halls.append(nxt)
					if cur in nxt.halls:
						pairs.append((cur, nxt))

		for room1, room2 in pairs:
			print(f"Pair {room1.name} <==> {room2.name} removed")
			try:
				room1.halls.remove(room2)
			except ValueError:
				pass
			try:
				room2.halls.remove(room1)
			except ValueError:
				pass

		for room in self.start.halls:
			new_route = [room]
			while room != self.end:
				new_route.append(room.halls[0])
				room = room.halls[0]
			self.final_routes.append(new_route)
		self.print_routes(self.final_routes)

	def solve(self):
		if self.end in self.start.halls:
			for i in range(self.ants_num):
				print(f"{Colors.BOLD}L{i + 1}-{self.end.name}{Colors.ENDC}", end=' ')
			print()
			return
		print(f"{Colors.BOLD}Max routes: {self.max_routes}{Colors.ENDC}")
		self._find_disjoint_routes()

		a = set()
		for route in self.final_routes:
			for room in route:
				if room != self.end and room != self.start and room in a:
					raise RuntimeError(f"Intersection on {room.name}")
				a.add(room)

		# while self._bfs():
		# 	pass
		# for room in self.rooms:
		# 	room.halls.clear()
		# # self.print_routes()
		# print("Rounds:", self._round - 1)
		# for route in self.routes:
		# 	for cur, nxt in self.current_next(route):
		# 		if cur in nxt.halls:
		# 			nxt.halls.remove(cur)
		# 		else:
		# 			cur.halls.append(nxt)
		# for room in self.rooms:
		# 	print(f"{room.name}")
		# 	for hall in room.halls:
		# 		print(f"==> {hall.name}")
	# for route in self.final_routes:
	# 	for room in route:
	# 		room.route_link = route
	# self.final_routes.sort(key=len)
	# self.move_ants()
	# print(f"{Colors.UNDERLINE}{Colors.OKBLUE}Result: {self.steps}{Colors.ENDC}")


	# def route_fits(self, current_route):
	# 	shorter_routes_len = 0
	# 	for route in self.final_routes:
	# 		if route == current_route:
	# 			break
	# 		shorter_routes_len += (len(current_route) - len(route))
	# 	return self.start.ants_in_room > shorter_routes_len

	# def move_ants(self):
	# 	while self.end.ants_in_room < self.ants_num:
	# 		for i in range(self.ants_num):
	# 			if self.ants[i] == self.start:
	# 				for route in self.final_routes:
	# 					if route[0].ants_in_room == 0 and self.route_fits(route):
	# 						self.start.ants_in_room -= 1
	# 						self.ants[i] = route[0]
	# 						route[0].ants_in_room += 1
	# 						print(f"{Colors.BOLD}L{i + 1}-{self.ants[i].name}{Colors.ENDC}", end=' ')
	# 						break
	# 			elif self.ants[i] != self.end:
	# 				route = self.ants[i].route_link
	# 				room_id = route.index(self.ants[i])
	# 				if route[room_id] != self.end:
	# 					self.ants[i].ants_in_room -= 1
	# 					self.ants[i] = route[room_id + 1]
	# 					self.ants[i].ants_in_room += 1
	# 					print(f"{Colors.BOLD}L{i + 1}-{self.ants[i].name}{Colors.ENDC}", end=' ')
	# 		print('')
	# 		self.steps += 1
