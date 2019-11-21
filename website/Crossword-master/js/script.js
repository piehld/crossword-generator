// A javascript-enhanced crossword puzzle [c] Jesse Weisbeck, MIT/GPL 
(function($) {
	$(function() {
		// provide crossword entries in an array of objects like the following example
		// Position refers to the numerical order of an entry. Each position can have 
		// two entries: an across entry and a down entry
		var puzzleData = 
		[
    {
        "clue": "_____S",
        "answer": "SONO",
        "position": 1,
        "orientation": "across",
        "startx": 1,
        "starty": 1
    },
    {
        "clue": "Mystery",
        "answer": "UNBAG",
        "position": 5,
        "orientation": "across",
        "startx": 7,
        "starty": 1
    },
    {
        "clue": "RUSSIAN _____'",
        "answer": "AVOS",
        "position": 10,
        "orientation": "across",
        "startx": 1,
        "starty": 2
    },
    {
        "clue": "a monotonous sound like that of an insect in motion ",
        "answer": "THRUM",
        "position": 11,
        "orientation": "across",
        "startx": 7,
        "starty": 2
    },
    {
        "clue": "Mystery",
        "answer": "NONASPIRINS",
        "position": 12,
        "orientation": "across",
        "startx": 1,
        "starty": 3
    },
    {
        "clue": "SUN-_____",
        "answer": "RYPE",
        "position": 15,
        "orientation": "across",
        "startx": 3,
        "starty": 4
    },
    {
        "clue": "DRIES VAN _____",
        "answer": "AGT",
        "position": 16,
        "orientation": "across",
        "startx": 8,
        "starty": 4
    },
    {
        "clue": "JOHN _____",
        "answer": "DOE",
        "position": 17,
        "orientation": "across",
        "startx": 1,
        "starty": 5
    },
    {
        "clue": "_____ TECHNICA",
        "answer": "ARS",
        "position": 19,
        "orientation": "across",
        "startx": 5,
        "starty": 5
    },
    {
        "clue": "something that one hopes or intends to accomplish ",
        "answer": "AIM",
        "position": 21,
        "orientation": "across",
        "startx": 9,
        "starty": 5
    },
    {
        "clue": "_____ CORP.",
        "answer": "UGS",
        "position": 23,
        "orientation": "across",
        "startx": 1,
        "starty": 6
    },
    {
        "clue": "ENT\u00c4S _____, NISKAVUORI?",
        "answer": "NYT",
        "position": 24,
        "orientation": "across",
        "startx": 5,
        "starty": 6
    },
    {
        "clue": "___ Corporation (\u65e5\u672c\u96fb\u6c17\u682a\u5f0f\u4f1a\u793e, Nippon Denki Kabushiki-gaisha) is a Japanese multinational information technology and electronics company, headquartered in Minato, Tokyo, Japan",
        "answer": "NEC",
        "position": 25,
        "orientation": "across",
        "startx": 9,
        "starty": 6
    },
    {
        "clue": "BRITISH AEROSPACE _____",
        "answer": "EAP",
        "position": 26,
        "orientation": "across",
        "startx": 1,
        "starty": 7
    },
    {
        "clue": "_____LY",
        "answer": "GEE",
        "position": 27,
        "orientation": "across",
        "startx": 5,
        "starty": 7
    },
    {
        "clue": "_____ MODEM",
        "answer": "DSL",
        "position": 28,
        "orientation": "across",
        "startx": 9,
        "starty": 7
    },
    {
        "clue": "___ (, also written lwa  as in Haitian Creole) are the spirits of Haitian Vodou and Louisiana Voodoo",
        "answer": "LOA",
        "position": 29,
        "orientation": "across",
        "startx": 2,
        "starty": 8
    },
    {
        "clue": "al_itihaad_al_islamiya",
        "answer": "AIAI",
        "position": 31,
        "orientation": "across",
        "startx": 6,
        "starty": 8
    },
    {
        "clue": "sanderling",
        "answer": "SANDERLINGS",
        "position": 33,
        "orientation": "across",
        "startx": 1,
        "starty": 9
    },
    {
        "clue": "Mystery",
        "answer": "ELSOL",
        "position": 37,
        "orientation": "across",
        "startx": 1,
        "starty": 10
    },
    {
        "clue": "_____ LANGUAGE",
        "answer": "LESE",
        "position": 38,
        "orientation": "across",
        "startx": 8,
        "starty": 10
    },
    {
        "clue": "Mystery",
        "answer": "TAEBO",
        "position": 39,
        "orientation": "across",
        "startx": 1,
        "starty": 11
    },
    {
        "clue": "_____ (DISAMBIGUATION)",
        "answer": "SSRI",
        "position": 40,
        "orientation": "across",
        "startx": 8,
        "starty": 11
    },
    {
        "clue": "_____ FRANCISCO",
        "answer": "SAN",
        "position": 1,
        "orientation": "down",
        "startx": 1,
        "starty": 1
    },
    {
        "clue": "_____ SOUND",
        "answer": "OVO",
        "position": 2,
        "orientation": "down",
        "startx": 2,
        "starty": 1
    },
    {
        "clue": "Mystery",
        "answer": "NONRESPONSE",
        "position": 3,
        "orientation": "down",
        "startx": 3,
        "starty": 1
    },
    {
        "clue": "Mystery",
        "answer": "OSAY",
        "position": 4,
        "orientation": "down",
        "startx": 4,
        "starty": 1
    },
    {
        "clue": "_____ ASSET MANAGEMENT",
        "answer": "UTI",
        "position": 5,
        "orientation": "down",
        "startx": 7,
        "starty": 1
    },
    {
        "clue": "2019 _____ MELLO YELLO DRAG RACING SERIES",
        "answer": "NHRA",
        "position": 6,
        "orientation": "down",
        "startx": 8,
        "starty": 1
    },
    {
        "clue": "brigandine",
        "answer": "BRIGANDINES",
        "position": 7,
        "orientation": "down",
        "startx": 9,
        "starty": 1
    },
    {
        "clue": "THE _____",
        "answer": "AUNTIES",
        "position": 8,
        "orientation": "down",
        "startx": 10,
        "starty": 1
    },
    {
        "clue": "_____ RACING",
        "answer": "GMS",
        "position": 9,
        "orientation": "down",
        "startx": 11,
        "starty": 1
    },
    {
        "clue": "LAURETTE _____-MCCOOK",
        "answer": "SPANG",
        "position": 13,
        "orientation": "down",
        "startx": 5,
        "starty": 3
    },
    {
        "clue": "Mystery",
        "answer": "PERYEAR",
        "position": 14,
        "orientation": "down",
        "startx": 6,
        "starty": 3
    },
    {
        "clue": "having reached the date at which payment is required ",
        "answer": "DUE",
        "position": 17,
        "orientation": "down",
        "startx": 1,
        "starty": 5
    },
    {
        "clue": "CARMENTA _____",
        "answer": "OGALALA",
        "position": 18,
        "orientation": "down",
        "startx": 2,
        "starty": 5
    },
    {
        "clue": "BRYAN _____",
        "answer": "STEIL",
        "position": 20,
        "orientation": "down",
        "startx": 7,
        "starty": 5
    },
    {
        "clue": "_____ CAFETERIAS",
        "answer": "MCL",
        "position": 22,
        "orientation": "down",
        "startx": 11,
        "starty": 5
    },
    {
        "clue": "MAOJINI _____",
        "answer": "ADOB",
        "position": 30,
        "orientation": "down",
        "startx": 4,
        "starty": 8
    },
    {
        "clue": "to trouble the mind of ",
        "answer": "AILS",
        "position": 32,
        "orientation": "down",
        "startx": 8,
        "starty": 8
    },
    {
        "clue": "being in a state of fitness for some experience or action ",
        "answer": "SET",
        "position": 33,
        "orientation": "down",
        "startx": 1,
        "starty": 9
    },
    {
        "clue": "_____ RATING SYSTEM",
        "answer": "ELO",
        "position": 34,
        "orientation": "down",
        "startx": 5,
        "starty": 9
    },
    {
        "clue": "galvanic_skin_response",
        "answer": "GSR",
        "position": 35,
        "orientation": "down",
        "startx": 10,
        "starty": 9
    },
    {
        "clue": "_____ INVESTMENTS COMPANY",
        "answer": "SEI",
        "position": 36,
        "orientation": "down",
        "startx": 11,
        "starty": 9
    }
]
	
		$('#puzzle-wrapper').crossword(puzzleData);
		
	})
	
})(jQuery)
