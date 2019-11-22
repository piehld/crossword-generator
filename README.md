# 590PZ-Project - Crossword-Puzzle Generator
Forks of this are student projects for IS 590PZ
Authors: Dennis Piehl and Xianzhuo Cao

# Crossword Generator:
A python program that will generate a filled crossword puzzle of specified dimensions and density of black squares.

The script relies on access to local word corpora/lists to be used in generating each puzzle, and subsequently generates clues using definitions from WordNet (via the NLTK library), Merriam-Webster's API, or Wikipedia (via the wikipedia API library). The program outputs the completely-filled crossword puzzle as a JSON file, 'data.json,' which is also written into a javascript user interface for viewing and filling in the puzzle (using the framework developed here: https://github.com/jweisbeck/Crossword).

# Attributions:
 - User interface for displaying and filling in crossword puzzles: https://github.com/jweisbeck/Crossword
	- Re-implemented here under the 'website' directory
 	- Our program will export the generated puzzle into this framework.
 - Union-find source code in Python ('union_find.py'): https://zxi.mytechroad.com/blog/data-structure/sp1-union-find-set/
 	- This is imported and used directly by our code as part of the blank grid generation.
 - Referrals for most word lists: https://www.quinapalus.com/xwfaq.html
 - Word Lists:
	- WordNet
		- Obtained here: https://wordnet.princeton.edu/download/current-version
		- Citation: Princeton University "About WordNet." WordNet. Princeton University. 2010.
	- UKACD18plus (UK Advanced Cryptics Dictionary)
		- Obtained here: https://www.quinapalus.com/qxwdownload.html
	- YAWL (Yet Another Word List)
		- Obtained here: http://freshmeat.sourceforge.net/projects/yawl/
	- SCOWL (Spell Checker Oriented Word Lists)
		- Obtained here: http://wordlist.aspell.net/

# Other references and resources:
 - https://pypi.org/project/wikipedia/
 - https://www.nltk.org/
 - https://dictionaryapi.com/
 - https://www.nytimes.com/puzzles/submissions/crossword
 - https://www.nytimes.com/2018/05/11/crosswords/how-to-make-crossword-puzzle-grid.html
