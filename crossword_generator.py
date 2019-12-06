# IS590PZ - Final Assignment
# Crossword-Puzzle Generator
# Group: Dennis Piehl and Xianzhuo Cao

from union_find import UnionFindSet
import numpy as np
import copy
from ast import literal_eval
from random import choice, choices
import re
import pprint
import sys
import os
import requests
import json
from nltk.corpus import wordnet as wn
import wikipedia


def main():
	"""
	Main function for generating a crossword puzzle.

	PARAMETERS TO SPECITY BELOW:
		grid_dimensions:	  	Size of crossword puzzle grid (rows, columns). Must(?) be Odd x Odd (min. 5x5, max. 24x24)
		black_square_density:	Proportion of grid squares to make black. Be aware that too high of density may cause the program to
								freeze, due to it being unable to generate a legal grid (e.g., if it would result in a 2-letter word)
		word_sample_size:		Number of words to sample from the word corpus for each iteration of the filling process
		penalty_limit:			Number of times program is allowed to reach a dead end before restarting from a clean slate


	Word corpora used:
		WordNet noun, adjective, verb, and adverb lists.
			- Obtained here: https://wordnet.princeton.edu/download/current-version
			- Citation: Princeton University "About WordNet." WordNet. Princeton University. 2010.
		UKACD18plus (UK Advanced Cryptics Dictionary)
			- Obtained here: https://www.quinapalus.com/qxwdownload.html
		TWL06 (Tournament Word List)
			- Obtained here: https://www.wordgamedictionary.com/word-lists/
		Western English word list
			- Also obtained here: https://www.wordgamedictionary.com/word-lists/
		YAWL (Yet Another Word List)
			- Obtained here: http://freshmeat.sourceforge.net/projects/yawl/
		SCOWL (Spell Checker Oriented Word Lists)
			- Obtained here: http://wordlist.aspell.net/

	"""
	global main_word_corpus
	global word_sample_size
	global penalty_limit

	grid_dimensions = (7,7)		# Size of crossword puzzle grid (rows, columns). Must(?) be Odd x Odd (min. 5x5, max. 24x24)
	black_square_density = 0.19	# Proportion of grid squares to make black. Be aware that too high of density may cause program to freeze, due to it being unable to generate a legal grid (e.g., if it would result in a 2-letter word)
	word_sample_size = 30	# Number of words to sample from the word corpus for each iteration of the filling process
	penalty_limit = 10		# Number of times program is allowed to reach a dead end before restarting from a clean slate

	XW_Puzzle = CrosswordPuzzle(grid_dimensions, black_square_density)

	print(XW_Puzzle.empty_grid)

	word_corpus_files = [
						'./dict_sources/wordnet/index.noun.processed.txt',
						'./dict_sources/wordnet/index.adj.processed.txt',
						'./dict_sources/wordnet/index.verb.processed.txt',
						'./dict_sources/wordnet/index.adv.processed.txt',
						'./dict_sources/qxw/UKACD18plus.txt.processed.txt',
						'./dict_sources/TWL/english.txt.processed.txt',
						'./dict_sources/TWL/twl06.txt.processed.txt',
						# './dict_sources/YAWL/yawl-0.3.2.03/word.list.processed.txt',
						# './dict_sources/SCOWL/scowl-2019.10.06/final/american-and-english.processed.txt',
						]
	main_word_corpus = read_word_corpus(word_corpus_files)
	size_of_corp = sum(len(main_word_corpus[k]) for k in main_word_corpus)
	print("Size of word corpus being used:", size_of_corp)

	# main_word_corpus = sort_word_dic(main_word_corpus) # Optional: Sort main_word_corpus by its length of the hints (Not relevant yet--see notes in sorting function below)

	# Fill grid using recursive function:
	XW_Puzzle.filled_grid =	XW_Puzzle.fill_grid_recursively(main_word_corpus, 0)
	print("DONE FILLING GRID!\nGenerating clues...")
	XW_Puzzle.generate_hints()
	print("\nAcross:")
	pprint.pprint(XW_Puzzle.across)
	print("\nDown:")
	pprint.pprint(XW_Puzzle.down)
	XW_Puzzle.write_to_json()
	print("\nDONE! Puzzle, clues, and answers written to 'data.json' and './website/Crossword-master/js/script.js' files.\nTo play, open './website/Crossword-master/index.html' with your favorite internet browser. Enjoy!")

	return


