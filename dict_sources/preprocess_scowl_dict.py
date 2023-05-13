import os

"""
Script to pre-process/clean up words from SCOWL data, filtering out only those that are of a relevant length, no numbers, no underscores, etc.

Will create a new smaller text file in the same readable format as other dictionary source files used.

Idea for efficient removal of special characters from here: https://stackoverflow.com/questions/5843518/remove-all-special-characters-punctuation-and-spaces-from-string
"""

dict_in_file_path_prefix = './SCOWL/scowl-2020.12.07/final/'
out_file_name = './SCOWL/american-and-english.processed.txt'

max_word_length = 25	# Don't think we'll be generating any puzzles larger than this

# Delete file if already exists, since will be 'appending' in chunks below, and don't want to keep appending to an an already processed file.
if os.path.isfile(out_file_name):
	os.remove(out_file_name)

for in_file in os.listdir(dict_in_file_path_prefix):
	if in_file.startswith('american') or in_file.startswith('english'):
		full_in_file_path = dict_in_file_path_prefix + in_file
		print(in_file)

		word_corpus = []
		i=0
		with open(full_in_file_path, 'r', encoding='latin-1') as f:
			for line in f:
				# print(line)
				try:
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
				except Exception as err:
					print("EXCEPTION",err)
					continue

		with open(out_file_name, 'a') as o:
			for w in word_corpus:
				o.write('[Blank clue]\t' + w.upper() + '\n')
			o.close()
