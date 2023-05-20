// A javascript-enhanced crossword puzzle [c] Jesse Weisbeck, MIT/GPL
(function($) {
        $(function() {
                // provide crossword entries in an array of objects like the following example
                // Position refers to the numerical order of an entry. Each position can have
                // two entries: an across entry and a down entry
                var puzzleData =
                [
    {
        "clue": "Irish Gaelic",
        "answer": "ERSE",
        "position": 1,
        "orientation": "across",
        "startx": 2,
        "starty": 1
    },
    {
        "clue": "Haphazardly",
        "answer": "SLAPD",
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
        "clue": "Nike competitor",
        "answer": "ASICS",
        "position": 7,
        "orientation": "across",
        "startx": 1,
        "starty": 4
    },
    {
        "clue": "\"Cheat, in a way\"",
        "answer": "PEEK",
        "position": 8,
        "orientation": "across",
        "startx": 1,
        "starty": 5
    },
    {
        "clue": "\"\"\"ER\"\" actress Christine\"",
        "answer": "ELISE",
        "position": 1,
        "orientation": "down",
        "startx": 2,
        "starty": 1
    },
    {
        "clue": "Flaxlike fiber",
        "answer": "RAMIE",
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
        "clue": "Breyers rival",
        "answer": "EDYS",
        "position": 4,
        "orientation": "down",
        "startx": 5,
        "starty": 1
    },
    {
        "clue": "Polaroid",
        "answer": "SNAP",
        "position": 5,
        "orientation": "down",
        "startx": 1,
        "starty": 2
    }
]
		$('#puzzle-wrapper').crossword(puzzleData);
	})
})(jQuery)
