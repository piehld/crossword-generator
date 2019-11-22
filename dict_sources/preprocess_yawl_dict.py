import os

"""
Script to pre-process/clean up words from YAWL ("yet another word list") data, filtering out only those that are of a relevant length, no numbers, no underscores, etc.

Will create a new smaller text file in the same readable format as other dictionary source files used.

Idea for efficient removal of special characters from here: https://stackoverflow.com/questions/5843518/remove-all-special-characters-punctuation-and-spaces-from-string
"""

in_file = './YAWL/yawl-0.3.2.03/word.list'
out_file_name = in_file + '.processed.txt'

max_word_length = 25	# Don't think we'll be generating any puzzles larger than this

# Delete file if already exists, since will be 'appending' in chunks below, and don't want to keep appending to an an already processed file.
if os.path.isfile(out_file_name):
	os.remove(out_file_name)

word_corpus = []
i=0
with open(in_file, 'r') as f:
	for line in f:
		word = line.split()[0].strip()
		if len(word) < max_word_length:
			word = ''.join(l for l in word if l.isalpha())
			if len(word) > 2 and word not in word_corpus:	# Check separately in case string is left < 3 characters or empty
				word_corpus.append(word)
				i+=1
		if i==1000:
			with open(out_file_name, 'a') as o:
				for w in word_corpus:
					o.write('[Blank clue]\t' + w.upper() + '\n')
				o.close()
			word_corpus = []
			i=0

with open(out_file_name, 'a') as o:
	for w in word_corpus:
		o.write('[Blank clue]\t' + w.upper() + '\n')
	o.close()
