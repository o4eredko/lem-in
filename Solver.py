import collections


class Colors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


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
				return self._save_route()
			for hall in room.halls:
				if hall not in visited:
					hall.added_by = room
					visited.add(hall)
					queue.append(hall)
		return False

	def _save_route(self):
		# self.routes = self.final_routes.copy()
		new_route = []
		tmp = self.end
		while tmp.added_by and tmp != self.start:
			new_route.append(tmp)
			tmp.added_by.halls.remove(tmp)
			tmp = tmp.added_by
		new_route.append(self.start)
		new_route.reverse()
		self.routes.append(new_route)
		return True

	# new_route = self._swap_routes(new_route)
	# new_route = self._clean_route(new_route)
	# for k in range(len(new_route)):
	# 	if new_route[k] != self.end:
	# 		new_route[k].route_link = new_route
	# self.routes.append(new_route)
	# score = self.count_steps()
	# if self.best_score is None or score < self.best_score:
	# 	self.best_score = score
	# 	self.final_routes = self.routes
	# 	return True
	# return False

	def _swap_routes(self, new_route):
		for i in range(len(self.routes)):
			for j in range(len(self.routes[i])):
				room = self.routes[i][j]
				if room in new_route:
					new_route_pos = new_route.index(room)
					old_route_pos = self.routes[i].index(room)
					old_route_sliced = self.routes[i][old_route_pos:]
					new_route_sliced = new_route[new_route_pos:]
					for k in range(len(new_route_sliced)):
						if new_route_sliced[k] != self.end:
							new_route_sliced[k].route_link = self.routes[i]
					new_route = new_route[:new_route_pos]
					new_route.extend(old_route_sliced)
					self.routes[i] = self.routes[i][:old_route_pos]
					self.routes[i].extend(new_route_sliced)
					# self._clean_route(self.routes[i])
					break
		return new_route

	@staticmethod
	def _clean_route(route):
		visited = set()
		i = 0
		while i < len(route):
			current_room = route[i]
			if current_room in visited:
				route.pop(i)
				i -= 1
				while i > 0 and route[i] != current_room:
					route.pop(i)
					i -= 1
				i = 0
				visited = set()
			visited.add(route[i])
			i += 1
		return route

	def count_steps(self):
		if not len(self.routes):
			return 2147483647
		steps = 0
		ants_moved = 0
		while ants_moved < self.ants_num:
			steps += 1
			for route in self.routes:
				if len(route) <= steps:
					ants_moved += 1
		return steps

	def move_ants(self):
		while self.end.ants_in_room < self.ants_num:
			for i in range(self.ants_num):
				if self.ants[i] == self.start:
					for route in self.final_routes:
						if route[0].ants_in_room == 0 and self.route_fits(route):
							self.start.ants_in_room -= 1
							self.ants[i] = route[0]
							route[0].ants_in_room += 1
							print(f"{Colors.BOLD}L{i + 1}-{self.ants[i].name}{Colors.ENDC}", end=' ')
							break
				elif self.ants[i] != self.end:
					route = self.ants[i].route_link
					room_id = route.index(self.ants[i])
					if route[room_id] != self.end:
						self.ants[i].ants_in_room -= 1
						self.ants[i] = route[room_id + 1]
						self.ants[i].ants_in_room += 1
						print(f"{Colors.BOLD}L{i + 1}-{self.ants[i].name}{Colors.ENDC}", end=' ')
			print('')
			self.steps += 1

	def print_routes(self):
		print(f"Round {self._round}:")
		for route in self.routes:
			for room in route:
				print(f"{Colors.OKBLUE}{room.name}{Colors.ENDC}", end='')
				if room != self.end:
					print(' --> ', end='')
			print('')
		print(f"{Colors.OKGREEN}Efficiency: {self.count_steps()}{Colors.ENDC}")

	def route_fits(self, current_route):
		shorter_routes_len = 0
		for route in self.final_routes:
			if route == current_route:
				break
			shorter_routes_len += (len(current_route) - len(route))
		return self.start.ants_in_room > shorter_routes_len

	def current_next(self, iterable):
		"""Make an iterator that yields an (previous, current, next) tuple per element.

		Returns None if the value does not make sense (i.e. previous before
		first and next after last).
		"""
		iterable = iter(iterable)
		cur = next(iterable)
		try:
			while True:
				nxt = next(iterable)
				yield (cur, nxt)
				cur = nxt
		except StopIteration:
			pass

	def solve(self):
		if self.end in self.start.halls:
			for i in range(self.ants_num):
				print(f"{Colors.BOLD}L{i + 1}-{self.end.name}{Colors.ENDC}", end=' ')
			print()
			return

		while self._bfs():
			pass
		for room in self.rooms:
			room.halls.clear()
		# self.print_routes()
		print("Rounds:", self._round - 1)
		for route in self.routes:
			for cur, nxt in self.current_next(route):
				if cur in nxt.halls:
					nxt.halls.remove(cur)
				else:
					cur.halls.append(nxt)
		for room in self.rooms:
			print(f"{room.name}")
			for hall in room.halls:
				print(f"==> {hall.name}")
	# for route in self.final_routes:
	# 	for room in route:
	# 		room.route_link = route
	# self.final_routes.sort(key=len)
	# self.move_ants()
	# print(f"{Colors.UNDERLINE}{Colors.OKBLUE}Result: {self.steps}{Colors.ENDC}")