class CrosswordPuzzle:
	"""
	Crossword Puzzle class for representing a full (unfilled or filled) crossword puzzle grid.

	Rules followed in grid generation:
		1) All words must be >= 3 characters
		2) All white spaces should be connected (i.e., no enclosed/blocked-off regions)
			* Using union-find algorithm to check this
		3) All white squares must be part of BOTH an Across AND Down crossing
			(i.e., there must be at least 1 white square to the left or right,
					AND at least 1 white square to the top or bottom.)
		4) Currently, must be Odd x Odd size (grid-generation restriction)

	- Also, for generating an easier case, option to ensure there is at least one black square in each row and each column
		(i.e., don't leave words that span the full grid length)
	"""

	def __init__(self, dimensions: tuple, density: float):
		"""
		Initialize the crossword puzzle grid.

		:param dimensions:	Specified grid dimensions as a tuple (rows, columns).
							Currently, must be Odd x Odd size.
		:param density:	Fraction of grid to set as black squares, as a float.

		:return self:	CrosswordPuzzle object.

		"""

		self.dims = dimensions
		self.rows = dimensions[0]
		self.cols = dimensions[1]
		self.ifcenter_black = False # Parameter to determine if the center is black
		self.density = density	# Should add a check to make sure the density is low enough that a "valid puzzle" is still possible (i.e., that no two-letter words are present, etc.)
		self.num_squares = dimensions[0]*dimensions[1]
		self.num_blk_sqs = round(self.num_squares * self.density) # If odd, center square must be made black; if even, no need.
		if self.num_blk_sqs % 2 != 0: # If odd number of black squares, make it even so puzzle can easily be made symmetrical (wihtout having to make center square black)
			self.num_blk_sqs -= 1
			self.ifcenter_black = True

		self.empty_grid = None
		self.blk_sqs_positions = []
		self.across, self.down = None, None
		self.filled_grid = None

		## Call main methods upon initialization
		self.fill_process_started = False
		self.list_of_word_coordinates_filled = []	# A growing list of coordinates for each word filled in the grid, to allow for easier access to backtrack word fill if necessary.

		self.make_empty_grid()
		self.initialize_across_and_down_word_spaces()
		self.grid = copy.deepcopy(self.empty_grid)


	def make_empty_grid(self):
		"""
		Method to generate a random empty grid, with symmetrical black and white squares, and numbering.

		Randomly choose black_squares, and make sure it obeys three rules above
		"""

		G = np.empty(self.dims, dtype=str)
		G[:] = '_'	# Set all initialized cells to '_' so that columns line up on stdout (i.e., instead of setting them to empty '')

		center = int(self.rows/2)
		if self.ifcenter_black == True:
			G[center][center] = '.'
			self.blk_sqs_positions.append((center, center))

		rand_nums,rand_pool = int(self.num_blk_sqs / 2), [i for i in range(0,int((self.num_squares - 1) / 2))]
		# G, rand_nums = self.fill_at_least_one(G, rand_nums)	# OPTIONAL: Comment this in to try placing at least one black square in each row and column (to generate an easier puzzle to fill)
		while(rand_nums > 0):
			rand_nums -= 1
			temp = choice(rand_pool)
			flag = 0
			while(self.check_valid(G,temp) == False):
				flag += 1
				if flag >=100:
					restart_program()
				temp = choice(rand_pool)
			rand_pool.remove(temp)
			self.blk_sqs_positions.append((int(temp/self.cols),temp % self.rows))
			G[int(temp/self.cols)][temp % self.rows] = '.'
			self.blk_sqs_positions.append((center * 2 - int(temp/self.cols),center * 2 - (temp % self.rows)))  # make the board symmetric
			G[center * 2 - int(temp/self.cols)][center * 2 - (temp % self.rows)] = '.'

		self.empty_grid = copy.deepcopy(G)

		return


	def fill_at_least_one(self, G, rand_nums):
		"""
		Optional function.
		To generate an easier puzzle to fill, try placing at least one black square in each row and column.
		(Prevents having any words that will span the entire length of the grid.)
		"""

		col_list = [i for i in range(0,self.cols)]
		pool = [i for i in range(0,self.cols)]
		center = int(self.rows/2)
		for row in range(0,int(self.rows/2)+1):
			rand_nums -= 1
			temp = choice(pool) # choose a col randomly
			while(self.check_valid(G,row*self.cols+temp) == False):
				temp = choice(pool)
			if temp in col_list:
				col_list.remove(temp)
			if 2 * center - temp in col_list:
				col_list.remove(2*center-temp)
			self.blk_sqs_positions.append((row,temp))
			G[row][temp] = '.'
			self.blk_sqs_positions.append((center * 2 - row,center * 2 - temp))  # make the board symmetric
			G[center * 2 - row][center * 2 - temp] = '.'

		for col in col_list:
			rand_nums -= 1
			if rand_nums == 0:
				return G,rand_nums
			temp = choice(pool) # choose a row randomly
			while(self.check_valid(G,temp*self.cols+col) == False):
				temp = choice(pool)
			self.blk_sqs_positions.append((temp,col))
			G[temp][col] = '.'
			self.blk_sqs_positions.append((center * 2 - temp,center * 2 - col))  # make the board symmetric
			G[center * 2 - temp][center * 2 - col] = '.'
		return G,rand_nums



	def check_valid(self, G, next_move):
		"""
		Method to check if a puzzle grid is valid when generating the grid
		pattern and inserting black squares.

		Check to make sure the density is low enough that a "valid puzzle" is still possible (i.e., that no two-letter words are present, etc.),
		depending on the number of black squares requested to be put into the grid.
		"""
		puzzle = copy.deepcopy(G)
		row,col = int(next_move/self.cols),next_move % self.rows
		puzzle[row][col] = '.'
		if row in (int(self.rows/2)-1,int(self.rows/2)-1) and col == int(self.cols/2):
			return False
		if col in (int(self.cols/2)-1,int(self.cols/2)+1) and row == int(self.rows/2):
			return False
		return self.check_rule1(puzzle,row,col) and self.check_rule2(puzzle)

	def check_rule1(self,puzzle,row,col):
		"""
		Method to check if all words are at least 3 letters or longer.
		"""
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
		"""
		Method to check if all white grids are connected

		This method makes use of the imported 'union_find' script.
		"""
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



	def initialize_across_and_down_word_spaces(self):
		"""
		Method to gather the collection of blank across & down spaces, into which the words will be filled.

		Each across and down attribute will be a dictionary of the clue number, start and end positions of the word,
		length of the word, and the temporary word fill as a regex string.
		"""

		self.across, self.down = {}, {}
		checked_down_squares = []

		# Gather down words first (since that's how numbering is ordered)
		clue_enum = 0
		for r in range(self.rows):
			on_blank_across_squares = False
			for c in range(self.cols):
				on_blank_down_squares = False
				if (r,c) not in self.blk_sqs_positions:

					if on_blank_across_squares == True:
						if c == self.cols-1:	# if at end of row
							self.across[curr_across_num].update( {"end":(r,c)} )

					elif on_blank_across_squares == False:
						on_blank_across_squares = True
						clue_enum += 1
						self.across.update( {clue_enum: {"start":(r,c)}} )
						curr_across_num = clue_enum

					# Now proceed through the column dimension first
					if on_blank_down_squares == False and (r,c) not in checked_down_squares:

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

		# Get length of each word and append to both the word dict itself
		for k in self.across.keys():
			wlength = self.across[k]["end"][1] - ( self.across[k]["start"][1] - 1 )
			self.across[k]["len"] = wlength
			self.across[k]['word_temp'] = '.' * wlength
			self.across[k]['clue'] = None
			self.across[k]['answer'] = None

		for k in self.down.keys():
			wlength = self.down[k]["end"][0] - ( self.down[k]["start"][0] - 1 )
			self.down[k]["len"] = wlength
			self.down[k]['word_temp'] = '.' * wlength
			self.down[k]['clue'] = None
			self.down[k]['answer'] = None

		self.fill_process_started = False
		self.list_of_word_coordinates_filled = []

		print("Across",self.across)
		print("Down",self.down)

		return



	def fill_word(self, word_id_to_fill, word_to_fill_grid_with, direction):
		"""
		Method to fill a stretch of blank grid spaces with a word.

		:param word_id_to_fill:	Word ID/clue number of grid to fill.
		:param word_to_fill_grid_with:	Word to fill into stretch of grid spaces.
		:param direction:	Direction of word placement in grid ('across' or 'down').

		:return bool:	True if word can be filled without any creating any non-words; else, False.
		"""

		word_coords = []

		if direction == 'across':
			row = self.across[word_id_to_fill]['start'][0]
			c1 = self.across[word_id_to_fill]['start'][1]

			for idx,letter in enumerate(word_to_fill_grid_with):
				self.grid[row][c1+idx] = letter
				if self.across[word_id_to_fill]['word_temp'][idx] != letter:
					word_coords.append((row,c1+idx))

			self.list_of_word_coordinates_filled.append((word_id_to_fill, direction, word_coords))

			self.across[word_id_to_fill].update( {"word_temp": word_to_fill_grid_with})		# Update the "word_temp" attribute for the filled word:
			direction_of_words_to_update = 'down'	# Specify the transverse direction of words to update the single letters for


		if direction == 'down':
			col = self.down[word_id_to_fill]['start'][1]
			r1 = self.down[word_id_to_fill]['start'][0]

			for idx,letter in enumerate(word_to_fill_grid_with):
				self.grid[r1+idx][col] = letter
				if self.down[word_id_to_fill]['word_temp'][idx] != letter:
					word_coords.append((r1+idx,col))

			self.list_of_word_coordinates_filled.append((word_id_to_fill, direction, word_coords))

			self.down[word_id_to_fill].update( {"word_temp": word_to_fill_grid_with})	# Update the "word_temp" attribute for the filled word:
			direction_of_words_to_update = 'across'	# Specify the transverse direction of words to update the single letters for

		# Now update all affected across & down words in self, and check if real words
		if self.update_across_and_down_with_partial_grid(direction_of_words_to_update):
			return True
		else:
			return False


	def remove_last_added_word(self):
		"""
		Method to remove the most recently added word (in order of self.list_of_word_coordinates_filled).
		"""
		word_id_to_remove = self.list_of_word_coordinates_filled[-1][0]
		direction = self.list_of_word_coordinates_filled[-1][1]
		word_coords_to_clear = self.list_of_word_coordinates_filled[-1][2]

		# Clear letters from grid
		for coord in word_coords_to_clear:
			self.grid[coord] = '_'

		# Update the across or down attributes of words in the transverse direction
		self.update_across_and_down_with_partial_grid('across')
		self.update_across_and_down_with_partial_grid('down')

		self.list_of_word_coordinates_filled.pop(-1)

		return


	def update_across_and_down_with_partial_grid(self, direction_of_words_to_update):
		"""
		Method to gather and update the across and down dictionaries with the current set of partially (or
		completely) filled words in the puzzle grid, as well as to check if any words which were filled
		indirectly are real words or not.
		"""

		if direction_of_words_to_update == 'across':	# specifying which part of the grid needs updating will save time from iterating over all words that didn't get changed
			for k in self.across.keys():
				row = self.across[k]['start'][0]
				c1 = self.across[k]['start'][1]
				c2 = self.across[k]['end'][1] + 1
				temp_word = np.str.join('',self.grid[row][c1:c2])
				temp_word_re = temp_word.replace('_','.')

				# Check if any newly filled words are actually words or not
				if '.' not in temp_word_re:
					if not word_exists(temp_word_re):
						return False

				self.across[k].update( {"word_temp": temp_word_re})


		if direction_of_words_to_update == 'down':
			for k in self.down.keys():
				col = self.down[k]['start'][1]
				r1 = self.down[k]['start'][0]
				r2 = self.down[k]['end'][0] + 1
				temp_word = np.str.join('',self.grid[r1:r2,col])
				temp_word_re = temp_word.replace('_','.')

				# Check if any newly filled words are actually words or not
				if '.' not in temp_word_re:
					if not word_exists(temp_word_re):
						return False

				self.down[k].update( {"word_temp": temp_word_re})

		return True


	def gather_all_possible_words(self, word_dict: dict, count_only: bool):
		"""
		Method to gather the number of possible words that can be filled into the current state of the grid,
		based on the partial fill of the grid so far. Returns an updated (and smaller) dictionary of words
		that may be selected as possible fills in the next grid-fill iteration.

		To improve program runtime when cycling through a set of words to identify which fill would provide the
		highest number of possible words in the next grid-fill iteration (i.e., when 'count_only' is True), only
		partially-filled words are checked (i.e., words with at least 1 letter in it, but are not already filled).

		Efficient regex compile & search idea from: https://stackoverflow.com/questions/38460918/regex-matching-a-dictionary-efficiently-in-python

		:param word_dict:	Word corpus dictionary with word lengths as keys and a nested dictionary of words:clues as values.
		:param count_only:	Boolean flag indicating if the function should only return the count of word possibilities or the
							newly updated dictionary of possible words.

		:return all_possible_word_choices_by_len_dict:	Updated word corpus dictionary containing all the possible words that can be filled into
														the current state of the grid. Organized by the word length as keys, and nested dictionary
														of words:clues as values.
		:return all_possible_word_choices_by_pattern_dict:	Word dictionary containing all the same words as 'all_possible_word_choices_by_len_dict',
															but organized by word regex pattern as the keys rather than word length.
		:return most_restricted_word_to_fill:	Word pattern of the current grid state that has the fewest number of possible words to fill with.

		:return num_possible_words_to_fill: Number of possible words that can be filled in for the current state of the grid (only accounts for words
											that are already partially-filled). Returned only if 'count_only' is True.

		"""

		if count_only:
			curr_grid_word_patterns = [self.across[k]['word_temp'] for k in self.across.keys() if '.' in self.across[k]['word_temp'] and len(set(self.across[k]['word_temp'])) > 1] + [self.down[k]['word_temp'] for k in self.down.keys() if '.' in self.down[k]['word_temp'] and len(set(self.down[k]['word_temp'])) > 1]
		else:
			curr_grid_word_patterns = [self.across[k]['word_temp'] for k in self.across.keys() if '.' in self.across[k]['word_temp']] + [self.down[k]['word_temp'] for k in self.down.keys() if '.' in self.down[k]['word_temp']]

		curr_grid_word_patterns = list(set(curr_grid_word_patterns))	# Don't repeat for identical word patterns
		print(curr_grid_word_patterns)

		curr_grid_word_regex_compiled_dict = {}
		for wp in curr_grid_word_patterns:
			if len(wp) not in curr_grid_word_regex_compiled_dict.keys():
				curr_grid_word_regex_compiled_dict.update({len(wp):[re.compile(wp).match]})
			else:
				curr_grid_word_regex_compiled_dict[len(wp)].append(re.compile(wp).match)

		num_possible_words_to_fill = 0
		all_possible_word_choices_by_len_dict = {}
		for wlen in curr_grid_word_regex_compiled_dict.keys():
			w_choices = [wi for wi in word_dict[wlen] if any ( regex_match(wi) for regex_match in curr_grid_word_regex_compiled_dict[wlen] )]
			all_possible_word_choices_by_len_dict.update( {wlen : w_choices} )
			num_possible_words_to_fill += len(w_choices)

		print("Total number of possible word choices so far:", num_possible_words_to_fill)

		if count_only:
			for wp in curr_grid_word_patterns:
				if len([k for k in all_possible_word_choices_by_len_dict[len(wp)] if re.compile(wp).match(k)]) == 0:
					return 0
			return num_possible_words_to_fill

		else:
			all_possible_word_choices_by_pattern_dict = {}
			for wp in curr_grid_word_patterns:
				wp_len = len(wp)
				curr_word_choices = [k for k in all_possible_word_choices_by_len_dict[wp_len] if re.compile(wp).match(k)]
				all_possible_word_choices_by_pattern_dict.update({wp:curr_word_choices})

		minimum_num_possible_fills = 1000000 # Arbitrarily chosen high number for comparing number of possibilities of each partial word in the current puzzle state.
		most_restricted_word_to_fill = None # initialize variable
		for wp in all_possible_word_choices_by_pattern_dict.keys():
			num_choices_for_curr_word = len(all_possible_word_choices_by_pattern_dict[wp])
			if num_choices_for_curr_word == 0:
				most_restricted_word_to_fill = wp
				break
			elif num_choices_for_curr_word < minimum_num_possible_fills:
				minimum_num_possible_fills = num_choices_for_curr_word
				most_restricted_word_to_fill = wp
			else:
				continue

		return all_possible_word_choices_by_len_dict, all_possible_word_choices_by_pattern_dict, most_restricted_word_to_fill



	def fill_grid_recursively(self, possible_word_dict: dict, penalty_count: int):
		"""
		Recursive method to fill the grid with words.

		Strategy works by filling in longest word(s) first, then the most limited/restricted words next (i.e., those with the
		fewest word possibilities for filling). At each iteration, a set of words are randomly picked from the word corpus
		dictionary (the number to pick is specified by 'word_sample_size'), and an attempt to fill each word is performed, at each
		point of which the number of possible words in the resulting grid state is recorded. The word from the pool that results
		in the MOST number of possible words AFTER being filled into the grid is the one chosen to actually fill into the grid.

		The new state of the puzzle grid is then sent back into this function to fill the next word. If a point is reached in
		which no fill is posssible or some other conflict occurs, a 'penalty' point is added and the grid reverts back one or
		more words (can be adjusted by copying the 'self.remove_last_added_word()' call multiple times in a row). Once a certain
		max number of penalties has occurred (specified by 'penalty_limit'), then the grid-filling process starts over from scratch.

		:param possible_word_dict:	Word corpus dictionary to use to for filling grid.
		:param penalty_count:	Number of penalties that have occurred at the current stage of the grid-filling process.

		"""
		global main_word_corpus
		global word_sample_size
		global penalty_limit

		if not '_' in self.grid:
			self.filled_grid = copy.deepcopy(self.grid)
			return self.filled_grid

		if penalty_count == penalty_limit:
			print("\nPENALTY LMIT REACHED: Re-attempting fill process from scratch...\n")
			self.grid = copy.deepcopy(self.empty_grid)
			self.initialize_across_and_down_word_spaces()
			penalty_count = 0
			return self.fill_grid_recursively(main_word_corpus, penalty_count)

		# Now do the actual filling part
		try:
			possible_word_dict_by_len, possible_word_dict_by_pattern, most_limited_word = self.gather_all_possible_words(main_word_corpus, count_only = False)
			most_limited_word_ids = [k for k in self.across.keys() if self.across[k]['word_temp'] == most_limited_word]
			if len(most_limited_word_ids) == 0:
				most_limited_word_ids = [k for k in self.down.keys() if self.down[k]['word_temp'] == most_limited_word]
				word_dir = 'down'
			else:
				word_dir = 'across'

			word_id_num_to_fill = choice(most_limited_word_ids)

			# If choosing first word or two, choose the longest in the puzzle
			if len(self.list_of_word_coordinates_filled) < 2:
				max_word_length = max(self.across[k]['len'] for k in self.across.keys())
				print(max_word_length)
				most_limited_word_ids = [k for k in self.across.keys() if self.across[k]['len'] == max_word_length and '.' in self.across[k]['word_temp']]
				word_dir = 'across'
				word_id_num_to_fill = choice(most_limited_word_ids)
				most_limited_word = self.across[word_id_num_to_fill]['word_temp']


			# TO ADD: Need to keep track of which words have been attempted for each particular step of the fill, to
			# 		  prevent entering a repetitive loop where the same sequence of words are attempted over and over.
			wds = choices(possible_word_dict_by_pattern[most_limited_word], k = word_sample_size)
			wds = set(list(wds)) # Only check unique words
			print(wds)
			if len(wds) == 0:
				print("Removing last 3 words and trying again...\n")
				self.remove_last_added_word()
				self.remove_last_added_word()
				self.remove_last_added_word()
				return self.fill_grid_recursively(main_word_corpus, penalty_count)

			print("Most limited word pattern to fill:", most_limited_word, "at", word_id_num_to_fill, word_dir)

			most_flexible_word = None
			most_possible_new_words_allowed = 0
			for w in wds:
				if self.fill_word(word_id_num_to_fill, w, word_dir):
					# Get number of possible words
					number_possible_new_words = self.gather_all_possible_words(possible_word_dict_by_len, count_only = True)
					if number_possible_new_words >= most_possible_new_words_allowed:
						most_flexible_word = w
						most_possible_new_words_allowed = number_possible_new_words
					self.remove_last_added_word()
				else:
					self.remove_last_added_word()

			try:
				print("  Filling with  ---->  ", most_flexible_word)
				self.fill_word(word_id_num_to_fill, most_flexible_word, word_dir)
			except Exception as err:
				print("\nEXCEPTION:", err)
				print("Removing last 3 words and trying again...\n")
				self.remove_last_added_word()
				self.remove_last_added_word()
				self.remove_last_added_word()
				penalty_count += 1

			print(self.grid)

			return self.fill_grid_recursively(main_word_corpus, penalty_count)

		except Exception as err:
			print("\nEXCEPTION:", err)
			print("Removing last 3 words and trying again...\n")
			penalty_count += 1
			self.remove_last_added_word()
			self.remove_last_added_word()
			self.remove_last_added_word()
			return self.fill_grid_recursively(main_word_corpus, penalty_count)


	def generate_hints(self):
		"""
		Method to generate clues for all words of the completed crossword puzzle.

		Makes use of the NLTK WordNet Python module, Merriam-Webster API, and Wikipedia Python API library,
		to try to find a corresponding clue for each word.

		If still no clues are able to be found, then the unkown word is assigned the hint, "[Mystery Clue!]."

		"""
		for key in self.across:
			word = self.across[key]['word_temp']
			self.across[key]['answer'] = word

			try:
				synonym_list = wn.synsets(word)	# Then try NLTK to find if there are synonyms
				worddef = synonym_list[0].definition()
				if len(worddef) > 1:
					self.across[key]['clue'] = str(worddef)
				continue
			except Exception:
				pass

			# If NLTK doesn't work, try Merriam Webster API
			url = "https://dictionaryapi.com/api/v3/references/ithesaurus/json/" + word + "?key=a0c37a49-8082-4e6e-984e-1a1275ba3c03"
			response = json.loads(requests.get(url).text)

			if response and isinstance(response[0],dict): # If it can be found in the Merriam Webster Dictionary, we use the definition
				self.across[key]['clue'] = response[0]['def'][0]['sseq'][0][0][1]['dt'][0][1]
				continue

			# If Merriam Webster doesn't work, try Wikipedia
			if wikipedia.search(word) != []:
				if word == wikipedia.search(word)[0].upper():# If it can be used as search keyword
					try:
						self.across[key]['clue'] = wikipedia.page(wikipedia.search(word)[0]).summary.split(".")[0].replace(wikipedia.search(word)[0],"___")
						continue
					except wikipedia.DisambiguationError as e:
						pass
				for title in wikipedia.search(word):
					if word in title.upper() and word!=title.upper():
						self.across[key]['clue'] = title.upper().replace(word,"_____")
						break

			if self.across[key]['clue'] != None:
				continue
			else:
				self.across[key]['clue'] = "[Mystery Clue!]"

		for key in self.down:
			word = self.down[key]['word_temp']
			self.down[key]['answer'] = word

			try:
				synonym_list = wn.synsets(word)	# Then try NLTK to find if there are synonyms
				worddef = synonym_list[0].definition()
				if len(worddef) > 1:
					self.down[key]['clue'] = str(worddef)
				continue
			except Exception:
				pass

			# If NLTK doesn't work, try Merriam Webster API
			url = "https://dictionaryapi.com/api/v3/references/ithesaurus/json/" + word + "?key=a0c37a49-8082-4e6e-984e-1a1275ba3c03"
			response = json.loads(requests.get(url).text)
			if response and isinstance(response[0],dict): # If it can be found in the Merriam Webster Dictionary, we use the definition
				self.down[key]['clue'] = response[0]['def'][0]['sseq'][0][0][1]['dt'][0][1]
				continue

			# If Merriam Webster doesn't work, try Wikipedia
			if wikipedia.search(word) != []:
				if word == wikipedia.search(word)[0].upper():# If it can be used as search keyword
					try:
						self.down[key]['clue'] = wikipedia.page(wikipedia.search(word)[0]).summary.split(".")[0].replace(wikipedia.search(word)[0],"___")
						continue
					except wikipedia.DisambiguationError as e:
						pass
				for title in wikipedia.search(word):
					if word in title.upper() and word!= title.upper():
						self.down[key]['clue'] = title.upper().replace(word,"_____")
						break

			if self.down[key]['clue'] != None:
				continue
			else:
				self.down[key]['clue'] = "[Mystery Clue!]"

		return



	def write_to_json(self):
		res = []
		for key in self.across.keys():
			dic = {}
			dic["clue"] = self.across[key]["clue"]
			dic["answer"] = self.across[key]["answer"]
			dic["position"] = key
			dic["orientation"] = "across"
			dic["startx"] = self.across[key]["start"][1]+1
			dic["starty"] = self.across[key]["start"][0]+1
			res.append(dic)

		for key in self.down.keys():
			dic = {}
			dic["clue"] = self.down[key]["clue"]
			dic["answer"] = self.down[key]["answer"]
			dic["position"] = key
			dic["orientation"] = "down"
			dic["startx"] = self.down[key]["start"][1]+1
			dic["starty"] = self.down[key]["start"][0]+1
			res.append(dic)

		json_str = json.dumps(res, indent=4)
		with open('data.json','w') as f:
			f.write(json_str)

		with open('./website/Crossword-master/js/script.js', 'w') as o:
			o.write("""// A javascript-enhanced crossword puzzle [c] Jesse Weisbeck, MIT/GPL\n(function($) {\n        $(function() {\n                // provide crossword entries in an array of objects like the following example\n                // Position refers to the numerical order of an entry. Each position can have\n                // two entries: an across entry and a down entry\n                var puzzleData =\n                """)
			o.write(json_str)
			o.write("""\n\t\t$('#puzzle-wrapper').crossword(puzzleData);\n\t})\n})(jQuery)\n""")
		return



