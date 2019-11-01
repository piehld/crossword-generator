# IS590PZ - Final Assignment
# Crossword-Puzzle Generator
# Group: Dennis Piehl and Xianzhuo Cao

import numpy as np
# import matplotlib.pyplot as plt
import copy
from ast import literal_eval


def main():

	grid_dimensions = (5, 5)	# Number rows and columns in crossword puzzle grid
	black_square_density = 0.2	# [Maximum] Fraction of squares that will be black

	xw_puzzle = CrosswordPuzzle(grid_dimensions, black_square_density)
	print(xw_puzzle)
	for a in dir(xw_puzzle):
		if not a.startswith('_'):
			print(a,getattr(xw_puzzle,a))
	print('\n\n')
	print(xw_puzzle.empty_grid)

	nyt_words = read_nyt_corpus('./dict_sources/nyt-crossword-master/clues_fixed.txt', grid_dimensions)

	xw_puzzle.fill_grid(nyt_words)

	return



class CrosswordPuzzle:
	"""
	Crossword Puzzle class for representing a full (unfilled or filled) crossword puzzle grid.
	"""

	def __init__(self, dims: tuple, density: float):
		"""
		Initialize the crossword puzzle grid.

		:param dims:	Specified grid dimensions as a tuple (rows, columns).
		:param density:	Fraction of grid to set as black squares, as a float.
		:return self:	CrosswordPuzzle object.

		"""

		self.dims = dims
		self.rows = dims[0]
		self.cols = dims[1]
		self.density = density	# Should add a check to make sure the density is low enough that a "valid puzzle" is still possible (i.e., that no two-letter words are present, etc.)
		self.num_squares = dims[0]*dims[1]
		self.num_blk_sqs = round(self.num_squares * self.density) # If odd, center square must be made black; if even, no need.
		if self.num_blk_sqs % 2 != 0: # [FOR TESTING PURPOSES] If odd number of black squares, make it even so puzzle can easily be made symmetrical (wihtout having to make center square black)
			self.num_blk_sqs -= 1
		self.empty_grid = None
		self.filled_grid = None

		## Call main methods upon initialization
		self.make_empty_grid()
		# self.fill_grid()


	def make_empty_grid(self):
		"""
		Method to generate a random empty grid, with symmetrical black and white squares, and numbering.

		For testing purposes, will start with simple 5x5 grid with four corners set as black squares.
		"""

		G = np.empty(self.dims, dtype=np.string_)	# Note: MUST use 'empty' (cannot use 'ndarray' or 'array'; the former will not be mutable (for some reason???) and the latter will be 1D)
		# G[:] = ''	# Set all initialized cells to empty
		G[:] = '_'	# Set all initialized cells to '_' so that columns line up on stdout (i.e., instead of setting them to empty '')

		# NORMALLY, will want to RANDOMLY pick a non-black square and then make it black (as well as the
		# symmetric/transpose location), so long as it doesn't create a rule violation in the standard puzzle design format
		# (e.g., cannot have any completely isolated regions, nor any white spaces flanked on either side by black squares).
		for bs in range(self.num_blk_sqs):
			rand = np.random.random_integers( low=0, high=self.cols-1, size=(1,2) )
			rand_pos = (rand[0,0], rand[0,1])

		# HOWEVER, for testing purposes, we are going to just set all four corners to black squares.
		G[0][0], G[4,0], G[0,4], G[4,4] = '.', '.', '.', '.'


		self.empty_grid = copy.deepcopy(G)

		return self.empty_grid

	def is_empty_grid_valid(self):
		"""
		Check to make sure the density is low enough that a "valid puzzle" is still possible (i.e., that no two-letter words are present, etc.),
		depending on the number of black squares requested to be put into the grid.
		"""

		pass

	def fill_grid(self, words):
		"""
		Method to fill the grid.

		:param words: Word corpus (in dict. format) to use to fill grid.
		"""

		grid_build = copy.deepcopy(self.empty_grid)

		# First get list of all accross and down empty cell stretches (with length)
			# Will likely need sub method to update this list once letters start getting put in the grid, to re-run each time a new letter is inserted.



		return self.filled_grid


def read_nyt_corpus(file, dims):
	"""
	Function to read in the NYT crossword clue corpus.

	Will we be able to store this entire thing in memory?
	"""

	clue_answer_dict = {}

	# Initialize dictionary with maximum wordlength count
	# for wl in range(1, max(dims)+1):
	for wl in range(1, 25):	# max length in this corpus is 24
		clue_answer_dict.update( { wl: {} } )
	i=0
	with open(file, 'r') as f:
		for line in f:
			clue = line.split('\t')[0]
			answer = line.split('\t')[1]
			answer_len = len(answer)

			if answer_len is not None and answer_len > 0:
				if answer not in clue_answer_dict[answer_len].keys():
					# print(answer_len,answer,clue)
					clue_answer_dict[answer_len].update( { answer : [clue] } )	# Need to put clues in a list in case multiple clues exist for the same answer
				elif answer in clue_answer_dict[answer_len].keys():
					# print(answer_len, answer, clue)
					clue_answer_dict[answer_len][answer].append(clue)

	print(clue_answer_dict[3].keys())

	return clue_answer_dict



if __name__ == "__main__":
	main()
