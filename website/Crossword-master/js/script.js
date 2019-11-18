// A javascript-enhanced crossword puzzle [c] Jesse Weisbeck, MIT/GPL 
(function($) {
	$(function() {
		// provide crossword entries in an array of objects like the following example
		// Position refers to the numerical order of an entry. Each position can have 
		// two entries: an across entry and a down entry
		var puzzleData = 
		[
    {
        "clue": "WINSOR _____",
        "answer": "MCCAY",
        "position": 1,
        "orientation": "across",
        "startx": 1,
        "starty": 1
    },
    {
        "clue": "3-HO-_____",
        "answer": "PCP",
        "position": 6,
        "orientation": "across",
        "startx": 8,
        "starty": 1
    },
    {
        "clue": "Mystery",
        "answer": "CROMES",
        "position": 9,
        "orientation": "across",
        "startx": 1,
        "starty": 2
    },
    {
        "clue": "___ ibn Abi Talib (Arabic: \u0639\u064e\u0644\u0650\u064a\u0651 \u0671\u0628\u0652\u0646 \u0623\u064e\u0628\u0650\u064a \u0637\u064e\u0627\u0644\u0650\u0628\u200e, \u02bfAl\u012by ibn \u02beAb\u012b \u1e6c\u0101lib; 13 September 601 \u2013 29 January 661) was the cousin and son-in-law of Muhammad, the last prophet of Islam",
        "answer": "ALI",
        "position": 11,
        "orientation": "across",
        "startx": 8,
        "starty": 2
    },
    {
        "clue": "Mystery",
        "answer": "DEMONWAYANS",
        "position": 12,
        "orientation": "across",
        "startx": 1,
        "starty": 3
    },
    {
        "clue": "_____ISM",
        "answer": "OMN",
        "position": 15,
        "orientation": "across",
        "startx": 2,
        "starty": 4
    },
    {
        "clue": "_____IA",
        "answer": "SLOVAK",
        "position": 16,
        "orientation": "across",
        "startx": 6,
        "starty": 4
    },
    {
        "clue": "_____ (DRINK)",
        "answer": "POG",
        "position": 17,
        "orientation": "across",
        "startx": 2,
        "starty": 5
    },
    {
        "clue": "___ is a genus of roughly 860 species of flowering plants in the family ___ceae",
        "answer": "ERICA",
        "position": 18,
        "orientation": "across",
        "startx": 7,
        "starty": 5
    },
    {
        "clue": "_____ JAE-HYUN",
        "answer": "AHN",
        "position": 19,
        "orientation": "across",
        "startx": 1,
        "starty": 6
    },
    {
        "clue": "Mystery",
        "answer": "EEW",
        "position": 20,
        "orientation": "across",
        "startx": 5,
        "starty": 6
    },
    {
        "clue": "_____\u2013CAUGHT MERGER",
        "answer": "COT",
        "position": 22,
        "orientation": "across",
        "startx": 9,
        "starty": 6
    },
    {
        "clue": "_____E",
        "answer": "TAMAL",
        "position": 23,
        "orientation": "across",
        "startx": 1,
        "starty": 7
    },
    {
        "clue": "_____S",
        "answer": "PUL",
        "position": 25,
        "orientation": "across",
        "startx": 8,
        "starty": 7
    },
    {
        "clue": "Mystery",
        "answer": "AGAPAI",
        "position": 26,
        "orientation": "across",
        "startx": 1,
        "starty": 8
    },
    {
        "clue": "AL-`_____",
        "answer": "ULA",
        "position": 28,
        "orientation": "across",
        "startx": 8,
        "starty": 8
    },
    {
        "clue": "___ \\rod-uh-muhn-TADE; roh-duh-muhn-TAHD\\ is a mass noun meaning boastful talk or behavior",
        "answer": "RODOMONTADE",
        "position": 29,
        "orientation": "across",
        "startx": 1,
        "starty": 9
    },
    {
        "clue": "Mystery",
        "answer": "UIE",
        "position": 32,
        "orientation": "across",
        "startx": 2,
        "starty": 10
    },
    {
        "clue": "THE _____S",
        "answer": "COTTAR",
        "position": 33,
        "orientation": "across",
        "startx": 6,
        "starty": 10
    },
    {
        "clue": "A RAM _____ _____",
        "answer": "SAM",
        "position": 34,
        "orientation": "across",
        "startx": 2,
        "starty": 11
    },
    {
        "clue": "the act or an instance of not having or being able to find ",
        "answer": "LOESS",
        "position": 35,
        "orientation": "across",
        "startx": 7,
        "starty": 11
    },
    {
        "clue": "_____ONALD'S",
        "answer": "MCD",
        "position": 1,
        "orientation": "down",
        "startx": 1,
        "starty": 1
    },
    {
        "clue": "Mystery",
        "answer": "CREOPHAGOUS",
        "position": 2,
        "orientation": "down",
        "startx": 2,
        "starty": 1
    },
    {
        "clue": "Mystery",
        "answer": "COMMONMADIA",
        "position": 3,
        "orientation": "down",
        "startx": 3,
        "starty": 1
    },
    {
        "clue": "in or into the middle of ",
        "answer": "AMONG",
        "position": 4,
        "orientation": "down",
        "startx": 4,
        "starty": 1
    },
    {
        "clue": "a strong wish for something ",
        "answer": "YEN",
        "position": 5,
        "orientation": "down",
        "startx": 5,
        "starty": 1
    },
    {
        "clue": "Mystery",
        "answer": "PAYOR",
        "position": 6,
        "orientation": "down",
        "startx": 8,
        "starty": 1
    },
    {
        "clue": "Mystery",
        "answer": "CLAVICULATE",
        "position": 7,
        "orientation": "down",
        "startx": 9,
        "starty": 1
    },
    {
        "clue": "Mystery",
        "answer": "PINACOLADAS",
        "position": 8,
        "orientation": "down",
        "startx": 10,
        "starty": 1
    },
    {
        "clue": "southwest",
        "answer": "SWS",
        "position": 10,
        "orientation": "down",
        "startx": 6,
        "starty": 2
    },
    {
        "clue": "Mystery",
        "answer": "ALEW",
        "position": 13,
        "orientation": "down",
        "startx": 7,
        "starty": 3
    },
    {
        "clue": "_____S",
        "answer": "SKAT",
        "position": 14,
        "orientation": "down",
        "startx": 11,
        "starty": 3
    },
    {
        "clue": "___ (; Avestan \ud802\udf01\ud802\udf19\ud802\udf00\ud802\udf2d \u0101tar) is the Zoroastrian concept of holy fire, sometimes described in abstract terms as \"burning and unburning fire\" or \"visible and invisible fire\" (Mirza, 1987:389)",
        "answer": "ATAR",
        "position": 19,
        "orientation": "down",
        "startx": 1,
        "starty": 6
    },
    {
        "clue": "___ (; ___ite: \ud808\udc79\ud808\udd2c\ud808\uddb7\ud808\udc76\ud808\udefe haltamti; Sumerian: \ud808\ude4f\ud808\ude20\ud808\udda0 NIM",
        "answer": "ELAM",
        "position": 20,
        "orientation": "down",
        "startx": 5,
        "starty": 6
    },
    {
        "clue": "a large hoofed domestic animal that is used for carrying or drawing loads and for riding ",
        "answer": "E",
        "position": 21,
        "orientation": "down",
        "startx": 6,
        "starty": 6
    },
    {
        "clue": "Mystery",
        "answer": "APOEM",
        "position": 24,
        "orientation": "down",
        "startx": 4,
        "starty": 7
    },
    {
        "clue": "to arrange something in a certain spot or position ",
        "answer": "PUTTO",
        "position": 25,
        "orientation": "down",
        "startx": 8,
        "starty": 7
    },
    {
        "clue": "_____ (DISAMBIGUATION)",
        "answer": "IOC",
        "position": 27,
        "orientation": "down",
        "startx": 6,
        "starty": 8
    },
    {
        "clue": "LON _____",
        "answer": "NOL",
        "position": 30,
        "orientation": "down",
        "startx": 7,
        "starty": 9
    },
    {
        "clue": "SAN FRANCISCO 49_____",
        "answer": "ERS",
        "position": 31,
        "orientation": "down",
        "startx": 11,
        "starty": 9
    }
]
	
		$('#puzzle-wrapper').crossword(puzzleData);
		
	})
	
})(jQuery)
