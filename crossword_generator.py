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
		self.across, self.down, self.word_len_dict = None, None, None

		## Call main methods upon initialization
		self.make_empty_grid()
		self.gather_across_and_down_word_spaces()
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

		self.across, self.down = {}, {}
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
							self.across[curr_across_num].update( {"end":(r,c)} )

					elif on_blank_across_squares == False:
						on_blank_across_squares = True
						clue_enum += 1
						self.across.update( {clue_enum: {"start":(r,c)}} )
						curr_across_num = clue_enum

					if on_blank_down_squares == False and (r,c) not in checked_down_squares:
						# Now proceed through the column dimension first

						# If down word doesn't start at same square as across word, increment the clue number
						if (r,c) != self.across[curr_across_num]["start"]:
							clue_enum += 1

						self.down.update( {clue_enum: {"start":(r,c)}} )
						on_blank_down_squares = True
						checked_down_squares.append((r,c))
						r2 = r
						while on_blank_down_squares:
							r2+=1
							if (r2,c) in self.blk_sqs_positions:
								self.down[clue_enum].update( {"end":(r2-1,c)} )
								on_blank_down_squares = False

							elif (r2,c) not in self.blk_sqs_positions:
								checked_down_squares.append((r2,c))
								if r2 == self.rows-1:	# if at end of column
									self.down[clue_enum].update( {"end":(r2,c)} )
									on_blank_down_squares = False
								else:
									continue

				elif (r,c) in self.blk_sqs_positions:
					if on_blank_across_squares == True:	# Then end the word
						self.across[curr_across_num].update( {"end":(r,c-1)} )
						on_blank_across_squares = False
					elif on_blank_across_squares == False:
						continue

		# Get length of each word, and append to both the word dict itself as well as a growing dict of word lengths to inform the fill order
		self.word_len_dict = {"across":{}, "down":{}}
		for k in self.across.keys():
			wlength = self.across[k]["end"][1] - ( self.across[k]["start"][1] - 1 )
			self.across[k]["len"] = wlength
			if wlength not in self.word_len_dict["across"].keys():
				self.word_len_dict["across"].update({wlength:[k]})
			elif wlength in self.word_len_dict["across"].keys():
				self.word_len_dict["across"][wlength].append(k)

		for k in self.down.keys():
			wlength = self.down[k]["end"][0] - ( self.down[k]["start"][0] - 1 )
			self.down[k]["len"] = wlength
			if wlength not in self.word_len_dict["down"].keys():
				self.word_len_dict["down"].update({wlength:[k]})
			elif wlength in self.word_len_dict["down"].keys():
				self.word_len_dict["down"][wlength].append(k)

		print("Across",self.across)
		print("Down",self.down)
		print("Word length dict",self.word_len_dict)

		return self.across, self.down, self.word_len_dict


	def refresh_word_len_dict(self, wd_len, wd_num_filled, direction):
		"""
		"""

		# print(self.word_len_dict[direction])

		idx = self.word_len_dict[direction][wd_len].index(wd_num_filled)
		self.word_len_dict[direction][wd_len].pop(idx)
		# print(self.word_len_dict[direction])

		# Now check if the list of availble words to fill is empty for the given length
		if len(self.word_len_dict[direction][wd_len]) == 0:
			self.word_len_dict[direction].pop(wd_len)

		# print(self.word_len_dict[direction])

		return


	def fill_word(self, grid_state, word_id_to_fill, word_to_fill_grid_with, direction):
		"""
		"""

		if direction == 'across':
			# use for across only
			row = self.across[word_id_to_fill]['start'][0]
			c1 = self.across[word_id_to_fill]['start'][1]
			c2 = self.across[word_id_to_fill]['end'][1] + 1

			for idx,letter in enumerate(word_to_fill_grid_with):
				grid_state[row][c1+idx] = letter

		if direction == 'down':
			# use for down only
			col = self.down[word_id_to_fill]['start'][1]
			r1 = self.down[word_id_to_fill]['start'][0]
			r2 = self.down[word_id_to_fill]['end'][0] + 1

			for idx,letter in enumerate(word_to_fill_grid_with):
				grid_state[r1+idx][col] = letter

		return grid_state



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

		curr_grid_word_patterns = [self.across[k]['word_temp'] for k in self.across.keys() if '.' in self.across[k]['word_temp']] + [self.down[k]['word_temp'] for k in self.down.keys() if '.' in self.down[k]['word_temp']]
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
		# for i in range(len(curr_grid_word_patterns)):
			# curr_word = curr_grid_word_patterns[i]
		for curr_word in curr_grid_word_patterns:
			curr_word_len = len(curr_word)
			curr_word_choices = {k for k in all_word_choices[curr_word_len].keys() if re.match(curr_word, k)}
			# curr_word_choices = {k:v for k,v in all_word_choices[curr_word_len].items() if re.match(curr_word, k)}
			# curr_word_choices = {curr_word:v for k,v in all_word_choices[curr_word_len].items() if re.match(curr_word, k)}
			# all_possible_words_by_curr_word.update(curr_word_choices)
			all_possible_words_by_curr_word.update({curr_word:curr_word_choices})


		print("Total number of possible word choices so far:", num_possible_words_to_fill)

		minimum_num_possible_fills = 100000 # arbitrarily chosen number of possible fills, to compare number possibilities for each partial word of the puzzle
		most_restricted_word_to_fill = None # initialize variable
		for curr_word in all_possible_words_by_curr_word.keys():
			num_choices_for_curr_word = len(all_possible_words_by_curr_word[curr_word])
			if num_choices_for_curr_word == 0:
				print("NO FILL POSSIBLE FOR WORD,", curr_word)
				most_restricted_word_to_fill = curr_word
				break
			elif num_choices_for_curr_word < minimum_num_possible_fills:
				minimum_num_possible_fills = num_choices_for_curr_word
				most_restricted_word_to_fill = curr_word
			else:
				continue


		# if num_possible_words_to_fill < 100:
			# pprint.pprint(all_possible_words_by_curr_word)
			# print([v for k,v in all_word_choices.items()])

		# TO ADD: Return the whole dictionary as already done here, but also return which across or down word to fill next based on having the fewest possible fills
		# return all_word_choices
		return all_possible_words_by_curr_word, most_restricted_word_to_fill


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

		fill_count = 0
		across_flag = True

		while '_' in G:

			self.update_across_and_down_with_partial_grid(G)

			# TO ADD: May want to fill longest words first (even if at first they might have more possibilities than shorter words...say, for the first 1/5 of the grid do it this way...?)

			try:

				all_word_choices_by_part_word, most_limited_word = self.gather_all_possible_words(G, word_dict)

				# First, choose the longest across word length to fill
				# NEED TO DO SOME MORE TESTING TO SEE IF THIS STRATEGY SAVES ANY TIME
				# 	(E.g., get an average number of iterations required to arrive at a complete puzzle with and without this strategy)
				# EVEN IF you determine that this doesn't improve the speed of puzzle filling, you can still keep this code block
				# 	to allow for the initial entry of pre-determined words (e.g., on the basis of puzzle theme)
				if fill_count < 3:
					if across_flag:
						word_dir = 'across'
						word_len_to_fill = max(self.word_len_dict[word_dir].keys())
						word_id_num_to_fill = choice(self.word_len_dict[word_dir][word_len_to_fill])
						print("Long across word to fill", word_id_num_to_fill, self.across[word_id_num_to_fill])
						w = choice(list(all_word_choices_by_part_word[self.across[word_id_num_to_fill]['word_temp']]))
						across_flag = False
					else:
						word_dir = 'down'
						word_len_to_fill = max(self.word_len_dict[word_dir].keys())
						word_id_num_to_fill = choice(self.word_len_dict[word_dir][word_len_to_fill])
						print("Long down word to fill", word_id_num_to_fill, self.down[word_id_num_to_fill])
						w = choice(list(all_word_choices_by_part_word[self.down[word_id_num_to_fill]['word_temp']]))
						across_flag = True

					clue = choice(word_dict[word_len_to_fill][w])


				else:
					print("Most limited word:", most_limited_word)

					# First check if the word is in the across dict; If not, then check if it's in the down dict
					most_limited_word_ids = [k for k in self.across.keys() if self.across[k]['word_temp'] == most_limited_word]
					if len(most_limited_word_ids) == 0:
						most_limited_word_ids = [k for k in self.down.keys() if self.down[k]['word_temp'] == most_limited_word]
						word_dir = 'down'
					else:
						word_dir = 'across'

					word_id_num_to_fill = choice(most_limited_word_ids)
					word_len_to_fill = len(most_limited_word)

					print(word_dir, "word to fill:", word_id_num_to_fill, most_limited_word)

					w = choice(list(all_word_choices_by_part_word[most_limited_word]))
					clue = choice(word_dict[word_len_to_fill][w])


				G = self.fill_word(G, word_id_num_to_fill, w, word_dir)
				self.refresh_word_len_dict(word_len_to_fill, word_id_num_to_fill, word_dir)

				print(w, clue)
				print(G)

				fill_count += 1


				# Lambda function for ranking word use frequency
				# sorted_words_by_freq = sorted(word_dict[word_len_to_fill].items(), key = lambda item: len(item[1]),reverse = True )
				# w = choice(sorted_words_by_freq[0:100])[0]

				# Old regex matching approach
				# w_choices = {k:v for k,v in word_dict[word_len_to_fill].items() if re.match(self.across[word_id_num_to_fill]['word_temp'], k)}
				# w_choices = {k:v for k,v in word_dict[word_len_to_fill].items() if re.match(self.down[word_id_num_to_fill]['word_temp'], k)}
				# w = choice(list(w_choices.keys()))

			except Exception as err:
				print("\nException raised:", err)
				print("Re-attempting fill process...\n")
				G = copy.deepcopy(self.empty_grid)
				self.gather_across_and_down_word_spaces()
				# sleep(3)
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
