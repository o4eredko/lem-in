import collections
import copy

from utils import Colors, prev_current_next, insert_insort, ignored


class Solver:
	def __init__(self, src):
		self.ants = None
		self._steps = 0
		self._tmp_routes = None
		self._routes = []
		self.final_routes = []
		self.best_score = float('inf')

		self.ants_num = src.ants_num
		self.rooms = src.rooms
		self.start = src.start
		self.end = src.end
		self.verbose = src.verbose
		self.validate = src.validate
		self.required_lines = src.required_lines
		self._max_routes = min(self.ants_num, len(self.start.halls), len(self.end.halls))

	def _print_routes(self, routes):
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
		visited = set()
		for route in self.final_routes:
			for room in route:
				if room != self.end and room != self.start and room.name in visited:
					raise RuntimeError(f"Intersection on room {room.name}")
				visited.add(room.name)
		else:
			print(f"{Colors.HEADER}No intersection of paths was found!{Colors.ENDC}")

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
			duplicate.input = cur
			cur.output = duplicate

			duplicate.halls = cur.halls[:]
			cur.halls = [prev] if prev in cur.halls else []
			duplicate.halls.append(cur)
			with ignored(ValueError):
				duplicate.halls.remove(prev)
			with ignored(ValueError):
				nxt.halls[nxt.halls.index(cur)] = duplicate

	def _save_route(self):
		"""
		Save new route and remove all links from start to end through that route.
		Then duplicates all intermediate nodes to get input node and output node for each node.
		It is a modification of Bhandari algorithm, because Bhandari allows different paths to
		go through one node, until they don't use the same edges.
		But my ants cannot occupy the same room and wait, so paths
		should be node-disjoint
		"""
		new_route = []
		tmp = self.end
		while tmp.added_by and tmp != self.start:
			new_route.append(tmp)
			with ignored(ValueError):
				tmp.added_by.halls.remove(tmp)
			tmp = tmp.added_by
		new_route.append(self.start)
		new_route.reverse()
		self._routes.append(new_route)
		self._duplicate_nodes(new_route)

	def _bfs(self):
		"""
		Breadth-First Search. Finds the shortest path and saves it to self.routes
		:return: True if new route was found, otherwise False
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
		for route in self._routes:
			for prev, cur, nxt in prev_current_next(route):
				if cur.input is not None:
					cur = cur.input
				if nxt is not None:
					if nxt.input is not None:
						nxt = nxt.input
					cur.halls.append(nxt)
					if cur in nxt.halls:
						with ignored(ValueError):
							cur.halls.remove(nxt)
						with ignored(ValueError):
							nxt.halls.remove(cur)

	def _form_routes(self):
		self._routes = []
		for room in self.start.halls:
			new_route = [room]
			while room != self.end:
				new_route.append(room.halls[0])
				room = room.halls[0]
			insert_insort(self._routes, new_route, key=len)

	def _update_final_routes(self, route_num, score):
		if self.verbose:
			print(f"{Colors.HEADER}Round {route_num}:{Colors.ENDC}")
			self._print_routes(self._routes)
		self.best_score = score
		for route in self._routes:
			for room in route:
				room.route_link = route
		self.final_routes = self._routes

	def _find_disjoint_routes(self):
		tmp_room_links = None
		for route_num in range(1, self._max_routes + 1):
			if route_num > 1:
				for room, restored_links in zip(self.rooms, tmp_room_links):
					room.halls = restored_links
				self._routes = self._tmp_routes
			if not self._bfs():
				break
			tmp_room_links = [room.halls[:] for room in self.rooms]
			self._tmp_routes = self._routes
			for room in self.rooms:
				room.halls.clear()
			self._put_routes_on_graph()
			self._form_routes()
			score = self._count_steps(self._routes)
			if score > self.best_score:
				continue
			self._update_final_routes(route_num, score)

	def _get_available_route(self):
		for i, route in enumerate(self.final_routes):
			first_room = route[0]
			if not first_room.ants_in_room:
				shorter_routes_len = sum(
					len(route) - len(shorter_route) for shorter_route in self.final_routes[:i])
				break
		else:
			return None
		return route if self.start.ants_in_room > shorter_routes_len else None

	def _move_ants(self):
		print(f"{Colors.BOLD}Final output:{Colors.ENDC} (format: L(ant_num)-(move to)(room_name))")
		self.ants = [self.start for _ in range(self.ants_num)]
		while self.end.ants_in_room < self.ants_num:
			for i, ant in enumerate(self.ants):
				if ant == self.start:
					route = self._get_available_route()
					if route is None:
						continue
					next_room = route[0]
				elif ant != self.end:
					route = ant.route_link
					next_room = route[route.index(ant) + 1]
				else:
					continue
				ant.ants_in_room -= 1
				self.ants[i] = next_room
				next_room.ants_in_room += 1
				room_color = next_room.mark or Colors.BOLD
				print(f"{room_color}L{i + 1}-{next_room.name}{Colors.ENDC}", end=' ')
			print()
			self._steps += 1

	def solve(self):
		"""
		Function uses modified Suurballe algorithm.
		That algorithm finds k node-disjoint paths.
		I try to find 1 shortest path and then increase k to find more paths.
		On each iteration i compare results and if it become better, i go to the next iteration,
		otherwise, algorithm stops.
		"""
		if self.end in self.start.halls:
			print(f"{Colors.BOLD}Final output:{Colors.ENDC} (format: L(ant_num)-(room_name))")
			for i in range(self.ants_num):
				print(f"{Colors.BOLD}L{i + 1}-{self.end.name}{Colors.ENDC}", end=' ')
			print()
			return
		if self.verbose:
			print(f"{Colors.BOLD}Max routes: {self._max_routes}{Colors.ENDC}")

		self._find_disjoint_routes()
		assert len(self.final_routes), "No possible solution"
		self._move_ants()
		if self.validate:
			self._check_intersection()

		if self.required_lines is None:
			print(f"{Colors.OKBLUE}Result: {self._steps}{Colors.ENDC}")
		elif self._steps <= self.required_lines:
			print(f"{Colors.OKBLUE}Result: {self._steps} <= {self.required_lines}{Colors.ENDC}")
		else:
			print(f"{Colors.FAIL}Result: {self._steps} > {self.required_lines}{Colors.ENDC}")
