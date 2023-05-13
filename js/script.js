// A javascript-enhanced crossword puzzle [c] Jesse Weisbeck, MIT/GPL
(function($) {
        $(function() {
                // provide crossword entries in an array of objects like the following example
                // Position refers to the numerical order of an entry. Each position can have
                // two entries: an across entry and a down entry
                var puzzleData =
                [
    {
        "clue": "\"\"\"S.O.S.\"\" band\"",
        "answer": "ABBA",
        "position": 1,
        "orientation": "across",
        "startx": 1,
        "starty": 1
    },
    {
        "clue": "Handy places to shop",
        "answer": "MARTS",
        "position": 5,
        "orientation": "across",
        "startx": 1,
        "starty": 2
    },
    {
        "clue": "Nursery rhyme opening",
        "answer": "BAABAA",
        "position": 7,
        "orientation": "across",
        "startx": 1,
        "starty": 3
    },
    {
        "clue": "Gun",
        "answer": "REV",
        "position": 9,
        "orientation": "across",
        "startx": 1,
        "starty": 4
    },
    {
        "clue": "Backwoods address abbr.",
        "answer": "RFD",
        "position": 10,
        "orientation": "across",
        "startx": 5,
        "starty": 4
    },
    {
        "clue": "Tobacco plug",
        "answer": "DOTTLE",
        "position": 12,
        "orientation": "across",
        "startx": 2,
        "starty": 5
    },
    {
        "clue": "Not slipping as much",
        "answer": "SURER",
        "position": 14,
        "orientation": "across",
        "startx": 3,
        "starty": 6
    },
    {
        "clue": "Affix a brand to",
        "answer": "SEAR",
        "position": 15,
        "orientation": "across",
        "startx": 4,
        "starty": 7
    },
    {
        "clue": "Writer Bierce",
        "answer": "AMBR",
        "position": 1,
        "orientation": "down",
        "startx": 1,
        "starty": 1
    },
    {
        "clue": "Cried out on a farm",
        "answer": "BAAED",
        "position": 2,
        "orientation": "down",
        "startx": 2,
        "starty": 1
    },
    {
        "clue": "Curtain call chorus",
        "answer": "BRAVOS",
        "position": 3,
        "orientation": "down",
        "startx": 3,
        "starty": 1
    },
    {
        "clue": "Up",
        "answer": "ATB",
        "position": 4,
        "orientation": "down",
        "startx": 4,
        "starty": 1
    },
    {
        "clue": "\"\"\"The Words\"\" autobiographer\"",
        "answer": "SARTRE",
        "position": 6,
        "orientation": "down",
        "startx": 5,
        "starty": 2
    },
    {
        "clue": "\"\"\"___ in Her Ear\"\" (classic Georges Feydeau farce)\"",
        "answer": "AFLEA",
        "position": 8,
        "orientation": "down",
        "startx": 6,
        "starty": 3
    },
    {
        "clue": "Charlie Chan creator Earl ___ Biggers",
        "answer": "DERR",
        "position": 11,
        "orientation": "down",
        "startx": 7,
        "starty": 4
    },
    {
        "clue": "Overseer of schools: Abbr.",
        "answer": "TUS",
        "position": 13,
        "orientation": "down",
        "startx": 4,
        "starty": 5
    }
]
		$('#puzzle-wrapper').crossword(puzzleData);
	})
})(jQuery)
