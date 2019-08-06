import copy

class bcolors:
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
		self.rooms = src.rooms
		self.ants_num = src.ants_num
		self.start = src.start
		self.end = src.end
		self.final_routes = []
		self.routes = []
		self.round = 0
		self.best_score = None

	def bfs(self):
		self.round += 1
		visited = set()
		queue = [self.start]
		visited.add(self.start)
		while queue:
			room = queue.pop(0)
			if room == self.end:
				return self.save_route()
			for hall in room.halls:
				if hall not in visited:
					hall.added_by = room
					visited.add(hall)
					queue.append(hall)
		return False

	def save_route(self):
		self.routes = self.final_routes
		tmp = self.end
		new_route = list()
		while tmp.added_by and tmp != self.start:
			new_route.append(tmp)
			tmp.added_by.halls.remove(tmp)
			if tmp != self.end:
				tmp.route_id = self.round
			tmp = tmp.added_by
		new_route.reverse()
		new_route = self.swap_routes(new_route)
		new_route = self.clean_route(new_route)
		self.routes.append(new_route)
		score = self.count_steps()
		if not self.best_score or score < self.best_score:
			self.best_score = score
			self.final_routes = self.routes
			return True
		return False

	def swap_routes(self, new_route):
		i = 0
		while i < self.round - 1:
			j = 0
			while j < len(self.routes[i]):
				room = self.routes[i][j]
				if room in new_route:
					new_route_pos = new_route.index(room)
					old_route_pos = self.routes[i].index(room)
					old_route_sliced = self.routes[i][old_route_pos:]
					new_route_sliced = new_route[new_route_pos:]
					new_route = new_route[:new_route_pos]
					new_route.extend(old_route_sliced)
					self.routes[i] = self.routes[i][:old_route_pos]
					self.routes[i].extend(new_route_sliced)
				j += 1
			i += 1
		return new_route

	def clean_route(self, route):
		visited = []
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
				visited = []
			visited.append(route[i])
			i += 1
		return route

	def count_steps(self):
		if not len(self.routes):
			return 2147483647
		steps = 0
		ants_moved = 0
		while ants_moved < self.ants_num:
			steps += 1
			for j in range(self.round):
				if len(self.routes[j]) <= steps:
					ants_moved += 1
		return steps

	def print_routes(self):
		print(f"Round {self.round}:")
		for route in self.routes:
			for room in route:
				print(f"{bcolors.OKBLUE}{room.name}{bcolors.ENDC}", end='')
				if room != self.end:
					print(' --> ', end='')
			print('')
		print(f"{bcolors.OKGREEN}Efficiency: {self.count_steps()}{bcolors.ENDC}")

	def solve(self):
		while self.bfs():
			self.print_routes()

# Find the shortest route using bfs
# Delete links inside this route from end to start
# Find the 2 shortest route
# Take directions back
# Remove all inverse edges along with their originals
