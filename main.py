import sys
from Parser import Parser
from Solver import Solver


def main():
	try:
		if len(sys.argv) != 2:
			raise KeyError("Usage: python lem_in map")
		parser = Parser(sys.argv[1], verbose=True)
		parser.parse_file()
		solver = Solver(parser)
		solver.solve()
	except (SyntaxError, AssertionError, RuntimeError) as e:
		red_color = "\033[0;31m"
		no_color = "\033[0m"
		print(f"{red_color}{e}{no_color}")


if __name__ == "__main__":
	main()
