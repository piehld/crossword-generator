// A javascript-enhanced crossword puzzle [c] Jesse Weisbeck, MIT/GPL
(function($) {
        $(function() {
                // provide crossword entries in an array of objects like the following example
                // Position refers to the numerical order of an entry. Each position can have
                // two entries: an across entry and a down entry
                var puzzleData =
                [
    {
        "clue": "\"Four kings, maybe\"",
        "answer": "MELD",
        "position": 1,
        "orientation": "across",
        "startx": 2,
        "starty": 1
    },
    {
        "clue": "Yes or no follower",
        "answer": "SIREE",
        "position": 5,
        "orientation": "across",
        "startx": 1,
        "starty": 2
    },
    {
        "clue": "How ham may be served in a sandwich",
        "answer": "ONRYE",
        "position": 6,
        "orientation": "across",
        "startx": 1,
        "starty": 3
    },
    {
        "clue": "Butchers' offerings",
        "answer": "MEATS",
        "position": 7,
        "orientation": "across",
        "startx": 1,
        "starty": 4
    },
    {
        "clue": "African fox",
        "answer": "ASSE",
        "position": 8,
        "orientation": "across",
        "startx": 1,
        "starty": 5
    },
    {
        "clue": "Pits",
        "answer": "MINES",
        "position": 1,
        "orientation": "down",
        "startx": 2,
        "starty": 1
    },
    {
        "clue": "Odd jobs",
        "answer": "ERRAS",
        "position": 2,
        "orientation": "down",
        "startx": 3,
        "starty": 1
    },
    {
        "clue": "1944 battle site",
        "answer": "LEYTE",
        "position": 3,
        "orientation": "down",
        "startx": 4,
        "starty": 1
    },
    {
        "clue": "Ruby and Sandra",
        "answer": "DEES",
        "position": 4,
        "orientation": "down",
        "startx": 5,
        "starty": 1
    },
    {
        "clue": "Body of an organism",
        "answer": "SOMA",
        "position": 5,
        "orientation": "down",
        "startx": 1,
        "starty": 2
    }
]
		$('#puzzle-wrapper').crossword(puzzleData);
	})
})(jQuery)
