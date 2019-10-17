import sys
import timeit
from Parser import Parser
from Solver import Solver


def run():
	verbose = len(sys.argv) > 2 and sys.argv[2] == '--verbose'
	parser = Parser(sys.argv[1], verbose=verbose)
	parser.parse_file()
	solver = Solver(parser)
	solver.solve()


def main():
	try:
		if len(sys.argv) < 2:
			raise KeyError("Usage: python lem_in map")
		print("Execution time:", timeit.timeit(run, number=1))
	except (SyntaxError, AssertionError, RuntimeError, FileNotFoundError) as e:
		red_color = "\033[0;31m"
		no_color = "\033[0m"
		print(f"{red_color}{e}{no_color}")


if __name__ == "__main__":
	main()
