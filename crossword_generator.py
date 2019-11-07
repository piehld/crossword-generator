# IS590PZ - Final Assignment
# Crossword-Puzzle Generator
# Group: Dennis Piehl and Xianzhuo Cao

import numpy as np
# import matplotlib.pyplot as plt
import copy
from ast import literal_eval
from random import choice

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

	# nyt_words = read_nyt_corpus('./dict_sources/nyt-crossword-master/clues_fixed.txt', grid_dimensions)
	nyt_words = {3:{'aaa':'test'}, 4:{'aaaa':'test'}, 5:{'aaaaa':'test'}}

	xw_puzzle.fill_grid(nyt_words)

	return



class CrosswordPuzzle:
	"""
	Crossword Puzzle class for representing a full (unfilled or filled) crossword puzzle grid.

	Currently must be Odd x Odd length

	Rules followed:
		- All words must be >= 3 characters
		- All white spaces should be connected (no enclosed/blocked-off regions)
			* Using union-find algorithm to check this
		- All white squares must be part of BOTH an Across and Down crossing
			* There must be at least 1 white square to the left or right, AND at least 1 white sqauare to the top or bottom
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
		self.ifcenter_black = False # Patrick: I add a new parameter to determine if the center is black
		self.density = density	# Should add a check to make sure the density is low enough that a "valid puzzle" is still possible (i.e., that no two-letter words are present, etc.)
		self.num_squares = dims[0]*dims[1]
		self.num_blk_sqs = round(self.num_squares * self.density) # If odd, center square must be made black; if even, no need.
		if self.num_blk_sqs % 2 != 0: # [FOR TESTING PURPOSES] If odd number of black squares, make it even so puzzle can easily be made symmetrical (wihtout having to make center square black)
			self.num_blk_sqs -= 1
			self.ifcenter_black = True

		self.blk_sqs_positions = None
		self.empty_grid = None
		self.filled_grid = None

		## Call main methods upon initialization

		self.make_empty_grid()
		# self.empty_grid = self.determine_black_square(self.empty_grid)

		# self.fill_grid()

	def determine_black_square(self,G):
		center = int(self.rows/2)
		if self.ifcenter_black == True:
			G[center][center] = '.'

		rand_nums,rand_pool = int(self.num_blk_sqs / 2), [i for i in range(0,int((self.num_squares - 1) / 2))]
		self.blk_sqs_positions = []
		while(rand_nums > 0):
			rand_nums -= 1
			temp = choice(rand_pool)
			rand_pool.remove(temp)
			self.blk_sqs_positions.append((int(temp/self.cols),temp % self.rows))
			G[int(temp/self.cols)][temp % self.rows] = '.'
			self.blk_sqs_positions.append((center * 2 - int(temp/self.cols),center * 2 - temp % self.rows))  # make the board symmetric
			G[center * 2 - int(temp/self.cols)][center * 2 - (temp % self.rows)] = '.'

		return G








	def make_empty_grid(self):
		"""
		Method to generate a random empty grid, with symmetrical black and white squares, and numbering.

		For testing purposes, will start with simple 5x5 grid with four corners set as black squares.
		"""

		# G = np.empty(self.dims, dtype=np.string_)	# Note: MUST use 'empty' (cannot use 'ndarray' or 'array'; the former will not be mutable (for some reason???) and the latter will be 1D)
		G = np.empty(self.dims, dtype=str)	# Note: MUST use 'empty' (cannot use 'ndarray' or 'array'; the former will not be mutable (for some reason???) and the latter will be 1D); Also, if you use "np.string_" this actually makes it an array of "bytes"...?!

		# G[:] = ''	# Set all initialized cells to empty
		G[:] = '_'	# Set all initialized cells to '_' so that columns line up on stdout (i.e., instead of setting them to empty '')

		# NORMALLY, will want to RANDOMLY pick a non-black square and then make it black (as well as the
		# symmetric/transpose location), so long as it doesn't create a rule violation in the standard puzzle design format
		# (e.g., cannot have any completely isolated regions, nor any white spaces flanked on either side by black squares).
		for bs in range(self.num_blk_sqs):
			rand = np.random.random_integers( low=0, high=self.cols-1, size=(1,2) )
			rand_pos = (rand[0,0], rand[0,1])

		# HOWEVER, for testing purposes, we are going to just set all four corners to black squares.
		G[0,0], G[4,0], G[0,4], G[4,4] = '.', '.', '.', '.'

		self.blk_sqs_positions = [(0,0), (4,0), (0,4), (4,4)]

		self.empty_grid = copy.deepcopy(G)

		return self.empty_grid, self.blk_sqs_positions

	def is_empty_grid_valid(self):
		"""
		Check to make sure the density is low enough that a "valid puzzle" is still possible (i.e., that no two-letter words are present, etc.),
		depending on the number of black squares requested to be put into the grid.
		"""

		pass

	def fill_grid(self, words):
		"""
		Method to fill the grid.

		When assigning words to white-square stretches, can use: np[0][0:4] = "LAIR" (or similar, where 4 is the 'end' of the word)

		Fill LONGER words first, then crossings to the longer words
		ALSO Choose most common words first (or rank them all)

		:param words: Word corpus (in dict. format) to use to fill grid.
		"""

		print("Here")

		G = copy.deepcopy(self.empty_grid)
		print(G)

		# First get list of all across and down empty cell stretches (with length)
			# Will likely need sub method to update this list once letters start getting put in the grid, to re-run each time a new letter is inserted.
		across, down = {}, {}
		checked_down_squares = []

		# Gather down words FIRST (since that's how numbering is ordered)
		clue_enum = 0
		for r in range(self.rows):
			on_blank_across_squares = False
			for c in range(self.cols):
				on_blank_down_squares = False
				if (r,c) not in self.blk_sqs_positions:

					# Swap Column block up here? For ordering of numbers?
					if on_blank_across_squares == True:
						if c == self.cols-1:	# if at end of row
							across[curr_across_num].update( {"end":(r,c)} )

					elif on_blank_across_squares == False:
						on_blank_across_squares = True
						clue_enum += 1
						across.update( {clue_enum: {"start":(r,c)}} )
						curr_across_num = clue_enum

					if on_blank_down_squares == False and (r,c) not in checked_down_squares:
						# Now proceed through the column dimension first

						# If down word doesn't start at same square as across word, increment the clue number
						if (r,c) != across[curr_across_num]["start"]:
							clue_enum += 1

						down.update( {clue_enum: {"start":(r,c)}} )
						on_blank_down_squares = True
						checked_down_squares.append((r,c))
						r2 = r
						while on_blank_down_squares:
							r2+=1
							if (r2,c) in self.blk_sqs_positions:
								down[clue_enum].update( {"end":(r2-1,c)} )
								on_blank_down_squares = False

							elif (r2,c) not in self.blk_sqs_positions:
								checked_down_squares.append((r2,c))
								if r2 == self.rows-1:	# if at end of column
									down[clue_enum].update( {"end":(r2,c)} )
									on_blank_down_squares = False
								else:
									continue

				elif (r,c) in self.blk_sqs_positions:
					if on_blank_across_squares == True:	# Then end the word
						across[curr_across_num].update( {"end":(r,c-1)} )
						on_blank_across_squares = False
					elif on_blank_across_squares == False:
						continue


		print("Across",across)
		print("Down",down)
		# print(G)
		# exit()

		# Get the spans of cells between each of them, row and column wise...and then append to the corresponding dicts

			# word_join = np.str.join('',G2[0][0:5])	# command to join cells from 0,0 to 0,5; will be useful later...maybe.

		def is_word(letters_of_word): # Return bool
			"""
			"""
			pass

		def is_there_a_possible_word(starting_or_partial_letters_of_word): # Return bool
			"""
			"""
			pass

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

	w = choice(list(clue_answer_dict[3].keys()))
	clue = clue_answer_dict[3][w][0]

	print(w, clue)

	for k in clue_answer_dict[4].keys():
		if len(clue_answer_dict[4][k]) > 20:
			print(k, clue_answer_dict[4][k])

	return clue_answer_dict



if __name__ == "__main__":
	main()
