from contextlib import contextmanager


class Room:
	def __init__(self, name, x, y):
		self.name = name
		self.x = int(x)
		self.y = int(y)
		self.ants_in_room = 0
		self.halls = []
		self.added_by = None
		self.route = None
		self.input = None
		self.output = None
		self.mark = None


class Colors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


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


def insert_insort(sequence, x, key=None):
	lo = 0
	hi = len(sequence)
	while lo < hi:
		mid = (lo + hi) // 2
		if key is not None:
			compare = key(x) < key(sequence[mid])
		else:
			compare = x < sequence[mid]
		if compare:
			hi = mid
		else:
			lo = mid + 1
	sequence.insert(lo, x)


@contextmanager
def ignored(*exceptions):
	try:
		yield
	except exceptions:
		pass
