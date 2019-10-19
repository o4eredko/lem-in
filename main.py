import sys
import timeit
from Parser import Parser
from Solver import Solver
from utils import Colors


def main():
	if len(sys.argv) < 2:
		raise KeyError("Usage: python lem_in map")
	try:
		start_time = timeit.default_timer()
		parser = Parser(sys.argv[1])
		parser.parse_file()
		solver = Solver(parser)
		solver.solve()
		time = timeit.default_timer() - start_time
		print(f"{Colors.BOLD}Time: {Colors.ENDC}{round(time, 4)}s for {len(solver.rooms)} rooms")
	except (SyntaxError, AssertionError, RuntimeError, FileNotFoundError) as e:
		red_color = "\033[0;31m"
		no_color = "\033[0m"
		print(f"{red_color}{e}{no_color}")


if __name__ == "__main__":
	main()
