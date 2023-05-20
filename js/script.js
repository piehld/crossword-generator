// A javascript-enhanced crossword puzzle [c] Jesse Weisbeck, MIT/GPL
(function($) {
        $(function() {
                // provide crossword entries in an array of objects like the following example
                // Position refers to the numerical order of an entry. Each position can have
                // two entries: an across entry and a down entry
                var puzzleData =
                [
    {
        "clue": "Chuck",
        "answer": "TOSS",
        "position": 1,
        "orientation": "across",
        "startx": 2,
        "starty": 1
    },
    {
        "clue": "the central research and development organization for the United States Department of Defense; responsible for developing new surveillance technologies since 9/11",
        "answer": "DARPA",
        "position": 5,
        "orientation": "across",
        "startx": 1,
        "starty": 2
    },
    {
        "clue": "Mr. Spock portrayer",
        "answer": "NIMOY",
        "position": 6,
        "orientation": "across",
        "startx": 1,
        "starty": 3
    },
    {
        "clue": "Asian palm",
        "answer": "ARECA",
        "position": 7,
        "orientation": "across",
        "startx": 1,
        "starty": 4
    },
    {
        "clue": "Cutty ___",
        "answer": "SARK",
        "position": 8,
        "orientation": "across",
        "startx": 1,
        "starty": 5
    },
    {
        "clue": "long-tailed arboreal mustelid of Central America and South America",
        "answer": "TAIRA",
        "position": 1,
        "orientation": "down",
        "startx": 2,
        "starty": 1
    },
    {
        "clue": "an abalone found near the Channel Islands",
        "answer": "ORMER",
        "position": 2,
        "orientation": "down",
        "startx": 3,
        "starty": 1
    },
    {
        "clue": "\"\"\"Baby and Child Care\"\" author\"",
        "answer": "SPOCK",
        "position": 3,
        "orientation": "down",
        "startx": 4,
        "starty": 1
    },
    {
        "clue": "___ prayer",
        "answer": "SAYA",
        "position": 4,
        "orientation": "down",
        "startx": 5,
        "starty": 1
    },
    {
        "clue": "Genetic strands",
        "answer": "DNAS",
        "position": 5,
        "orientation": "down",
        "startx": 1,
        "starty": 2
    }
]
		$('#puzzle-wrapper').crossword(puzzleData);
	})
})(jQuery)
