# 590PZ-Project - Crossword-Puzzle Generator
Forks of this are student projects for IS 590PZ

# Idea proposal:
Group: Dennis Piehl and Xianzhuo Cao

We propose creating a program that will generate crossword puzzles of specified dimensions (minimum 5x5, maximum 21x21), in which we will use available word corpuses from various dictionaries, online collections, and "crosswordese"-specific lists as sources for clues + solutions to be used in each puzzle. Because the nature of preparing a crossword puzzle requires that specific letters and words are used to fill in the empty spaces, each puzzle will only have one solution.

In deciding to pursue a crossword puzzle generator as opposed to a crossword puzzle solver, we recognized that the design of such a solver would be particularly difficult given the vagueness of many clues, as well as the pun and/or indirectness of many other clues. To solve a crossword puzzle, a computer is actually not well equipped unless the puzzle includes only real and direct clues. Typically, puzzles include many cultural references and/or puns that [currently] humans can more easily decipher.

We'll plan to pursue the standard style crossword puzzles, rather than the more simple "criss-cross" style puzzles, and using density as a way of adjusting difficulty (but still keeping within the reasonable level of black-square density as found in most publications). We will start with the smaller case to begin with, however, before moving onto bigger puzzles.

To make the game somewhat more unique than a crossword puzzle of random, unrelated words, we are also considering creating one that follows a general theme by pre-defining a few of the answers in the grid, and then filling in the puzzle around them. We are curious to know if doing this also makes the rest of the puzzle-filling process easier computationally, as it would immediately reduce the number of potential words that need to be cycled through. (Alternatively, this could also introduce a major obstacle for the program...so we will see!)
_____________________________

# Helpful resources/links:
 - https://github.com/jweisbeck/Crossword - Our demo is implementing our data into this framework.
 - https://zxi.mytechroad.com/blog/data-structure/sp1-union-find-set/ - This contains the source codes about the inplementation of union find in python. We used it directly in our code.
 - https://en.wikipedia.org/wiki/Crossword - This contains some of the important rules for crosswords (note only the American style crossword)
 - https://en.wikipedia.org/wiki/The_New_York_Times_crossword_puzzle
 - https://www.nytimes.com/puzzles/submissions/crossword
 - https://www.nytimes.com/2018/05/11/crosswords/how-to-make-crossword-puzzle-grid.html
 - https://www.quinapalus.com/xwfaq.html