def word_exists(word_to_check):
	"""
	Function to check if a completely-filled word is really a word (indirectly or directly).
	"""
	global main_word_corpus

	if word_to_check in main_word_corpus[len(word_to_check)].keys():
		return True
	else:
		return False


def read_word_corpus(file_list):
	"""
	Function to read in the provided dictionary word corpus.

	Will we be able to store this entire thing in memory?
	"""

	clue_answer_dict = {}

	# Initialize dictionary with maximum wordlength count
	for wl in range(1, 25):	# max word length of most crosswords ever is 24
		clue_answer_dict.update( { wl: {} } )

	for file in file_list:
		with open(file, 'r') as f:
			for line in f:
				clue = line.split('\t')[0]
				answer = line.split('\t')[1].strip()
				answer_len = len(answer)

				if answer_len is not None and answer_len > 0:
					if answer not in clue_answer_dict[answer_len].keys():
						clue_answer_dict[answer_len].update( { answer : [clue] } )	# Need to put clues in a list in case multiple clues exist for the same answer
					elif answer in clue_answer_dict[answer_len].keys():
						clue_answer_dict[answer_len][answer].append(clue)

	return clue_answer_dict


def sort_word_dic(word_dict):
	"""
	Sort the dictionary by its length of hints.

	Optional function to run on word corpus to sort words by the number of clues available for the word.
	In a way, this can provide a ranking system of most commonly used words for crosswords if you want to
	add those words first (with the assumption that these words will provide easier fills.)

	This is only useful if you are reading in a word corpus obtained from a clue-answer dump of many
	different crossword puzzles (e.g., if you were to save the output word list over hundreds of iterations
	of puzzle generation), since such a data dump would likely have a set of words that are listed multiple times.
	"""

	for wordlength in word_dict.keys():
		pairs= sorted(word_dict[wordlength].items(),key = lambda item: len(item[1]),reverse = True)
		new_dic = {}
		for pair in pairs:
			new_dic[pair[0]] = pair[1]
		word_dict[wordlength] = copy.deepcopy(new_dic)
	return word_dict


def restart_program():
	print("Re-attempting random blank-grid generation...")
	python = sys.executable
	os.execl(python, python, * sys.argv)


if __name__ == "__main__":
	main()
