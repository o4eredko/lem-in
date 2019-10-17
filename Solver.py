import collections
import copy
from utils import Colors, prev_current_next, insert_insort


class Solver:
	def __init__(self, src):
		self.steps = 0
		self.ants_num = src.ants_num
		self.rooms = src.rooms
		self.start = src.start
		self.end = src.end
		self.routes = []
		self.verbose = src.verbose
		self.final_routes = []
		self.best_score = float('inf')
		self.ants = [self.start] * self.ants_num
		self.max_routes = min(self.ants_num, len(self.start.halls), len(self.end.halls))
		self.required_lines = src.required_lines

	def _print_routes(self, routes):
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

	def _check_intersection(self):
		a = set()
		for route in self.final_routes:
			for room in route:
				room.route_link = route
				if room != self.end and room != self.start and room.name in a:
					raise RuntimeError(f"Intersection on {room.name}")
				a.add(room.name)

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

	def _duplicate_nodes(self, route):
		for prev, cur, nxt in prev_current_next(route):
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
			duplicate.halls.append(cur)
			try:
				duplicate.halls.remove(prev)
			except ValueError:
				pass

			try:
				nxt.halls[nxt.halls.index(cur)] = duplicate
			except ValueError:
				pass

	def _save_route(self):
		"""
		Save new route and remove all links from start to end through that route.
		Then duplicates all intermediate nodes to get input node and output node for each node.
		It is a modification of Bhandari algorithm, because Bhandari allows different paths go through
		one node, until they don't use the same edges.
		But my ants cannot occupy the same room and wait, so paths
		should be node-disjoint
		"""
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
		self._duplicate_nodes(new_route)

	def _bfs(self):
		"""
		Breadth-First Search. Finds the shortest path and saves it to self.routes
		:return: bool, True if new route was found, otherwise False
		"""
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

	def _put_routes_on_graph(self):
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
		self.routes.clear()
		for room1, room2 in pairs:
			if self.verbose:
				print(f"Pair {room1.name} <==> {room2.name} removed")
			try:
				room1.halls.remove(room2)
			except ValueError:
				pass
			try:
				room2.halls.remove(room1)
			except ValueError:
				pass

	def _del_all_edges(self):
		for room in self.rooms:
			room.halls.clear()
			if room.output is not None:
				room.output.halls.clear()

	def _form_routes(self):
		for room in self.start.halls:
			new_route = [room]
			while room != self.end:
				room.route_link = new_route
				new_route.append(room.halls[0])
				room = room.halls[0]
			insert_insort(self.routes, new_route, key=len)

	def _find_disjoint_routes(self):
		for route_num in range(1, self.max_routes + 1):
			original_halls = [room.halls[:] for room in self.rooms]
			self.routes = []
			for i in range(route_num):
				if not self._bfs():
					return
			self._del_all_edges()
			self._put_routes_on_graph()
			self._form_routes()
			for i, room in enumerate(self.rooms):
				room.halls = original_halls[i]
				room.input = room.output = None

			score = self._count_steps(self.routes)
			if score > self.best_score:
				return
			if self.verbose:
				print(f"{Colors.HEADER}Round: {route_num}{Colors.ENDC}")
				self._print_routes(self.routes)
			self.best_score = score
			self.final_routes = self.routes

	def _route_fits(self, current_route):
		shorter_routes_len = 0
		for route in self.final_routes:
			if route == current_route:
				break
			shorter_routes_len += (len(current_route) - len(route))
		return self.start.ants_in_room > shorter_routes_len

	def _move_ants(self):
		print(f"{Colors.BOLD}Final output:{Colors.ENDC} (format: L(ant_num)-(move to)(room_name))")
		while self.end.ants_in_room < self.ants_num:
			for i in range(self.ants_num):
				if self.ants[i] == self.start:
					for route in self.final_routes:
						if route[0].ants_in_room == 0 and self._route_fits(route):
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

	def solve(self):
		"""
		Function uses modified Suurballe algorithm.
		That algorithm finds k node-disjoint paths.
		I try to find 1 shortest path and then increase k to find more paths.
		On each iteration i compare results and if it become better, i go to the next iteration,
		otherwise, algorithm stops.
		"""
		if self.end in self.start.halls:
			print(f"{Colors.BOLD}Final output:{Colors.ENDC} (format: L(ant_num)-(move to)(room_name))")
			for i in range(self.ants_num):
				print(f"{Colors.BOLD}L{i + 1}-{self.end.name}{Colors.ENDC}", end=' ')
			print()
			return
		if self.verbose:
			print(f"{Colors.BOLD}Max routes: {self.max_routes}{Colors.ENDC}")
		self._find_disjoint_routes()
		assert len(self.final_routes), "No possible path"
		self._check_intersection()
		self._move_ants()
		if self.required_lines is None:
			print(f"{Colors.BOLD}{Colors.OKBLUE}Result: {self.steps}{Colors.ENDC}")
		elif self.steps <= self.required_lines:
			print(f"{Colors.BOLD}{Colors.OKBLUE}Result: {self.steps} <= {self.required_lines}{Colors.ENDC}")
		else:
			print(f"{Colors.BOLD}{Colors.FAIL}Result: {self.steps} > {self.required_lines}{Colors.ENDC}")
