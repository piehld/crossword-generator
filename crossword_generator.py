# IS590PZ - Final Assignment
# Crossword-Puzzle Generator
# Group: Dennis Piehl and Xianzhuo Cao

from union_find import UnionFindSet
import numpy as np
# import matplotlib.pyplot as plt
import copy
from ast import literal_eval
from random import choice
from time import sleep
import re
import pprint


def main():

	grid_dimensions = (5, 5)	# Number rows and columns in crossword puzzle grid
	black_square_density = 0.2	# [Maximum] Fraction of squares that will be black

	xw_puzzle = CrosswordPuzzle(grid_dimensions, black_square_density)

	print(xw_puzzle.empty_grid)

	nyt_words = read_nyt_corpus('./dict_sources/nyt-crossword-master/clues_fixed.txt', grid_dimensions)
	nyt_words = sort_word_dic(nyt_words) # Sort nyt_words by its length of the hints

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
		self.across, self.down, self.word_len_dict = self.gather_across_and_down_word_spaces()

		# self.fill_grid()

	def make_empty_grid(self):
		"""
		Method to generate a random empty grid, with symmetrical black and white squares, and numbering.

		Randomly choose black_squares, and make sure it obeys three rules above

		For testing purposes, will start with simple 5x5 grid with four corners set as black squares.
		"""

		G = np.empty(self.dims, dtype=str)	# Note: MUST use 'empty' (cannot use 'ndarray' or 'array'; the former will not be mutable (for some reason???) and the latter will be 1D); Also, if you use "np.string_" this actually makes it an array of "bytes"...?!
		G[:] = '_'	# Set all initialized cells to '_' so that columns line up on stdout (i.e., instead of setting them to empty '')

		# NORMALLY, will want to RANDOMLY pick a non-black square and then make it black (as well as the
		# symmetric/transpose location), so long as it doesn't create a rule violation in the standard puzzle design format
		# (e.g., cannot have any completely isolated regions, nor any white spaces flanked on either side by black squares).

		# HOWEVER, for testing purposes, we are going to just set all four corners to black squares.
		G[0,0], G[4,0], G[0,4], G[4,4] = '.', '.', '.', '.'
		self.blk_sqs_positions = [(0,0), (4,0), (0,4), (4,4)]
		self.empty_grid = copy.deepcopy(G)
		return self.empty_grid, self.blk_sqs_positions

		# Below is random generator -- for now use predetermined grid above.
		# When ready, remove 4 lines above

		center = int(self.rows/2)
		if self.ifcenter_black == True:
			G[center][center] = '.'

		rand_nums,rand_pool = int(self.num_blk_sqs / 2), [i for i in range(0,int((self.num_squares - 1) / 2))]
		self.blk_sqs_positions = []
		while(rand_nums > 0):
			rand_nums -= 1
			temp = choice(rand_pool)
			while(self.check_valid(G,temp) == False):
				temp = choice(rand_pool)
			rand_pool.remove(temp)
			self.blk_sqs_positions.append((int(temp/self.cols),temp % self.rows))
			G[int(temp/self.cols)][temp % self.rows] = '.'
			self.blk_sqs_positions.append((center * 2 - int(temp/self.cols),center * 2 - temp % self.rows))  # make the board symmetric
			G[center * 2 - int(temp/self.cols)][center * 2 - (temp % self.rows)] = '.'

		self.empty_grid = copy.deepcopy(G)

		return self.empty_grid, self.blk_sqs_positions


	def check_valid(self,G,next_move):
		'''
		check if a puzzle is valid when generating black squares
		'''
		puzzle = copy.deepcopy(G)
		row,col = int(next_move/self.cols),next_move % self.rows
		puzzle[row][col] = '.'
		return self.check_rule1(puzzle,row,col) and self.check_rule2(puzzle)

	def check_rule1(self,puzzle,row,col):
		'''
		check if all words are no less than 3 letters
		'''
		cur_length = 0
		for c in range(0,self.cols): # check if current row obeys the first rule
			if puzzle[row][c] == "_":
				cur_length += 1
			if puzzle[row][c] == ".":
				if cur_length < 3 and cur_length != 0:
					return False
				else:
					cur_length = 0
		if cur_length in (1,2):
			return False
		cur_length = 0
		for r in range(0,self.rows): # check if current column obeys the first rule
			if puzzle[r][col] == "_":
				cur_length += 1
			if puzzle[r][col] == ".":
				if cur_length < 3 and cur_length != 0:
					return False
				else:
					cur_length = 0
		if cur_length in (1,2):
			return False
		return True

	def check_rule2(self,puzzle):
		'''
		check if all white grids are connected
		use union find
		'''
		n = self.rows * self.cols
		s = UnionFindSet(n)
		### Everytime union your right and your down
		for r in range(0,self.rows):
			for c in range(0,self.cols):
				if puzzle[r][c] == "_":
					if r + 1 < self.rows and puzzle[r+1][c] == "_":
						s.union(r*self.cols+c,(r+1)*self.cols+c)
					if c + 1 < self.cols and puzzle[r][c+1] == "_":
						s.union(r*self.cols+c,r*self.cols+c+1)
				else:
					continue
		parent = -1
		for r in range(0,self.rows):
			for c in range(0,self.cols):
				if puzzle[r][c] == "_":
					if parent == -1:
						parent = r * self.cols + c
					else:
						if parent != s.find(r*self.cols+c):
							return False

		return True




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


	def update_across_and_down_with_partial_grid(self, grid_state): # updated across and down dicts with partial words to check possible validity
		"""
		Purpose of this function is to gather the current partial (or completed) list of words in the grid,
		to subsequently check each partially filled word for its potential to be a real word or not, as well
		as if a word which was filled indirectly is a real word or not.
		"""

		for k in self.across.keys():
			row = self.across[k]['start'][0]
			c1 = self.across[k]['start'][1]
			c2 = self.across[k]['end'][1] + 1
			temp_word = np.str.join('',grid_state[row][c1:c2])
			temp_word_re = temp_word.replace('_','.')

			self.across[k].update( {"word_temp": temp_word_re})

		for k in self.down.keys():
			col = self.down[k]['start'][1]
			r1 = self.down[k]['start'][0]
			r2 = self.down[k]['end'][0] + 1
			temp_word = np.str.join('',grid_state[r1:r2,col])
			temp_word_re = temp_word.replace('_','.')

			self.down[k].update( {"word_temp": temp_word_re})

		return


	def gather_all_possible_words(self, grid_state, word_dict):
		"""
		Method to gather the number of possible words that can be filled into the current state of the grid,
		based on the partial fill of the grid so far.

		# Regex compile idea from: https://stackoverflow.com/questions/38460918/regex-matching-a-dictionary-efficiently-in-python

		"""

		# TO ADD: Maybe don't run this if > 10000 possibilities
		# OR BETTER: In list creation below, only gather the words with a partial letter in it, (i.e., ignore all-blank words...)

		curr_grid_word_patterns = [self.across[k]['word_temp'] for k in self.across.keys()] + [self.down[k]['word_temp'] for k in self.down.keys()]
		print(curr_grid_word_patterns)

		curr_grid_word_regex_compiled_dict = {}
		for wp in curr_grid_word_patterns:
			if len(wp) not in curr_grid_word_regex_compiled_dict.keys():
				curr_grid_word_regex_compiled_dict.update({len(wp):[re.compile(wp).match]})
			else:
				curr_grid_word_regex_compiled_dict[len(wp)].append(re.compile(wp).match)

		num_possible_words_to_fill = 0
		all_word_choices = {}
		for wlen in curr_grid_word_regex_compiled_dict.keys():
			w_choices = {k:v for k,v in word_dict[wlen].items() if any ( regex_match(k) for regex_match in curr_grid_word_regex_compiled_dict[wlen] ) }
			all_word_choices.update( {wlen : w_choices} )
			print("Number possible words of length",wlen,"=", len(w_choices))
			num_possible_words_to_fill += len(w_choices)

		all_possible_words_by_curr_word = {}
		for i in range(len(curr_grid_word_patterns)):
			curr_word = curr_grid_word_patterns[i]
			curr_word_len = len(curr_word)
			curr_word_choices = {k for k in all_word_choices[curr_word_len].keys() if re.match(curr_word, k)}
			# curr_word_choices = {k:v for k,v in all_word_choices[curr_word_len].items() if re.match(curr_word, k)}
			# curr_word_choices = {curr_word:v for k,v in all_word_choices[curr_word_len].items() if re.match(curr_word, k)}
			# all_possible_words_by_curr_word.update(curr_word_choices)
			all_possible_words_by_curr_word.update({curr_word:curr_word_choices})


		print("Total number of possible word choices so far:", num_possible_words_to_fill)


		# if num_possible_words_to_fill < 100:
			# pprint.pprint(all_possible_words_by_curr_word)
			# print([v for k,v in all_word_choices.items()])

		# TO ADD: Return the whole dictionary as already done here, but also return which across or down word to fill next based on having the fewest possible fills
		return all_word_choices


	def is_fill_of_rest_of_grid_possible(self, grid_state, word_dict): # return bool
		"""
		Method to check if filling of all remaining words is possible based on the letters in partially-filled words,
		as well as if any indirectly filled words are actually real words.

		"""

		# curr_grid_word_patterns = [self.across[k]['word_temp'] for k in self.across.keys()] + [self.down[k]['word_temp'] for k in self.down.keys()]

		return True

		return False



	def fill_grid(self, word_dict):
		"""
		Method to fill the grid.

		When assigning words to white-square stretches, can use: np[0][0:4] = "LAIR" (or similar, where 4 is the 'end' of the word)

		Fill LONGER words first, then crossings to the longer words
		ALSO Choose most common words first (or rank them all)

		# word_join = np.str.join('',G2[0][0:5])	# command to join cells from 0,0 to 0,5; will be useful later...maybe.


		:param word_dict: Word corpus (in dict. format) to use to fill grid.
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

		G = copy.deepcopy(self.empty_grid)
		print(G)

		across_flag = True

		while '_' in G:
			try:
				# First, choose the longest across word length to fill
				if across_flag:
					self.update_across_and_down_with_partial_grid(G)
					max_word_len = max(self.word_len_dict['across'].keys())
					word_to_fill = choice(self.word_len_dict['across'][max_word_len])
					print("Across word to fill", word_to_fill, self.across[word_to_fill])

					# use for across only
					row = self.across[word_to_fill]['start'][0]
					c1 = self.across[word_to_fill]['start'][1]
					c2 = self.across[word_to_fill]['end'][1] + 1

					all_word_choices = self.gather_all_possible_words(G, word_dict)
					w = choice(list(all_word_choices[max_word_len].keys()))
					clue = choice(all_word_choices[max_word_len][w])
					print(w, clue)

					# w_choices = {k:v for k,v in word_dict[max_word_len].items() if re.match(self.across[word_to_fill]['word_temp'], k)}
					# w = choice(list(w_choices.keys()))

					# Lambda function for ranking word use frequency
					# sorted_words_by_freq = sorted(word_dict[max_word_len].items(), key = lambda item: len(item[1]),reverse = True )
					# w = choice(sorted_words_by_freq[0:100])[0]

					for idx,letter in enumerate(w):
						G[row][c1+idx] = letter

					across_flag = False

					self.refresh_word_len_dict(max_word_len, word_to_fill, 'across')
					print(self.across, self.down)
					print(G)

				elif not across_flag:
					self.update_across_and_down_with_partial_grid(G)
					max_word_len = max(self.word_len_dict['down'].keys())
					word_to_fill = choice(self.word_len_dict['down'][max_word_len])
					print("Down word to fill", word_to_fill, self.down[word_to_fill])

					# use for down only
					col = self.down[word_to_fill]['start'][1]
					r1 = self.down[word_to_fill]['start'][0]
					r2 = self.down[word_to_fill]['end'][0] + 1

					all_word_choices = self.gather_all_possible_words(G, word_dict)
					w = choice(list(all_word_choices[max_word_len].keys()))
					clue = choice(all_word_choices[max_word_len][w])
					print(w, clue)

					# w_choices = {k:v for k,v in word_dict[max_word_len].items() if re.match(self.down[word_to_fill]['word_temp'], k)}
					# w = choice(list(w_choices.keys()))

					# Lambda function for ranking word use frequency
					# sorted_words_by_freq = sorted(word_dict[max_word_len].items(), key = lambda item: len(item[1]),reverse = True )
					# w = choice(sorted_words_by_freq[0:100])[0]

					for idx,letter in enumerate(w):
						G[r1+idx][col] = letter

					across_flag = True

					self.refresh_word_len_dict(max_word_len, word_to_fill, 'down')
					print(self.across, self.down)
					print(G)

			except Exception as err:
				print("Exception raised:", err)
				print("Re-attempting fill process...")
				G = copy.deepcopy(self.empty_grid)
				across_flag = True
				sleep(3)
				continue

		exit()

		self.filled_grid = copy.deepcopy(G)

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

	# for word_len in clue_answer_dict.keys():
	# 	clue_answer_dict[word_len] = sorted(clue_answer_dict[word_len].items(), key = lambda item: len(item[1]) )

	return clue_answer_dict


def sort_word_dic(word):
	'''
	Sort the dictionary by its length of hints
	'''
	for wordlength in word.keys():
		pairs= sorted(word[wordlength].items(),key = lambda item: len(item[1]),reverse = True)
		new_dic = {}
		for pair in pairs:
			new_dic[pair[0]] = pair[1]
		word[wordlength] = copy.deepcopy(new_dic)
	return word


if __name__ == "__main__":
	main()
