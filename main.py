import sys
from Parser import Parser
from Solver import Solver


def main():
	try:
		if len(sys.argv) != 2:
			raise Exception("Usage: python lem_in map")
		parser = Parser(sys.argv[1])
		parser.parse_file()
		solver = Solver(parser)
		solver.solve()
	except Exception as e:
		print(str(e))


if __name__ == "__main__":
	main()
