import sys
from Parser import Parser
from Solver import Solver
import timeit


def main():
	try:
		if len(sys.argv) != 2:
			raise KeyError("Usage: python lem_in map")
		parser = Parser(sys.argv[1], verbose=True)
		print(timeit.timeit(parser.parse_file, number=1))
		# solver = Solver(parser)
		# solver.solve()
	except (SyntaxError, AssertionError) as e:
		red_color = "\033[0;31m"
		no_color = "\033[0m"
		print(f"{red_color}{e}{no_color}")


if __name__ == "__main__":
	main()
