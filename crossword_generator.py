# IS590PZ - Final Assignment
# Crossword-Puzzle Generator
# Group: Dennis Piehl and Xianzhuo Cao

import numpy as np
# import matplotlib.pyplot as plt
import copy
from ast import literal_eval
from random import choice
from time import sleep
import re

def main():

	grid_dimensions = (5, 5)	# Number rows and columns in crossword puzzle grid
	black_square_density = 0.2	# [Maximum] Fraction of squares that will be black

	xw_puzzle = CrosswordPuzzle(grid_dimensions, black_square_density)
	# print(xw_puzzle)
	# for a in dir(xw_puzzle):
	# 	if not a.startswith('_'):
	# 		print(a,getattr(xw_puzzle,a))
	# print('\n\n')
	print(xw_puzzle.empty_grid)

	nyt_words = read_nyt_corpus('./dict_sources/nyt-crossword-master/clues_fixed.txt', grid_dimensions)
	# nyt_words = {3:{'aaa':['test'],'bbb':['test']}, 4:{'aaaa':['test'],'bbbb':['test']}, 5:{'aaaaa':['test'],'bbbbb':['test']}}

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

		self.across, self.down, self.word_len_dict = self.gather_across_and_down_word_spaces()

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


	def gather_across_and_down_word_spaces(self):
		"""
		Method to gather the collection of blank across & down spaces, into which the words will be filled.

		# First get list of all across and down empty cell stretches (with length)
			# Will likely need sub method to update this list once letters start getting put in the grid, to re-run each time a new letter is inserted.

		"""

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

		# Get length of each word, and append to both the word dict itself as well as a growing dict of word lengths to inform the fill order
		word_len_dict = {"across":{}, "down":{}}
		for k in across.keys():
			wlength = across[k]["end"][1] - ( across[k]["start"][1] - 1 )
			across[k]["len"] = wlength
			if wlength not in word_len_dict["across"].keys():
				word_len_dict["across"].update({wlength:[k]})
			elif wlength in word_len_dict["across"].keys():
				word_len_dict["across"][wlength].append(k)

		for k in down.keys():
			wlength = down[k]["end"][0] - ( down[k]["start"][0] - 1 )
			down[k]["len"] = wlength
			if wlength not in word_len_dict["down"].keys():
				word_len_dict["down"].update({wlength:[k]})
			elif wlength in word_len_dict["down"].keys():
				word_len_dict["down"][wlength].append(k)

		print("Across",across)
		print("Down",down)
		print("Word length dict",word_len_dict)

		return across, down, word_len_dict


	def refresh_word_len_dict(self, wd_len, wd_num_filled, direction):
		"""
		"""

		print(self.word_len_dict[direction])

		idx = self.word_len_dict[direction][wd_len].index(wd_num_filled)
		self.word_len_dict[direction][wd_len].pop(idx)
		# print(self.word_len_dict[direction])

		# Now check if the list of availble words to fill is empty for the given length
		if len(self.word_len_dict[direction][wd_len]) == 0:
			self.word_len_dict[direction].pop(wd_len)

		print(self.word_len_dict[direction])

		return


	def fill_grid(self, words):
		"""
		Method to fill the grid.

		When assigning words to white-square stretches, can use: np[0][0:4] = "LAIR" (or similar, where 4 is the 'end' of the word)

		Fill LONGER words first, then crossings to the longer words
		ALSO Choose most common words first (or rank them all)

		# word_join = np.str.join('',G2[0][0:5])	# command to join cells from 0,0 to 0,5; will be useful later...maybe.


		:param words: Word corpus (in dict. format) to use to fill grid.
		"""


		def is_word(letters_of_word): # Return bool
			"""
			"""
			pass

		def is_there_a_possible_word(starting_or_partial_letters_of_word): # Return bool
			"""
			"""
			pass

		def is_puzzle_fill_complete(xw_grid):
			"""
			"""
			pass



		print("Here")
		G = copy.deepcopy(self.empty_grid)
		print(G)

		# First, choose the longest across word length to fill
		across_flag = True
		# for word in range(len(self.across) + len(self.down)):
		while '_' in G:
			if across_flag:
				max_len_across = max(self.word_len_dict['across'].keys())
				word_to_fill = choice(self.word_len_dict['across'][max_len_across])
				print("Across word to fill", word_to_fill, self.across[word_to_fill])

				# use for across only
				row = self.across[word_to_fill]['start'][0]
				c1 = self.across[word_to_fill]['start'][1]
				c2 = self.across[word_to_fill]['end'][1] + 1
				# print(G[row][c1:c2])

				curr_word = np.str.join('',G[row][c1:c2])
				print(curr_word)
				curr_word_re = curr_word.replace('_','.')
				print(curr_word_re)
				# exit()
				curr_letters_and_idxs = [(ix,l) for (ix,l) in enumerate(curr_word) if l != '_']
				print(curr_letters_and_idxs)

				# Regex compile idea from: https://stackoverflow.com/questions/38460918/regex-matching-a-dictionary-efficiently-in-python
					# dicti={'the':20, 'a':10, 'over':2}
					# regex_list=['the', 'an?']
					# extractddicti= {k:v for k,v in dicti.items() if any (re.match("^"+regex+"$",k) for regex in regex_list)}
					# NOW, COMPILED:
					# regex_list_compiled=[re.compile("^"+i+"$") for i in regex_list]
					# extractddicti= {k:v for k,v in dicti.items() if any (re.match(regex,k) for regex in regex_list_compiled)} 

					# OR even "better":
						# patterns=['the', 'an?']
						# regex_matches = [re.compile("^"+pattern+"$").match for pattern in patterns]
						# extractddicti= {k:v for k,v in dicti.items() if any (regex_match(k) for regex_match in regex_matches)}

				w_choices = {k:v for k,v in words[max_len_across].items() if re.match(curr_word_re, k)}
				print(w_choices.keys())
				w = choice(list(w_choices.keys()))



				# w = choice(list(words[max_len_across].keys()))
				# sorted_words_by_freq = sorted(words[max_len_across].items(), key = lambda item: len(item[1]),reverse = True )
				# w = choice(sorted_words_by_freq[0:100])[0]

				# sleep(3)

				# Check if chosen word agres with current string of letters of current word [***STUPID SIMPLE WAY OF CHECKING AND FILLING PUZZLE*** -- WILL IMPROVE LATER]
				if not all([ w[ix] == l for (ix,l) in curr_letters_and_idxs ]):
					print("There's a mis-match!")
					print(G)
					continue

				clue = choice(words[max_len_across][w])
				print(w, clue)

				# G[row][c1:c2] = w
				for idx,letter in enumerate(w):
					G[row][c1+idx] = letter

				across_flag = False

				self.refresh_word_len_dict(max_len_across, word_to_fill, 'across')

				print(G)


			elif not across_flag:
				max_len_down = max(self.word_len_dict['down'].keys())
				word_to_fill = choice(self.word_len_dict['down'][max_len_down])
				print("Down word to fill", word_to_fill, self.down[word_to_fill])

				# use for down only
				col = self.down[word_to_fill]['start'][1]
				r1 = self.down[word_to_fill]['start'][0]
				r2 = self.down[word_to_fill]['end'][0] + 1
				# print(G[r1:r2,col])

				curr_word = np.str.join('',G[r1:r2,col])
				print(curr_word)
				curr_word_re = curr_word.replace('_','.')
				print(curr_word_re)
				curr_letters_and_idxs = [(ix,l) for (ix,l) in enumerate(curr_word) if l != '_']
				print(curr_letters_and_idxs)

				# Regex compile idea from: https://stackoverflow.com/questions/38460918/regex-matching-a-dictionary-efficiently-in-python
				# dicti={'the':20, 'a':10, 'over':2}
				# regex_list=['the', 'an?']
				# extractddicti= {k:v for k,v in dicti.items() if any (re.match("^"+regex+"$",k) for regex in regex_list)}

				w_choices = {k:v for k,v in words[max_len_down].items() if re.match(curr_word_re, k)}
				print(w_choices.keys())
				w = choice(list(w_choices.keys()))

				# w = choice(list(words[max_len_down].keys()))
				# sorted_words_by_freq = sorted(words[max_len_down].items(), key = lambda item: len(item[1]),reverse = True )
				# w = choice(sorted_words_by_freq[0:100])[0]

				# Check if chosen word agres with current string of letters of current word [***STUPID SIMPLE WAY OF CHECKING AND FILLING PUZZLE*** -- WILL IMPROVE LATER]
				if not all([ w[ix] == l for (ix,l) in curr_letters_and_idxs ]):
					print("There's a mis-match!")
					print(G)
					continue

				clue = choice(words[max_len_down][w])
				print(w, clue)

				for idx,letter in enumerate(w):
					G[r1+idx][col] = letter


				across_flag = True

				self.refresh_word_len_dict(max_len_down, word_to_fill, 'down')

				print(G)


		exit()

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

	# print(clue_answer_dict[3].keys())

	# w = choice(list(clue_answer_dict[3].keys()))
	# clue = clue_answer_dict[3][w][0]
    #
	# print(w, clue)

	# for k in clue_answer_dict[4].keys():
	# 	if len(clue_answer_dict[4][k]) > 20:
	# 		print(k, clue_answer_dict[4][k])

	# for word_len in clue_answer_dict.keys():
	# 	clue_answer_dict[word_len] = sorted(clue_answer_dict[word_len].items(), key = lambda item: len(item[1]) )




	return clue_answer_dict



if __name__ == "__main__":
	main()
