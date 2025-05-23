# -*- coding: utf-8 -*-
#
#   Copyright 2006,2009,2011 Steve Stavropoulos <steve@math.upatras.gr>
#
#   This file is part of Flexy.
#
#   Flexy is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   Flexy is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Flexy.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import sys, re, string
from utils import *

def translate(alist, word):
	for what in alist:
		word = word.replace(what['from'], what['to'])
	return word

def translateback(alist, word):
	for what in alist:
		word = word.replace(what['to'], what['from'])
	return word

wordencoding = [
	{'from': 'αί', 'to': 'a'},
	{'from': 'ού', 'to': 'b'},
	{'from': 'εί', 'to': 'c'},
	{'from': 'οί', 'to': 'd'},
	{'from': 'εύ', 'to': 'e'},
	{'from': 'αύ', 'to': 'f'},

	{'from': 'αι', 'to': 'n'},
	{'from': 'ου', 'to': 'o'},
	{'from': 'ει', 'to': 'p'},
	{'from': 'οι', 'to': 'q'},
	{'from': 'ευ', 'to': 'r'},
	{'from': 'αυ', 'to': 's'},
]

# Convert capital letters to lowercase and back
for letter in 'ΆΈΉΎΊΌΏΑΕΗΥΙΟΩ':
	wordencoding.append({'from': letter, 'to': letter.lower() + '_'})

tonismenafwnhenta = 'abcdefάέήύίόώΐΰ';
atonafwnhenta = 'nopqrsαεηυιοωϊϋ';
fwnhenta = tonismenafwnhenta + atonafwnhenta;
# We add x, y, z, for use by the rules. _ is a marker for capital letter
symfwna = 'βγδζθκλμνξπρστφχψxyz_';

tonismenofwnhen = '[' + tonismenafwnhenta + ']'
atonofwnhen = '[' + atonafwnhenta + ']'
fwnhen = '[' + fwnhenta + ']'
symfwno = '[' + symfwna + ']'

def preaction(word):
	return translate(wordencoding, word)

def postaction(word):
	return translateback(wordencoding, word)

def transfertonosdown(word):
	return _transfertonos(word, 'down')

def transfertonosdowntwice(word):
	word = transfertonosdown(word)
	return transfertonosdown(word)

def transfertonosup(word):
	return _transfertonos(word, 'up')

def _transfertonos(word, direction):
	expression = '^(.*)(%s)(%s*)(%s)(.*)$'
	if direction == 'down':
		expression = expression % (tonismenofwnhen, symfwno, atonofwnhen)
	elif direction == 'up':
		expression = expression % (atonofwnhen, symfwno, tonismenofwnhen)
	else:
		return word
	symplegmare = re.compile(expression);
	symplegma = symplegmare.match(word)
	if symplegma:
		if direction == 'down':
			paliostonos = tr(tonismenafwnhenta, atonafwnhenta, symplegma.group(2))
			neostonos = tr(atonafwnhenta, tonismenafwnhenta, symplegma.group(4))
			return symplegma.group(1) + paliostonos + symplegma.group(3) + neostonos + symplegma.group(5)
		else:
			paliostonos = tr(tonismenafwnhenta, atonafwnhenta, symplegma.group(4))
			neostonos = tr(atonafwnhenta, tonismenafwnhenta, symplegma.group(2))
			return symplegma.group(1) + neostonos + symplegma.group(3) + paliostonos + symplegma.group(5)
	else:
		if direction == 'up':
			expression = '^%s+%s' % (symfwno, tonismenofwnhen)
			symplegmare = re.compile(expression);
			symplegma = symplegmare.match(word)
			if symplegma:
				return _transfertonos('ε' + word, direction)
		print('Could not detect ascent in %s (original: %s)' % (word, postaction(word)), file=sys.stderr)
		return word # No match, no accent, do nothing more

# Αφαιρεί τον πρώτο τόνο όταν υπάρχουν δύο
def deletefirsttonos(word):
	symplegmare = re.compile('^(.*)(%s)(.*%s.*)$' % (tonismenofwnhen, tonismenofwnhen));
	symplegma = symplegmare.match(word)
	if symplegma:
		notonos = tr(tonismenafwnhenta, atonafwnhenta, symplegma.group(2))
		return symplegma.group(1) + notonos + symplegma.group(3)
	else:
		return word # No match, do nothing more

rules = {}
# αχταρμάς
rules['O1nop'] = {
	'match': 'άς$',
	'actions':
		[
		{
			'replace': 'άς',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ά',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		]
}
rules['O1p'] =  {
	'match': 'άς$',
	'actions':
		[
		{
			'replace': 'άδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'άδων',
			'restype': 'OusPlGen',
		},
		]
}
# αυγουλάς, ανανάς
rules['O1'] =  {
	'match': 'άς$',
	'actions': rules['O1nop']['actions'] + rules['O1p']['actions']
}
# παπατρέχας, Ποσειδώνας
rules['O2nop'] = {
	'match': 'ας$',
	'actions':
		[
		{
			'replace': 'ας',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'α',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		]
}
# καπιτάλας, μάγκας
rules['O2nopgen'] = {
	'match': 'ας$',
	'actions': rules['O2nop']['actions'] +
		[
		{
			'replace': 'ες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		]
}
# αιώνας
rules['O2'] = {
	'match': 'ας$',
	'actions': rules['O2nopgen']['actions'] + 
		[
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
		},
		]
}
# Ποσειδώνας, βήχας, γιόκας
rules['O3nop'] = {
	'match': 'ας$',
	'actions': rules['O2nop']['actions'],
}
# ασχημάντρας, γεροξούρας, μάπας
rules['O3nopgen'] = {
	'match': 'ας$',
	'actions': rules['O2nopgen']['actions'],
}
# κανάγιας, τυχεράκιας, αέρας
rules['O3ides'] = {
	'match': 'ας$',
	'actions': rules['O3nop']['actions'] + 
		[
		{
			'search': fwnhen + '*' + 'ας$',
			'replace': 'ηδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'search': fwnhen + '*' + 'ας$',
			'replace': 'ηδων',
			'restype': 'OusPlGen',
		},
		]
}
# βόας, γαλαξίας
rules['O3'] = {
	'match': 'ας$',
	'actions': rules['O3nopgen']['actions'] +
		[
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# αρχιδούκας, δούκας, μήνας, πόδας
rules['O3a'] = {
	'match': rules['O3']['match'],
	'actions': rules['O3']['actions'] +
		[
		{
			'replace': 'ος',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		]
}
# μπόγιας, μουστάκιας
rules['O4nop'] = {
	'match': 'ας$',
	'actions': rules['O2nop']['actions'],
}
# πρεζάκιας, ρήγας
rules['O4ides'] = {
	'match': 'ας$',
	'actions': rules['O3ides']['actions']
}
# κάλφας, μπάρμπας
rules['O4'] = {
	'match': 'ας$',
	'actions': rules['O4nop']['actions'] + 
		[
		{
			'replace': 'αδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'αδων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# αντίπαπας, γαϊδουρόβηχας, κάπελας
rules['O5nop'] = {
	'match': 'ας$',
	'actions': rules['O2nop']['actions'],
}
# αλητάμπουρας, άντρακλας, δράκουλας
rules['O5nopgen'] = {
	'match': 'ας$',
	'actions': rules['O2nopgen']['actions'],
}
# ακτήμονας, άμβωνας
rules['O5'] = {
	'match': 'ας$',
	'actions': rules['O2nop']['actions'] +
		[
		{
			'replace': 'ες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# γίγας, γίγαντας, άτλας, άτλαντας, ελέφας,
# έρπης, έρπητας, γόης, γόητας
rules['O5a'] = {
0:
	{
		'match': '[^(αντ)]ας$',
		'search': 'ας$',
		'actions': rules['O2nop']['actions'] +
			[
			{
				'replace': 'αντες',
				'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			},
			{
				'replace': 'αντων',
				'restype': 'OusPlGen',
				'callfunc': transfertonosdown,
			},
			]
	},
1:
	{
		'match': 'αντας$',
		'search': 'ας$',
		'actions': rules['O2nop']['actions'] +
			[
			{
				'replace': 'ες',
				'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			},
			{
				'replace': 'ων',
				'restype': 'OusPlGen',
				'callfunc': transfertonosdown,
			},
			]
	},
2:
	{
		'match': 'ης$',
		'actions':
			[
			{
				'replace': 'ης',
				'restype': 'OusEnOnom',
			},
			{
				'replace': 'η',
				'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
			},
			{
				'replace': 'ητες',
				'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			},
			{
				'replace': 'ητων',
				'restype': 'OusPlGen',
				'callfunc': transfertonosdown,
			},
			]
	},
3:
	{
		'match': 'ητας$',
		'search': 'ας$',
		'actions': rules['O2nop']['actions'] +
			[
			{
				'replace': 'ες',
				'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			},
			{
				'replace': 'ων',
				'restype': 'OusPlGen',
				'callfunc': transfertonosdown,
			},
			]
	},
}
# τσέλιγκας, δέσποτας, δερβέναγας
rules['O6'] = {
	'match': 'ας$',
	'actions': rules['O2nop']['actions'] +
		[
		{
			'replace': 'αδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': 'αδων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdowntwice,
		},
		]
}
# Ερμής
rules['O7nop'] = {
	'match': 'ής$',
	'actions':
		[
		{
			'replace': 'ής',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ή',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		]
}
# νικητής, δωρητής, εξεταστής
rules['O7'] = {
	'match': 'ής$',
	'actions': rules['O7nop']['actions'] +
		[
		{
			'replace': 'ές',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'OusPlGen',
		},
		]
}
# γανωματής, ατζαμής, μουστακαλής, χατζής
rules['O8'] = {
	'match': 'ής$',
	'actions': rules['O7nop']['actions'] +
		[
		{
			'replace': 'ήδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ήδων',
			'restype': 'OusPlGen',
		},
		]
}
# βουτηχτής, πραματευτής, δουλευτής
rules['O9'] = {
	'match': 'ής$',
	'actions': rules['O7nop']['actions'] +
		[
		{
			'replace': 'ές',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'OusPlGen',
		},
		{
			'replace': 'άδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'άδων',
			'restype': 'OusPlGen',
		},
		]
}
# πλάστης, Άδης, Άρης
rules['O10nop'] = {
	'match': 'ης$',
	'actions':
		[
		{
			'replace': 'ης',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'η',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		]
}
# ναύτης, αγύρτης, αιμοδότης
rules['O10'] = {
	'match': 'ης$',
	'actions': rules['O10nop']['actions'] +
		[
		{
			'replace': 'ες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# κοσμάκης
rules['O11nop'] = {
	'match': 'ης$',
	'actions': rules['O10nop']['actions']
}
# γεροξούρας
rules['O11nopgen'] = {
	'match': 'ης$',
	'actions': rules['O10nop']['actions'] +
		[
		{
			'replace': 'ηδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		]
}
# μανάβης, εαυτούλης, φακίρης
rules['O11'] = {
	'match': 'ης$',
	'actions': rules['O11nopgen']['actions'] +
		[
		{
			'replace': 'ηδων',
			'restype': 'OusPlGen',
		},
		]
}
# τέντζερης
rules['O12nop'] = {
	'match': 'ης$',
	'actions': rules['O10nop']['actions']
}
# φούρναρης, μάστορης 
rules['O12'] = {
	'match': 'ης$',
	'actions': rules['O10nop']['actions'] +
		[
		{
			'replace': 'ηδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ηδων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# καφές, φερετζές, κεφτές
rules['O13'] = {
	'match': 'ές$',
	'actions':
		[
		{
			'replace': 'ές',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'έ',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'έδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'έδων',
			'restype': 'OusPlGen',
		},
		]
}
# τάδες
rules['O14nop'] = {
	'match': 'ες$',
	'actions':
		[
		{
			'replace': 'ες',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ε',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		]
}
# κόντες, λεβάντες
rules['O14'] = {
	'match': 'ες$',
	'actions': rules['O14nop']['actions'] +
		[
		{
			'replace': 'ηδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ηδων',
			'restype': 'OusPlGen',
		},
		]
}
# παππούς
rules['O15'] = {
	'match': 'ούς$',
	'actions':
		[
		{
			'replace': 'ούς',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ού',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ούδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ούδων',
			'restype': 'OusPlGen',
		},
		]
}
# νους, πλους, ρους
rules['O15a'] = {
	'match': 'ους$',
	'actions':
		[
		{
			'replace': 'ους',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ου',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		# special case: πλους
		{
			'match': '^πλους$',
			'search': 'πλους',
			'replace': 'πλόες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'match': '^πλους$',
			'search': 'πλους',
			'replace': 'πλοών',
			'restype': 'OusPlGen',
		},
		]
}
# περίπλους, διάπλους, προπάππους, απόπλους
rules['O16'] = {
	'match': 'ους$',
	'actions':
		[
		{
			'replace': 'ους',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ου',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'οι',
			'restype': ['OusPlOnom', 'OusPlKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'OusPlAit',
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
		},
		]
}
# εγκεφαλισμός, Oυρανός, οχαδερφισμός 
rules['O17nop'] = {
	'match': 'ός$',
	'actions':
		[
		{
			'replace': 'ός',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ού',
			'restype': 'OusEnGen',
		},
		{
			'replace': 'ό',
			'restype': 'OusEnAit',
		},
		{
			'replace': 'έ',
			'restype': 'OusEnKlit',
		},
		]
}
# ουρανός, αδερφός, ανιψιός, ωφελιμισμός
rules['O17'] = {
	'match': 'ός$',
	'actions': rules['O17nop']['actions'] +
		[
		{
			'replace': 'οί',
			'restype': ['OusPlOnom', 'OusPlKlit'],
		},
		{
			'replace': 'ούς',
			'restype': 'OusPlAit',
		},
		{
			'replace': 'ών',
			'restype': 'OusPlGen',
		},
		]
}
# O18: κατάληξη ος, τονίζονται στην παραλήγουσα
rules['O18nopnok'] = {
	'match': 'ος$',
	'actions':
		[
		{
			'replace': 'ος',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
		},
		{
			'replace': 'ο',
			'restype': 'OusEnAit',
		},
		]
}
# όχλος, νότος, σάλος
rules['O18nop'] = {
	'match': 'ος$',
	'actions': rules['O18nopnok']['actions'] +
		[
		{
			'replace': 'ε',
			'restype': 'OusEnKlit',
		},
		]
}
rules['O18plu'] = {
	'match': 'ος$',
	'actions':
		[
		{
			'replace': 'οι',
			'restype': ['OusPlOnom', 'OusPlKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'OusPlAit',
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
		},
		]
}
# δρόμος, ανθρωπολόγος, βιρτουόζος
rules['O18'] = {
	'match': 'ος$',
	'actions': rules['O18nop']['actions'] + rules['O18plu']['actions']
}
# O18anop: ίδια με Ο18, αλλά στην κλιτική λήγουν σε ο αντί για ε
rules['O18anop'] = {
	'match': 'ος$',
	'actions': rules['O18nopnok']['actions'] +
		[
		{
			'replace': 'ο',
			'restype': 'OusEnKlit',
		},
		]
}
# γέρος, μαέστρος, μπουλούκος 
rules['O18a'] = {
	'match': 'ος$',
	'actions': rules['O18anop']['actions'] + rules['O18plu']['actions']
}
# ίδια με Ο18, αλλά τονίζονται στην προπαραλήγουσα και αλλάζει ο τόνος 
rules['O19nop'] = {
	'match': 'ος$',
	'actions':
		[
		{
			'replace': 'ος',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ο',
			'restype': 'OusEnAit',
		},
		{
			'replace': 'ε',
			'restype': 'OusEnKlit',
		},
		]
}
# άγγελος, διάδικος, διάδρομος, κατάλογος
rules['O19'] = {
	'match': 'ος$',
	'actions': rules['O19nop']['actions'] +
		[
		{
			'replace': 'οι',
			'restype': ['OusPlOnom', 'OusPlKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'OusPlAit',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O20: ίδια με Ο18, αλλά τονίζονται στην προπαραλήγουσα
rules['O20nop'] = rules['O18nop']
rules['O20'] = rules['O18']
# O20a: ίδια με O20, αλλά μπορεί να γίνει και μεταφορά τόνου
# ψευδάργυρος
rules['O20anop'] = {
	'match': 'ος$',
	'actions': rules['O20nop']['actions'] +
		[
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		]
}
# πρόμαχος, πρόξενος, πτέραρχος
rules['O20a'] = {
	'match': 'ος$',
	'actions': rules['O20anop']['actions'] + rules['O18plu']['actions'] +
		[
		{
			'replace': 'ους',
			'restype': 'OusPlAit',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O21: κατάληξη σε έας
# Mορφέας
rules['O21nop'] = {
	'match': 'έας$',
	'actions':
		[
		{
			'replace': 'έας',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'έα',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		]
}
# δεκανέας, ιππέας (όχι ιππείς), φονέας, φορέας
rules['O21'] = {
	'match': 'έας$',
	'actions': rules['O21nop']['actions'] +
		[
		{
			'replace': 'είς',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'έων',
			'restype': 'OusPlGen',
		},
		]
}
# O22: κατάληξη σε ής
# Ηρακλής
rules['O22nop'] = {
	'match': 'ής$',
	'actions':
		[
		{
			'replace': 'ής',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ή',
			'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
		},
		]
}
# ευγενής, ιθαγενής, συγγενής
rules['O22'] = {
	'match': 'ής$',
	'actions': rules['O22nop']['actions'] +
		[
		{
			'replace': 'είς',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'OusPlGen',
		},
		]
}
# O23: κατάληξη σε ά, πληθυντικός σε άδες
# Xαλιμά
rules['O23nop'] = {
	'match': 'ά$',
	'actions':
		[
		{
			'replace': 'ά',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'άς',
			'restype': 'OusEnGen',
		},
		]
}
# μαμά, νταντά, τσατσά, οκά
rules['O23'] = {
	'match': 'ά$',
	'actions': rules['O23nop']['actions'] +
		[
		{
			'replace': 'άδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'άδων',
			'restype': 'OusPlGen',
		},
		]
}
# O24: κατάληξη σε ιά, πληθυντικός σε ές
# αραπιά, βλαχιά, ξηρά
rules['O24nop'] = {
	'match': 'ιά$',
	'search': 'ά$',
	'actions': rules['O23nop']['actions']
}
# καρδιά, απανεμιά, απονιά, αραπιά
rules['O24'] = {
	'match': 'ιά$',
	'search': 'ά$',
	'actions': rules['O24nop']['actions'] +
		[
		{
			'replace': 'ές',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'OusPlGen',
		},
		]
}
# O25: κατάληξη σε α, κατεβάζει τόνο σε Αιτιατική Πληθυντικού
# αντιβία, ενδοεπικοινωνία, κάρμα
rules['O25nop'] = {
	'match': 'α$',
	'actions': 
		[
		{
			'replace': 'α',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ας',
			'restype': 'OusEnGen',
		},
		]
}
# ευφυΐα
rules['O25anop'] = rules['O25nop']
# O25a: ίδια με O25, αλλά δεν έχει Αιτιατική Πληθυντικού
rules['O25a'] = {
	'match': 'α$',
	'actions': rules['O25anop']['actions'] +
		[
		{
			'replace': 'ες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		]
}
# ακινησία, ώρα, ακολουθία
rules['O25'] = {
	'match': 'α$',
	'actions': rules['O25a']['actions'] +
		[
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O26: ίδιο με O25 αλλά δεν κατεβάζει τόνο σε Αιτιατική Πληθυντικού
# μητέρα, επικεφαλίδα, ζωστήρα, θαμπάδα
rules['O26'] = {
	'match': 'α$',
	'actions': rules['O25a']['actions'] +
		[
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
		},
		]
}
# O27: ίδιο με O25, αλλά κατεβάζει δύο συλλαβές τόνο σε Αιτιατική Πληθυντικού
# εξώσφαιρα, ενάργεια, εγωπάθεια
rules['O27nop'] = rules['O25nop']
# θάλασσα, γέφυρα, δέσποινα, διάνοια
rules['O27'] = {
	'match': 'α$',
	'actions': rules['O25a']['actions'] +
		[
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdowntwice,
		},
		]
}
# O27a: ίδιο με O25a
# 
rules['O27anop'] = rules['O25anop']
# πέστροφα, φραγκόκοτα, χορτόπιτα, ψαρόσουπα
rules['O27a'] = rules['O25a']
# O28: ίδιο με O25
# 
rules['O28nop'] = rules['O25nop']
# σάλπιγγα, γονιμότητα, δυνατότητα
rules['O28'] = rules['O25']
# O29α: κατάληξη σε ή, χωρίς γενική πληθυντικού
# Χωρίς χρήση μάλλον...
rules['O29anop'] = {
	'match': 'ή$',
	'actions':
		[
		{
			'replace': 'ή',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ής',
			'restype': 'OusEnGen',
		},
		]
}
# υπακοή, ζωγραφική, προσμονή, προσοχή
rules['O29a'] = {
	'match': 'ή$',
	'actions': rules['O29anop']['actions'] +
		[
		{
			'replace': 'ές',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		]
}
# O29: κατάληξη σε ή, με γενική πληθυντικού
# αθλητιατρική, φυγή, γη, οργή
rules['O29nop'] = rules['O29anop']
# ψυχή, διαγωγή, διαλογή, ωδή, φωνή
rules['O29'] = {
	'match': 'ή$',
	'actions': rules['O29a']['actions'] +
		[
		{
			'replace': 'ών',
			'restype': 'OusPlGen',
		},
		]
}
# O30a: κατάληξη σε η, χωρίς γενική πληθυντικού
# Χωρίς χρήση μάλλον...
rules['O30anop'] = {
	'match': 'η$',
	'actions':
		[
		{
			'replace': 'η',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ης',
			'restype': 'OusEnGen',
		},
		]
}
# αγάπη, βιασύνη, ήβη, κήλη, μύτη
rules['O30a'] = {
	'match': 'η$',
	'actions': rules['O30anop']['actions'] +
		[
		{
			'replace': 'ες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		]
}
# O30: κατάληξη σε η, με γενική πληθυντικού
# αίγλη, ειρήνη, εξοχοτάτη, μέθη, ειρήνη
rules['O30nop'] = rules['O30anop']
# βαζελίνη, βενζίνη, γνώμη, ζελατίνη
rules['O30'] = {
	'match': 'η$',
	'actions': rules['O30a']['actions'] +
		[
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O31: 	κατάληξη σε η, χωρίς να κατεβάζει τόνο σε γενική πληθυντικού και
#	με έξτρα μορφή σε εως σε γενική ενικού
# πλάση, Πόλη, ζέση
rules['O31nop'] = {
	'match': 'η$',
	'actions': rules['O30anop']['actions'] +
		[
		{
			'replace': 'εως',
			'restype': 'OusEnGen',
		},
		]
}
# σκέψη, θρέψη, καύση, κλάση
rules['O31'] = {
	'match': 'η$',
	'actions': rules['O31nop']['actions'] +
		[
		{
			'replace': 'εις',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'εων',
			'restype': 'OusPlGen',
		},
		]
}
# Ίδιο με O30a, αλλά τονίζονται στην προπαραλήγουσα αντί για την παραλήγουσα
rules['O32nop'] = rules['O30anop']
rules['O32'] = rules['O30a']
# Ίδιο με O30anop
rules['O32a'] = rules['O30anop']
# O33: 	Ίδιο με O30a αλλά κατεβάζει τόνο σε όλο τον πληθυντικό και έξτρα μορφή
#	σε εως με κατέβασμα τόνου σε γενική ενικού
# διανόηση, μόρφωση, προΰπαρξη 
rules['O33nop'] = {
	'match': 'η$',
	'actions': rules['O30anop']['actions'] +
		[
		{
			'replace': 'εως',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		]
}
# άθληση, αιώρηση, ώθηση, φώτιση
rules['O33'] = {
	'match': 'η$',
	'actions': rules['O33nop']['actions'] +
		[
		{
			'replace': 'εις',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O34: κατάληξη σε ός
# Ίσως χωρίς χρήση
rules['O34nop'] = {
	'match': 'ός$',
	'actions':
		[
		{
			'replace': 'ός',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ού',
			'restype': 'OusEnGen',
		},
		{
			'replace': 'ό',
			'restype': ['OusEnAit', 'OusEnKlit'],
		},
		]
}
# οδός, δοκός, τροφός
rules['O34'] = {
	'match': 'ός$',
	'actions': rules['O34nop']['actions'] +
		[
		{
			'replace': 'οί',
			'restype': ['OusPlOnom', 'OusPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'OusPlGen',
		},
		{
			'replace': 'ούς',
			'restype': 'OusPlAit',
		},
		]
}
# O35: κατάληξη σε ος
# βίβλος, Βίβλος, Ρόδος
rules['O35nop'] = {
	'match': 'ος$',
	'actions':
		[
		{
			'replace': 'ος',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
		},
		{
			'replace': 'ο',
			'restype': ['OusEnAit', 'OusEnKlit'],
		},
		]
}
# διχοτόμος, λέμφος, λίθος, νόσος, παρθένος
rules['O35'] = {
	'match': 'ος$',
	'actions': rules['O35nop']['actions'] +
		[
		{
			'replace': 'οι',
			'restype': ['OusPlOnom', 'OusPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
		},
		{
			'replace': 'ους',
			'restype': 'OusPlAit',
		},
		]
}
# O36: κατάληξη σε ος, κατεβάζει τόνο
# Ίσως χωρίς χρήση...
rules['O36nop'] = {
	'match': 'ος$',
	'actions':
		[
		{
			'replace': 'ος',
			'restype': 'OusEnOnom',
		},
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ο',
			'restype': ['OusEnAit', 'OusEnKlit'],
		},
		]
}
# εγκύκλιος, διάλεκτος, διέξοδος, ήπειρος, κάθετος, υφήλιος
rules['O36'] = {
	'match': 'ος$',
	'actions': rules['O36nop']['actions'] +
		[
		{
			'replace': 'οι',
			'restype': ['OusPlOnom', 'OusPlKlit'],
		},
		{
			'replace': 'ες',
			'restype': ['OusPlOnom', 'OusPlAit'],
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ους',
			'restype': 'OusPlAit',
			'callfunc': transfertonosdown,
		},
		]
}
# O37: κατάληξη σε ού, πληθυντικός σε ούδες
# Ίσως χωρίς χρήση
rules['O37nop'] = {
	'match': 'ού$',
	'actions':
		[
		{
			'replace': 'ού',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ούς',
			'restype': 'OusEnGen',
		},
		]
}
# αλεπού, βιζιτού, καφετζού, μπουμπού
rules['O37'] = {
	'match': 'ού$',
	'actions': rules['O37nop']['actions'] +
		[
		{
			'replace': 'ούδες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ούδων',
			'restype': 'OusPlGen',
		},
		]
}
# O37a: κατάληξη σε ω, πληθυντικός σε ες
# μουρλέγκω, μπάμπω, τρελέγκω
rules['O37anop'] = {
	'match': 'ω$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ως',
			'restype': 'OusEnGen',
		},
		]
}
# βάβω, τσουράπω, χαρχάλω
rules['O37a'] = {
	'match': 'ω$',
	'actions': rules['O37anop']['actions'] +
		[
		{
			'replace': 'ες',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
		},
		]
}
# O37b: κατάληξη σε ώ, χωρίς πληθυντικό και με έξτρα μορφή σε γενική ενικού
# ηχώ
rules['O37b'] = {
	'match': 'ώ$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ούς',
			'restype': 'OusEnGen',
		},
		{
			'replace': 'ώς',
			'restype': 'OusEnGen',
		},
		]
}
# O38: κατάληξη σε ό, πληθυντικός σε ά
# καθισιό, κοινό, ηθικό
rules['O38nop'] = {
	'match': 'ό$',
	'actions':
		[
		{
			'replace': 'ό',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ού',
			'restype': 'OusEnGen',
		},
		]
}
# βουνό, αλλαντικό, γλυκό, γραφτό, ωό
rules['O38'] = {
	'match': 'ό$',
	'actions': rules['O38nop']['actions'] +
		[
		{
			'replace': 'ά',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'OusPlGen',
		},
		]
}
# O39: κατάληξη σε ο, πληθυντικός σε α
# αντήλιο, κουμάντο, πασατέμπο
rules['O39nop'] = {
	'match': 'ο$',
	'actions':
		[
		{
			'replace': 'ο',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
		},
		]
}
# επουράνια
rules['O39nopgen'] = {
	'match': 'ο$',
	'actions': rules['O39nop']['actions'] +
		[
		{
			'replace': 'α',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		]
}
# πεύκο, μεταλλείο, μοτίβο, ψώνιο
rules['O39'] = {
	'match': 'ο$',
	'actions': rules['O39nopgen']['actions'] +
		[
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
		},
		]
}
# O40: κατάληξη σε ο, πληθυντικός σε α, κατεβάζει τόνο σε γενική
# χλώριο, ραδόνιο, νάτριο, κάλιο
rules['O40nop'] = {
	'match': 'ο$',
	'actions':
		[
		{
			'replace': 'ο',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		]
}
# πρόσωπο, ραδιόφωνο, σκάνδαλο, σκιάδιο, ωράριο
rules['O40'] = {
	'match': 'ο$',
	'actions': rules['O40nop']['actions'] +
		[
		{
			'replace': 'α',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O41: κατάληξη σε ο, πληθυντικός σε α, δεν κατεβάζει τόνο σε γενική
# καταχείμωνο, μεσοβδόμαδο, κατακαλόκαιρο
rules['O41nop'] = {
	'match': 'ο$',
	'actions':
		[
		{
			'replace': 'ο',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
		},
		]
}
# φώσφορο, σίδερο, αμαξάδικο, άμφιο
rules['O41'] = {
	'match': 'ο$',
	'actions': rules['O41nop']['actions'] +
		[
		{
			'replace': 'α',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
		},
		]
}
# O42: ίδιο με O41, αλλά μπορεί να κατεβάσει τόνο σε γενική
# αγουρέλαιο
rules['O42nop'] = {
	'match': 'ο$',
	'actions': rules['O41nop']['actions'] +
		[
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		]
}
# βούτυρο, αυτόματο, άχυρο, βότανο, τρίκυκλο
rules['O42'] = {
	'match': 'ο$',
	'actions': rules['O41']['actions'] +
		[
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O43: κατάληξη σε ί, πληθυντικός σε ά, δεν κατεβάζει τόνο σε γενική
# στρατί, τζιτζί
rules['O43nop'] = {
	'match': 'ί$',
	'actions':
		[
		{
			'replace': 'ί',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ιού',
			'restype': 'OusEnGen',
		},
		]
}
# ασκί, παιδί, βρακί, ψωμί, σπυρί, σπαθί
rules['O43'] = {
	'match': 'ί$',
	'actions': rules['O43nop']['actions'] +
		[
		{
			'replace': 'ιά',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ιών',
			'restype': 'OusPlGen',
		},
		]
}
# O44a: κατάληξη σε ι, δεν έχει γενική
# 
rules['O44anop'] = {
	'match': 'ι$',
	'actions':
		[
		{
			'replace': 'ι',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		]
}
# αρνάκι, τόπι, τροπάρι, πρεζάκι, πούλι 
rules['O44a'] = {
	'match': 'ι$',
	'actions': rules['O44anop']['actions'] +
		[
		{
			'replace': 'ια',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		]
}
# O44: κατάληξη σε ι, κατεβάζει τόνο σε γενική
# ασβέστι, μούσκλο, θειάφι 
rules['O44nop'] = {
	'match': 'ι$',
	'actions': rules['O44anop']['actions'] +
		[
		{
			'replace': 'ιού',
			'restype': 'OusEnGen',
			'callfunc': deletefirsttonos,
		},
		]
}
# τραγούδι, βόδι, βόιδι (!), γρανάζι, δελφίνι
rules['O44'] = {
	'match': 'ι$',
	'actions': rules['O44nop']['actions'] +
		[
		{
			'replace': 'ια',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ιών',
			'restype': 'OusPlGen',
			'callfunc': deletefirsttonos,
		},
		]
}
# O45: κατάληξη σε ι, πληθυντικός σε άγια
# 
rules['O45nop'] = {
	'match': 'ι$',
	'actions':
		[
		{
			'replace': 'ι',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'γιού',
			'restype': 'OusEnGen',
			'callfunc': deletefirsttonos,
		},
		]
}
# τσάι, κατώι, καλάι, μπόι, ρολόι
rules['O45'] = {
	'match': 'ι$',
	'actions': rules['O45nop']['actions'] +
		[
		{
			'replace': 'για',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'γιών',
			'restype': 'OusPlGen',
			'callfunc': deletefirsttonos,
		},
		]
}
# O46a: κατάληξη σε ος, πληθυντικός σε η, χωρίς γενική πληθυντικού
# 
rules['O46anop'] = {
	'match': 'ος$',
	'actions':
		[
		{
			'replace': 'ος',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'OusEnGen',
		},
		]
}
# μίσος, θάμπος, θάρρος, άγχος, σκότος
rules['O46a'] = {
	'match': 'ος$',
	'actions': rules['O46anop']['actions'] +
		[
		{
			'replace': 'η',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		]
}
# O46: ίδιο με O46a, αλλά και με γενική πληθυντικού
# ψύχος
rules['O46nop'] = rules['O46anop']
# γένος, μέρος, έπος, νέφος, πέλος
rules['O46'] = {
	'match': 'ος$',
	'actions': rules['O46a']['actions'] +
		[
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O46b: ίδιο με O46, αλλά χωρίς πληθυντικό
# ψύχος
rules['O46b'] = rules['O46nop']
# O47: κατάληξη σε ος, πληθυντικός σε η, κατεβάζει τόνο
# όνειδος
rules['O47nop'] = {
	'match': 'ος$',
	'actions':
		[
		{
			'replace': 'ος',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		]
}
# έδαφος, όφελος, κέλυφος, έλεος, έρεβος
rules['O47'] = {
	'match': 'ος$',
	'actions': rules['O47nop']['actions'] +
		[
		{
			'replace': 'η',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdowntwice,
		},
		]
}
# O48: κατάληξη σε α, πληθυντικός σε ατα
# 
rules['O48nop'] = {
	'match': 'α$',
	'actions':
		[
		{
			'replace': 'α',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ατος',
			'restype': 'OusEnGen',
		},
		]
}
# κύμα, αίμα, άρμα, βήμα, κλίμα, πνεύμα
rules['O48'] = {
	'match': 'α$',
	'actions': rules['O48nop']['actions'] +
		[
		{
			'replace': 'ατα',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ατων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O49: κατάληξη σε α, πληθυντικός σε ατα, κατεβάζει τόνο
# καστανόχωμα
rules['O49nop'] = {
	'match': 'α$',
	'actions':
		[
		{
			'replace': 'α',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ατος',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		]
}
# όνομα, αλάτισμα, άλλαγμα, χρέωμα, χούφτωμα
rules['O49'] = {
	'match': 'α$',
	'actions': rules['O49nop']['actions'] +
		[
		{
			'replace': 'ατα',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ατων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdowntwice,
		},
		]
}
# O50: κατάληξη σε ο, πληθυντικός σε ατα, κατεβάζει τόνο
# 
rules['O50nop'] = {
	'match': 'ο$',
	'actions':
		[
		{
			'replace': 'ο',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ατος',
			'restype': 'OusEnGen',
			'callfunc': transfertonosdown,
		},
		]
}
# γράψιμο, βάψιμο, βήξιμο, βράσιμο, βρέξιμο, κράξιμο, ντύσιμο
rules['O50'] = {
	'match': 'ο$',
	'actions': rules['O50nop']['actions'] +
		[
		{
			'replace': 'ατα',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ατων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdowntwice,
		},
		]
}
# O51: κατάληξη σε ας, πληθυντικός σε ατα, κατεβάζει τόνο σε γεν. πληθυντικού
# γήρας, ημίφως
rules['O51nop'] = {
	'match': 'ας$',
	'actions':
		[
		{
			'replace': 'ας',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'ατος',
			'restype': 'OusEnGen',
		},
		]
}
# κρέας, δέρας, κέρας, τέρας, άλας
rules['O51'] = {
	'match': 'ας$',
	'actions': rules['O51nop']['actions'] +
		[
		{
			'replace': 'ατα',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ατων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
# O51a: μόνο το φως και το ημίφως
# ημίφως
rules['O51anop'] = {
	'match': 'ως$',
	'actions':
		[
		{
			'replace': 'ως',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'match': '^φως$',
			'search': 'ως$',
			'replace': 'ωτός',
			'restype': 'OusEnGen',
		},
		{
			'match': '^ημίφως$',
			'search': 'ως$',
			'replace': 'ους',
			'restype': 'OusEnGen',
		},
		]
}
# φως
rules['O51a'] = {
	'match': 'ως$',
	'actions': rules['O51anop']['actions'] +
		[
		{
			'replace': 'ώτα',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ώτων',
			'restype': 'OusPlGen',
		},
		]
}
# O52: κατάληξη σε όν (και ον σκέτο), πληθυντικός σε όντα
# 
rules['O52nop'] = {
	'match': '[οό]ν$',
	'actions':
		[
		{
			'search': '',
			'replace': '',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'όντος',
			'restype': 'OusEnGen',
		},
		]
}
# ον, παρόν, προσόν, προϊόν
rules['O52'] = {
	'match': '[οό]ν$',
	'actions': rules['O52nop']['actions'] +
		[
		{
			'replace': 'όντα',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'όντων',
			'restype': 'OusPlGen',
		},
		]
}
# O53: κατάληξη σε ον, πληθυντικός σε οντα
# όζον
rules['O53nop'] = {
	'match': 'ον$',
	'actions':
		[
		{
			'search': '',
			'replace': '',
			'restype': ['OusEnOnom', 'OusEnAit', 'OusEnKlit'],
		},
		{
			'replace': 'οντος',
			'restype': 'OusEnGen',
		},
		]
}
# μέλλον, διαφέρον, ενδιαφέρον, ζέον, καθήκον
rules['O53'] = {
	'match': 'ον$',
	'actions': rules['O53nop']['actions'] +
		[
		{
			'replace': 'οντα',
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'οντων',
			'restype': 'OusPlGen',
			'callfunc': transfertonosdown,
		},
		]
}


# E1: κατάληξη σε ός, θηλυκό σε ή
# καλός, αιολικός, αιχμηρός, ωχρός
rules['E1o'] = {
	'match': 'ός$',
	'actions':
		[
		{
			'replace': 'ός',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'ού',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ό',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'έ',
			'restype': 'EpArsEnKlit',
		},
		{
			'replace': 'οί',
			'restype': 'EpArsPlOnom',
		},
		{
			'replace': 'ών',
			'restype': 'EpArsPlGen',
		},
		{
			'replace': 'ούς',
			'restype': 'EpArsPlAit',
		},
		{
			'replace': 'οί',
			'restype': 'EpArsPlKlit',
		},
		]
}
rules['E1h'] = {
	'match': 'ή$',
	'actions':
		[
		{
			'replace': 'ή',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ής',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ές',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E1to'] = {
	'match': 'ό$',
	'actions':
		[
		{
			'replace': 'ό',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ού',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'ά',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E1'] = {
	'match': '(ός|ή|ό)$',
	'actions': rules['E1o']['actions'] + rules['E1h']['actions'] + rules['E1to']['actions']
}
# E2: ίδιο με E1, αλλά το θηλυκό είναι σε ιά
# γλυκός, ελαφρός, νιος (!)
rules['E2o'] = rules['E1o']
rules['E2to'] = rules['E1to']
rules['E2h'] = {
	'match': 'ιά$',
	'actions':
		[
		{
			'replace': 'ιά',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ιάς',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ές',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E2'] = {
	'match': '(ός|ιά|ό)$',
	'actions': rules['E2o']['actions'] + rules['E2h']['actions'] + rules['E2to']['actions']
}
# E3: κατάληξη σε ος, θηλυκό σε η
# άσπρος, αφορεσμένος, βαρβάτος, γιομάτος
rules['E3o'] = {
	'match': 'ος$',
	'actions':
		[
		{
			'replace': 'ος',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'ου',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ο',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'ε',
			'restype': 'EpArsEnKlit',
		},
		{
			'replace': 'οι',
			'restype': 'EpArsPlOnom',
		},
		{
			'replace': 'ων',
			'restype': 'EpArsPlGen',
		},
		{
			'replace': 'ους',
			'restype': 'EpArsPlAit',
		},
		{
			'replace': 'οι',
			'restype': 'EpArsPlKlit',
		},
		]
}
rules['E3h'] = {
	'match': 'η$',
	'actions':
		[
		{
			'replace': 'η',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ης',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E3to'] = {
	'match': 'ο$',
	'actions':
		[
		{
			'replace': 'ο',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ου',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'α',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E3'] = {
	'match': '(ος|η|ο)$',
	'actions': rules['E3o']['actions'] + rules['E3h']['actions'] + rules['E3to']['actions']
}
# E4: ίδιο με E3, αλλά θηλυκό σε α
# αστείος, ωραίος, ατόφιος, γαλάζιος
rules['E4o'] = rules['E3o']
rules['E4to'] = rules['E3to']
rules['E4h'] = {
	'match': 'α$',
	'actions':
		[
		{
			'replace': 'α',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E4'] = {
	'match': '(ος|α|ο)$',
	'actions': rules['E4o']['actions'] + rules['E4h']['actions'] + rules['E4to']['actions']
}
# E5: ίδιο με E3, αλλά τονίζεται στην προπαραλήγουσα
# όμορφος, άγευστος, ώριμος
rules['E5o'] = rules['E3o']
rules['E5h'] = rules['E3h']
rules['E5to'] = rules['E3to']
rules['E5'] = rules['E3']
# E6: ίδιο με E4, αλλά τονίζεται στην προπαραλήγουσα
# άγιος, αδέξιος, άθλιος, ύπτιος, χρόνιος, τέλειος
rules['E6o'] = rules['E4o']
rules['E6h'] = rules['E4h']
rules['E6to'] = rules['E4to']
rules['E6'] = rules['E4']
# E7: κατάληξη σε -ύς, -ιά, -ύ
# τραχύς, βαθύς, βαρύς, μακρύς, παχύς, πλατύς
rules['E7o'] = {
	'match': 'ύς$',
	'actions':
		[
		{
			'replace': 'ύς',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'ιού',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ύ',
			'restype': ['EpArsEnGen', 'EpArsEnAit', 'EpArsEnKlit'],
		},
		{
			'replace': 'ιοί',
			'restype': 'EpArsPlOnom',
		},
		{
			'replace': 'είς',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'ιών',
			'restype': 'EpArsPlGen',
		},
		{
			'replace': 'ιούς',
			'restype': 'EpArsPlAit',
		},
		{
			'replace': 'ιοί',
			'restype': 'EpArsPlKlit',
		},
		]
}
rules['E7h'] = {
	'match': 'ιά$',
	'actions':
		[
		{
			'replace': 'ιά',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ιάς',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ιές',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ιών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E7to'] = {
	'match': 'ύ$',
	'actions':
		[
		{
			'replace': 'ύ',
			'restype': ['EpOuEnOnom', 'EpOuEnGen', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ιού',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'ιά',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ιών',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E7'] = {
	'match': '(ύς|ιά|ύ)$',
	'actions': rules['E7o']['actions'] + rules['E7h']['actions'] + rules['E7to']['actions']
}
# E7a: κατάληξη σε -ύς, -εία, -ύ
# ευθύς, βραδύς, δασύς, οξύς, ταχύς, θρασύς
rules['E7ao'] = {
	'match': 'ύς$',
	'actions':
		[
		{
			'replace': 'ύς',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'έος',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ύ',
			'restype': ['EpArsEnGen', 'EpArsEnAit', 'EpArsEnKlit'],
		},
		{
			'replace': 'είς',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'έων',
			'restype': 'EpArsPlGen',
		},
		]
}
rules['E7ah'] = {
	'match': 'εία$',
	'actions':
		[
		{
			'replace': 'εία',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'είας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'είες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ειών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E7ato'] = {
	'match': 'ύ$',
	'actions':
		[
		{
			'replace': 'ύ',
			'restype': ['EpOuEnOnom', 'EpOuEnGen', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'έος',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'έα',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'έων',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E7a'] = {
	'match': '(ύς|εία|ύ)$',
	'actions': rules['E7ao']['actions'] + rules['E7ah']['actions'] + rules['E7ato']['actions']
}
# E8: κατάληξη σε -ής, -ιά, -ί
# σταχτής, θαλασσής, κανελής, καφεδής
rules['E8o'] = {
	'match': 'ής$',
	'actions':
		[
		{
			'replace': 'ής',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'ιού',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ή',
			'restype': ['EpArsEnGen', 'EpArsEnAit', 'EpArsEnKlit'],
		},
		{
			'replace': 'ιοί',
			'restype': 'EpArsPlOnom',
		},
		{
			'replace': 'ιών',
			'restype': 'EpArsPlGen',
		},
		{
			'replace': 'ιούς',
			'restype': 'EpArsPlAit',
		},
		{
			'replace': 'ιοί',
			'restype': 'EpArsPlKlit',
		},
		]
}
rules['E8h'] = rules['E7h']
rules['E8to'] = {
	'match': 'ί$',
	'actions':
		[
		{
			'replace': 'ί',
			'restype': ['EpOuEnOnom', 'EpOuEnGen', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ιού',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'ιά',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ιών',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E8'] = {
	'match': '(ής|ιά|ί)$',
	'actions': rules['E8o']['actions'] + rules['E8h']['actions'] + rules['E8to']['actions']
}
# E9: κατάληξη σε -ης, -α, -ικο
# ζηλιάρης, κιτρινιάρης, μαυρομάτης, ξεδοντιάρης
rules['E9o'] = {
	'match': 'ης$',
	'actions':
		[
		{
			'replace': 'ης',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'η',
			'restype': ['EpArsEnGen', 'EpArsEnAit', 'EpArsEnKlit'],
		},
		{
			'replace': 'ηδες',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'ηδων',
			'restype': 'EpArsPlGen',
		},
		]
}
rules['E9h'] = {
	'match': 'α$',
	'actions':
		[
		{
			'replace': 'α',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ων', # ασυνήθιστο
			'restype': 'EpThPlGen',
		},
		]
}
rules['E9to'] = {
	'match': 'ικο$',
	'actions':
		[
		{
			'replace': 'ικο',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ικου',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'ικα',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ικων',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E9'] = {
	'match': '(ης|α|ικο)$',
	'actions': rules['E9o']['actions'] + rules['E9h']['actions'] + rules['E9to']['actions']
}
# E9a: κατάληξη σε -άς, -ού, -άδικο
# 
rules['E9ao'] = {
	'match': 'άς$',
	'actions':
		[
		{
			'replace': 'άς',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'ά',
			'restype': ['EpArsEnGen', 'EpArsEnAit', 'EpArsEnKlit'],
		},
		{
			'replace': 'άδες',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'άδων',
			'restype': 'EpArsPlGen',
		},
		]
}
rules['E9ah'] = {
	'match': 'ού$',
	'actions':
		[
		{
			'replace': 'ού',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ούς',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ούδες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ούδων',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E9ato'] = {
0:	{
		'match': 'άδικο$',
		'actions':
			[
			{
				'replace': 'άδικο',
				'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
			},
			{
				'replace': 'άδικου',
				'restype': 'EpOuEnGen',
			},
			{
				'replace': 'άδικα',
				'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
			},
			{
				'replace': 'άδικων',
				'restype': 'EpOuPlGen',
			},
			]
	},
1: 	{
		'match': 'ούδικο$',
			'actions':
				[
				{
					'replace': 'ούδικο',
					'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
				},
				{
					'replace': 'ούδικου',
					'restype': 'EpOuEnGen',
				},
				{
					'replace': 'ούδικα',
					'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
				},
				{
					'replace': 'ούδικων',
					'restype': 'EpOuPlGen',
				},
				]
	}
}
rules['E9a'] = {
	'match': '(άς|ού|άδικο|ούδικο)$',
	'actions': rules['E9ao']['actions'] + rules['E9ah']['actions'] + rules['E9ato'][0]['actions'] + rules['E9ato'][1]['actions']
}
# E10: κατάληξη σε -ής, -ής, -ές
# συνεχής, ατυχής, γηγενής, διαφανής, διεθνής, ψυχοπαθής
rules['E10o'] = {
	'match': 'ής$',
	'actions':
		[
		{
			'replace': 'ής',
			'restype': ['EpArsEnOnom', 'EpArsEnKlit'],
		},
		{
			'replace': 'ούς',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ή',
			'restype': ['EpArsEnAit', 'EpArsEnKlit'],
		},
		{
			'replace': 'είς',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpArsPlGen',
		},
		]
}
rules['E10h'] = {
	'match': 'ής$',
	'actions':
		[
		{
			'replace': 'ής',
			'restype': ['EpThEnOnom', 'EpThEnKlit'],
		},
		{
			'replace': 'ούς',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ή',
			'restype': 'EpThEnAit',
		},
		{
			'replace': 'είς',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E10to'] = {
	'match': 'ές$',
	'actions':
		[
		{
			'replace': 'ές',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ούς',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'ή',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E10'] = {
	'match': '(ής|ές)$',
	'actions': rules['E10o']['actions'] + rules['E10h']['actions'] + rules['E10to']['actions']
}
# E11: κατάληξη σε -ης, -ης, -ες
# ελώδης, αγχώδης, αμμώδης, ευώδης, ζωώδης, φρενήρης, χαώδης
rules['E11o'] = {
	'match': 'ης$',
	'actions':
		[
		{
			'replace': 'ης',
			'restype': ['EpArsEnOnom', 'EpArsEnKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'η',
			'restype': ['EpArsEnAit', 'EpArsEnKlit'],
		},
		{
			'replace': 'εις',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpArsPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E11h'] = {
	'match': 'ης$',
	'actions':
		[
		{
			'replace': 'ης',
			'restype': ['EpThEnOnom', 'EpThEnKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'η',
			'restype': 'EpThEnAit',
		},
		{
			'replace': 'εις',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E11to'] = {
	'match': 'ες$',
	'actions':
		[
		{
			'replace': 'ες',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'η',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpOuPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E11'] = {
	'match': '(ης|ες)$',
	'actions': rules['E11o']['actions'] + rules['E11h']['actions'] + rules['E11to']['actions']
}
# E11a: κατάληξη σε -ης, -ης, -ες. Ίδιο με E11, αλλά δεν κατεβάζει τόνο
# κακοήθης, αήθης, αυθάδης, επιμηκής, συνήθης
rules['E11ao'] = {
	'match': 'ης$',
	'actions':
		[
		{
			'replace': 'ης',
			'restype': ['EpArsEnOnom', 'EpArsEnKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'η',
			'restype': ['EpArsEnAit', 'EpArsEnKlit'],
		},
		{
			'replace': 'εις',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpArsPlGen',
		},
		]
}
rules['E11ah'] = {
	'match': 'ης$',
	'actions':
		[
		{
			'replace': 'ης',
			'restype': ['EpThEnOnom', 'EpThEnKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'η',
			'restype': 'EpThEnAit',
		},
		{
			'replace': 'εις',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E11ato'] = {
	'match': 'ες$',
	'actions':
		[
		{
			'replace': 'ες',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'η',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E11a'] = {
	'match': '(ης|ες)$',
	'actions': rules['E11ao']['actions'] + rules['E11ah']['actions'] + rules['E11ato']['actions']
}
# E12: κατάληξη σε -ων, -ουσα, -ον
# τρέχων, άρχων, αρμόζων, ισχύων, κατέχων, πάσχων, υποβόσκων, φέρων
rules['E12o'] = {
	'match': 'ων$',
	'actions':
		[
		{
			'replace': 'ων',
			'restype': ['EpArsEnOnom', 'EpArsEnKlit'],
		},
		{
			'replace': 'οντος',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'οντα',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'οντες',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'οντων',
			'restype': 'EpArsPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E12h'] = {
	'match': 'ουσα$',
	'actions':
		[
		{
			'replace': 'ουσα',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ουσης',
			'restype': 'EpThEnGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ουσας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ουσες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ουσων',
			'restype': 'EpThPlGen',
			'callfunc': transfertonosdowntwice,
		},
		]
}
rules['E12to'] = {
	'match': 'ον$',
	'actions':
		[
		{
			'replace': 'ον',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'οντος',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'οντα',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'οντων',
			'restype': 'EpOuPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E12'] = {
	'match': '(ων|ουσα|ον)$',
	'actions': rules['E12o']['actions'] + rules['E12h']['actions'] + rules['E12to']['actions']
}
# E12a: κατάληξη σε -ών, -ούσα, -όν
# ανιών, απών, παθών, παρελθών
rules['E12ao'] = {
	'match': 'ών$',
	'actions':
		[
		{
			'replace': 'ών',
			'restype': ['EpArsEnOnom', 'EpArsEnKlit'],
		},
		{
			'replace': 'όντος',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'όντος',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'όντες',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'όντων',
			'restype': 'EpArsPlGen',
		},
		]
}
rules['E12ah'] = {
	'match': 'ούσα$',
	'actions':
		[
		{
			'replace': 'ούσα',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ούσης',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ούσας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ούσες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ουσών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E12ato'] = {
	'match': 'όν$',
	'actions':
		[
		{
			'replace': 'όν',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'όντος',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'όντα',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'όντων',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E12a'] = {
	'match': '(ών|ούσα|όν)$',
	'actions': rules['E12ao']['actions'] + rules['E12ah']['actions'] + rules['E12ato']['actions']
}
# E12b: κατάληξη σε -ών, -ούσα, -ούν
# συμπαθών, ανθών, διαφωνών, κρατών
rules['E12bo'] = {
	'match': 'ών$',
	'actions':
		[
		{
			'replace': 'ών',
			'restype': ['EpArsEnOnom', 'EpArsEnKlit'],
		},
		{
			'replace': 'ούντος',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ούντα',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'ούντες',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'ούντων',
			'restype': 'EpArsPlGen',
		},
		]
}
rules['E12bh'] = rules['E12ah']
rules['E12bto'] = {
	'match': 'ούν$',
	'actions':
		[
		{
			'replace': 'ούν',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ούντος',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'ούντα',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ούντων',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E12b'] = {
	'match': '(ών|ούσα|ούν)$',
	'actions': rules['E12bo']['actions'] + rules['E12bh']['actions'] + rules['E12bto']['actions']
}
# E12c: κατάληξη σε -είς, -είσα, -έν
# διασωθείς, δοθείς, κατατεθείς, προσληφθείς, συμφωνηθείς
rules['E12co'] = {
	'match': 'είς$',
	'actions':
		[
		{
			'replace': 'είς',
			'restype': ['EpArsEnOnom', 'EpArsEnKlit'],
		},
		{
			'replace': 'έντος',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'έντα',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'έντες',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'έντων',
			'restype': 'EpArsPlGen',
		},
		]
}
rules['E12ch'] = {
	'match': 'είσα$',
	'actions':
		[
		{
			'replace': 'είσα',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'είσης',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'είσας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'είσες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'εισών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E12cto'] = {
	'match': 'έν$',
	'actions':
		[
		{
			'replace': 'έν',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'έντος',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'έντα',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'έντων',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E12c'] = {
	'match': '(είς|είσα|έν)$',
	'actions': rules['E12co']['actions'] + rules['E12ch']['actions'] + rules['E12cto']['actions']
}
# E12d: κατάληξη σε -είς, -είσα, -έν
# λήξας, άπας, σύμπας, διατελέσας
rules['E12do'] = {
	'match': 'ας$',
	'actions':
		[
		{
			'replace': 'ας',
			'restype': ['EpArsEnOnom', 'EpArsEnKlit'],
		},
		{
			'replace': 'αντος',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'αντα',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'αντες',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'αντων',
			'restype': 'EpArsPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E12dh'] = {
	'match': 'ασα$',
	'actions':
		[
		{
			'replace': 'ασα',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ασης',
			'restype': 'EpThEnGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ασας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ασες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ασών',
			'restype': 'EpThPlGen',
			'callfunc': deletefirsttonos,
		},
		]
}
rules['E12dto'] = {
	'match': 'αν$',
	'actions':
		[
		{
			'replace': 'αν',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'αντος',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'αντα',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'αντων',
			'restype': 'EpOuPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E12d'] = {
	'match': '(ας|ασα|αν)$',
	'actions': rules['E12do']['actions'] + rules['E12dh']['actions'] + rules['E12dto']['actions']
}
# E12e: κατάληξη σε -ους, -ους, -ουν
# βραδύνους, άνους, μικρόνους, οξύνους
rules['E12eo'] = {
	'match': 'ους$',
	'actions':
		[
		{
			'replace': 'ους',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'ου',
			'restype': ['EpArsEnGen', 'EpArsEnAit'],
		},
		{
			'replace': 'οες',
			'restype': ['EpArsPlOnom', 'EpArsPlAit'],
		},
		{
			'replace': 'οων',
			'restype': 'EpArsPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E12eh'] = {
	'match': 'ους$',
	'actions':
		[
		{
			'replace': 'ους',
			'restype': 'EpThEnOnom',
		},
		{
			'replace': 'ου',
			'restype': ['EpThEnGen', 'EpThEnAit'],
		},
		{
			'replace': 'οες',
			'restype': ['EpThPlOnom', 'EpThPlAit'],
		},
		{
			'replace': 'οων',
			'restype': 'EpThPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E12eto'] = {
	'match': 'ουν$',
	'actions':
		[
		{
			'replace': 'ουν',
			'restype': ['EpOuEnOnom', 'EpOuEnAit'],
		},
		{
			'replace': 'ου',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'οα',
			'restype': ['EpOuPlOnom', 'EpOuPlAit'],
		},
		{
			'replace': 'οων',
			'restype': 'EpOuPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E12e'] = {
	'match': '(ους|ουν)$',
	'actions': rules['E12eo']['actions'] + rules['E12eh']['actions'] + rules['E12eto']['actions']
}
# E12st: κατάληξη σε -ων, -ώσα, -ων
# δρων, ζων, ενθουσιών, κυβερνών
rules['E12sto'] = {
	'match': '(ων|ών)$',
	'actions':
		[
		{
			'search': '',
			'replace': '',
			'restype': ['EpArsEnOnom', 'EpArsEnKlit'],
		},
		{
			'replace': 'ώντος',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ώντα',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'ώντες',
			'restype': ['EpArsPlOnom', 'EpArsPlAit', 'EpArsPlKlit'],
		},
		{
			'replace': 'ώντων',
			'restype': 'EpArsPlGen',
		},
		]
}
rules['E12sth'] = {
	'match': 'ώσα$',
	'actions':
		[
		{
			'replace': 'ώσα',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ώσης',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ώσας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ώσες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ωσών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E12stto'] = {
	'match': '(ων|ών)$',
	'actions':
		[
		{
			'search': '',
			'replace': '',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ώντος',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'ώντα',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ώντων',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E12st'] = {
	'match': '(ων|ών)$', # Δεν δεχόμαστε τη μορφή του θηλυκού ως εκκίνηση
	'actions': rules['E12sto']['actions'] + rules['E12sth']['actions'] + rules['E12stto']['actions']
}
# E13: κατάληξη σε -ός, -ά, -ό
# φθοροποιός, ειρηνοποιός, ζωοποιός, κακοποιός, χαροποιός
rules['E13o'] = {
	'match': '(ός)$',
	'actions':
		[
		{
			'replace': 'ός',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'ού',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ό',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'έ',
			'restype': 'EpArsEnKlit',
		},
		{
			'replace': 'οί',
			'restype': ['EpArsPlOnom', 'EpArsPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpArsPlGen',
		},
		{
			'replace': 'ούς',
			'restype': 'EpArsPlAit',
		},
		]
}
rules['E13oh'] = {
	'match': '(ός)$',
	'actions':
		[
		{
			'replace': 'ός',
			'restype': 'EpThEnOnom',
		},
		{
			'replace': 'ού',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ό',
			'restype': 'EpThEnAit',
		},
		{
			'replace': 'έ',
			'restype': 'EpThEnKlit',
		},
		{
			'replace': 'οί',
			'restype': ['EpThPlOnom', 'EpThPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpThPlGen',
		},
		{
			'replace': 'ούς',
			'restype': 'EpThPlAit',
		},
		]
}
rules['E13h'] = {
	'match': 'ά$',
	'actions':
		[
		{
			'replace': 'ά',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'άς',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ές',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E13to'] = {
	'match': '(ό)$',
	'actions':
		[
		{
			'replace': 'ό',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ού',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'ά',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E13'] = {
	'match': '(ός|ά|ό)$',
	'actions': rules['E13o']['actions'] + rules['E13oh']['actions'] +  rules['E13h']['actions'] + rules['E13to']['actions']
}
# E14: κατάληξη σε -ος, -α, -ο
# ζημιογόνος, ελικοφόρος, εντομοφάγος, ιστιοφόρος, καινοτόμος, ωοτόκος
rules['E14o'] = {
	'match': '(ος)$',
	'actions':
		[
		{
			'replace': 'ος',
			'restype': 'EpArsEnOnom',
		},
		{
			'replace': 'ου',
			'restype': 'EpArsEnGen',
		},
		{
			'replace': 'ο',
			'restype': 'EpArsEnAit',
		},
		{
			'replace': 'ε',
			'restype': 'EpArsEnKlit',
		},
		{
			'replace': 'οι',
			'restype': ['EpArsPlOnom', 'EpArsPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpArsPlGen',
		},
		{
			'replace': 'ους',
			'restype': 'EpArsPlAit',
		},
		]
}
rules['E14oh'] = {
	'match': '(ος)$',
	'actions':
		[
		{
			'replace': 'ος',
			'restype': 'EpThEnOnom',
		},
		{
			'replace': 'ου',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ο',
			'restype': 'EpThEnAit',
		},
		{
			'replace': 'ε',
			'restype': 'EpThEnKlit',
		},
		{
			'replace': 'οι',
			'restype': ['EpThPlOnom', 'EpThPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
		},
		{
			'replace': 'ους',
			'restype': 'EpThPlAit',
		},
		]
}
rules['E14h'] = {
	'match': 'α$',
	'actions':
		[
		{
			'replace': 'α',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E14to'] = {
	'match': '(ο)$',
	'actions':
		[
		{
			'replace': 'ο',
			'restype': ['EpOuEnOnom', 'EpOuEnAit', 'EpOuEnKlit'],
		},
		{
			'replace': 'ου',
			'restype': 'EpOuEnGen',
		},
		{
			'replace': 'α',
			'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpOuPlGen',
		},
		]
}
rules['E14'] = {
	'match': '(ος|α|ο)$',
	'actions': rules['E14o']['actions'] + rules['E14oh']['actions'] + rules['E14h']['actions'] + rules['E14to']['actions']
}
# E15: κατάληξη σε -ος, -α, -ο. Ίδιο με Ε14, με κάποιες έξτρα μορφές
# ευκλείδειος, δαμόκλειος, έγγειος, έγκυος, διαγώνιος, λεόντειος
rules['E15o'] = {
	'match': '(ος)$',
	'actions': rules['E14o']['actions'] +
		[
		{
			'replace': 'ου',
			'restype': 'EpArsEnGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ων',
			'restype': 'EpArsPlGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ους',
			'restype': 'EpArsPlAit',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E15oh'] = {
	'match': '(ος)$',
	'actions': rules['E14oh']['actions'] +
		[
		{
			'replace': 'ου',
			'restype': 'EpThEnGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ους',
			'restype': 'EpThPlAit',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E15h'] = {
	'match': 'α$',
	'actions':
		[
		{
			'replace': 'α',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ας',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E15to'] = {
	'match': '(ο)$',
	'actions': rules['E14to']['actions'] +
		[
		{
			'replace': 'ου',
			'restype': 'EpOuEnGen',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ων',
			'restype': 'EpOuPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E15'] = {
	'match': '(ος|α|ο)$',
	'actions': rules['E15o']['actions'] + rules['E15oh']['actions'] + rules['E15h']['actions'] + rules['E15to']['actions']
}
# E16: κατάληξη σε -ός, -ή, -ό. Ίδιο με Ε13, αλλά -ή στο θηλυκό
# ανενεργός, ηχαγωγός, προσαγωγός, ενεργός
rules['E16o'] = rules['E13o']
rules['E16oh'] = rules['E13oh']
rules['E16h'] = {
	'match': 'ή$',
	'actions':
		[
		{
			'replace': 'ή',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ής',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ές',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ών',
			'restype': 'EpThPlGen',
		},
		]
}
rules['E16to'] = rules['E13to']
rules['E16'] = {
	'match': '(ός|ή|ό)$',
	'actions': rules['E16o']['actions'] + rules['E16oh']['actions'] + rules['E16h']['actions'] + rules['E16to']['actions']
}
# E17: κατάληξη σε -ος, -η, -ο. Ίδιο με Ε15, αλλά θυληκό σε -η
# διάδικος, 
rules['E17o'] = rules['E15o']
rules['E17oh'] = rules['E15oh']
rules['E17h'] = {
	'match': 'η$',
	'actions':
		[
		{
			'replace': 'η',
			'restype': ['EpThEnOnom', 'EpThEnAit', 'EpThEnKlit'],
		},
		{
			'replace': 'ης',
			'restype': 'EpThEnGen',
		},
		{
			'replace': 'ες',
			'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
			'callfunc': transfertonosdown,
		},
		]
}
rules['E17to'] = rules['E15to']
rules['E17'] = {
	'match': '(ος|η|ο)$',
	'actions': rules['E17o']['actions'] +  rules['E17oh']['actions'] + rules['E17h']['actions'] + rules['E17to']['actions']
}
rules['E'] =  {
0:
	{
		'match': '^πολύς$',
		'search': 'ύς$',
		'actions':
			[
			{
				'replace': 'ύς',
				'restype': 'EpArsEnOnom',
			},
			{
				'replace': 'ύ',
				'restype': ['EpArsEnGen', 'EpArsEnAit'],
			},
			{
				'replace': 'λού',
				'restype': 'EpArsEnGen',
			},
			{
				'replace': 'λοί',
				'restype': ['EpArsPlOnom', 'EpArsPlKlit'],
			},
			{
				'replace': 'λών',
				'restype': 'EpArsPlGen',
			},
			{
				'replace': 'λούς',
				'restype': 'EpArsPlAit',
			},
			{
				'replace': 'λή',
				'restype': ['EpThEnOnom', 'EpThEnAit'],
			},
			{
				'replace': 'λής',
				'restype': 'EpThEnGen',
			},
			{
				'replace': 'λές',
				'restype': ['EpThPlOnom', 'EpThPlAit', 'EpThPlKlit'],
			},
			{
				'replace': 'λών',
				'restype': 'EpThPlGen',
			},
			{
				'replace': 'ύ',
				'restype': ['EpOuEnOnom', 'EpOuEnGen', 'EpOuEnAit'],
			},
			{
				'replace': 'λού',
				'restype': 'EpOuEnGen',
			},
			{
				'replace': 'λά',
				'restype': ['EpOuPlOnom', 'EpOuPlAit', 'EpOuPlKlit'],
			},
			{
				'replace': 'λών',
				'restype': 'EpOuPlGen',
			},
			]
	}
}


rules['P1a'] = { # Κλειδώνω
		'match': '(ώνω|ώνομαι)$',
		'actions':
			[
			{
				'replace': 'ώνω',
				'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
			},
			{
				'replace': 'ώνεις',
				'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
			},
			{
				'replace': 'ώνει',
				'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
			},
			{
				'replace': 'ώνουμε',
				'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
			},
			{
				'replace': 'ώνετε',
				'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
			},
			{
				'replace': 'ώνουν',
				'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
			},
			{
				'replace': 'ώνε',
				'restype': 'RhmEnergEnestProstEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώνοντας',
				'restype': 'RhmEnergEnestMetox',
			},
			{
				'replace': 'ώνα',
				'restype': 'RhmEnergPrtOristEgw',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώνες',
				'restype': 'RhmEnergPrtOristEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώνε',
				'restype': 'RhmEnergPrtOristAytos',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώναμε',
				'restype': 'RhmEnergPrtOristEmeis',
			},
			{
				'replace': 'ώνατε',
				'restype': 'RhmEnergPrtOristEseis',
			},
			{
				'replace': 'ώναν',
				'restype': 'RhmEnergPrtOristAytoi',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώσα',
				'restype': 'RhmEnergAorOristEgw',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώσες',
				'restype': 'RhmEnergAorOristEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώσε',
				'restype': 'RhmEnergAorOristAytos',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώσαμε',
				'restype': 'RhmEnergAorOristEmeis',
			},
			{
				'replace': 'ώσατε',
				'restype': 'RhmEnergAorOristEseis',
			},
			{
				'replace': 'ώσαν',
				'restype': 'RhmEnergAorOristAytoi',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώσω',
				'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
			},
			{
				'replace': 'ώσεις',
				'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
			},
			{
				'replace': 'ώσει',
				'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
			},
			{ # Same with above
				'replace': 'ώσει',
				'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'],
			},
			{ # Variation of above
				'replace': 'ωμένο',
				'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'],
			},
			{
				'replace': 'ώσουμε',
				'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
			},
			{
				'replace': 'ώσετε',
				'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
			},
			{
				'replace': 'ώσουν',
				'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
			},
			{
				'replace': 'ώσε',
				'restype': 'RhmEnergAorProstEgw',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ώστε',
				'restype': 'RhmEnergAorProstEmeis',
			},
			{
				'replace': 'ώσει',
				'restype': ['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'],
			},
			{ # Same with above for Ypotaktikh
				'replace': 'ώσει',
				'restype': ['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'],
			},
			{ # Same with above for Syntelesmenos Mellontas
				'replace': 'ώσει',
				'restype': ['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			},
			{ # Variation of the above
				'replace': 'ωμένο',
				'restype': ['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			},
			# End of Energhtikh Fwnh
			]
	}
rules['P1b'] = { # Κλειδώνω
		'match': '(ώνω|ώνομαι)$',
		'actions':
			[
			{
				'replace': 'ώνομαι',
				'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
			},
			{
				'replace': 'ώνεσαι',
				'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
			},
			{
				'replace': 'ώνου',
				'restype': 'RhmPathEnestProstEsy',
			},
			{
				'replace': 'ώνεται',
				'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
			},
			{
				'replace': 'ωνόμαστε',
				'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			},
			{
				'replace': 'ώνεστε',
				'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis', 'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
			},
			{
				'replace': 'ώνονται',
				'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
			},
			{
				'replace': 'ωνόμουν',
				'restype': 'RhmPathPrtOristEgw',
			},
			{
				'replace': 'ωνόσουν',
				'restype': 'RhmPathPrtOristEsy',
			},
			{
				'replace': 'ωνόταν',
				'restype': 'RhmPathPrtOristAytos',
			},
			{
				'replace': 'ωνόμασταν',
				'restype': 'RhmPathPrtOristEmeis',
			},
			{
				'replace': 'ωνόσασταν',
				'restype': 'RhmPathPrtOristEseis',
			},
			{
				'replace': 'ώνονταν',
				'restype': 'RhmPathPrtOristAytoi',
			},
			{
				'replace': 'ώθηκα',
				'restype': 'RhmPathAorOristEgw',
			},
			{
				'replace': 'ώθηκες',
				'restype': 'RhmPathAorOristEsy',
			},
			{
				'replace': 'ώθηκε',
				'restype': 'RhmPathAorOristAytos',
			},
			{
				'replace': 'ωθήκαμε',
				'restype': 'RhmPathAorOristEmeis',
			},
			{
				'replace': 'ωθήκατε',
				'restype': 'RhmPathAorOristEseis',
			},
			{
				'replace': 'ώθηκαν',
				'restype': 'RhmPathAorOristAytoi',
			},
			{
				'replace': 'ωθώ',
				'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			},
			{
				'replace': 'ωθείς',
				'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			},
			{
				'replace': 'ωθεί',
				'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			},
			{ # Same with above
				'replace': 'ωθεί',
				'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'],
			},
			{ # Variation of above
				'replace': 'ωμένος',
				'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'],
			},
			{ # plural form of the above
				'replace': 'ωμένοι',
				'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'],
			},
			{
				'replace': 'ωθούμε',
				'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			},
			{
				'replace': 'ωθείτε',
				'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			},
			{
				'replace': 'ωθούν',
				'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			},
			{
				'replace': 'ώσου',
				'restype': 'RhmPathAorProstEgw',
			},
			{
				'replace': 'ωθείτε',
				'restype': 'RhmPathAorProstEmeis',
			},
			{
				'replace': 'ωθεί',
				'restype': ['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'],
			},
			{ # Same with above for Ypotaktikh
				'replace': 'ωθεί',
				'restype': ['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'],
			},
			{ # Variation of the above for Oristikh and Ypotaktikh
				'replace': 'ωμένος',
				'restype': ['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'],
			},
			{ # plural of the above
				'replace': 'ωμένοι',
				'restype': ['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'],
			},
			{ # Same with above for Syntelesmenos Mellontas
				'replace': 'ωθεί',
				'restype': ['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			},
			{ # Variation of the above
				'replace': 'ωμένος',
				'restype': ['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			},
			{ # plural of the above
				'replace': 'ωμένοι',
				'restype': ['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			},
			{
				'replace': 'ωμένος',
				'restype': 'RhmPathPrkMetox',
			},
			# End of Pathhtikh Fwnh
			]
	}
rules['P1'] =  {
		'match': '(ώνω|ώνομαι)$',
		'actions': rules['P1a']['actions'] + rules['P1b']['actions'],
	}
rules['P2.1a'] = { # αγαλιάζω, αθεΐζω, αναδακρύζω
		'match': '(ζω|ζομαι)$',
		'actions':
			[
			{
				'replace': 'ζω',
				'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
			},
			{
				'replace': 'ζεις',
				'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
			},
			{
				'replace': 'ζει',
				'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
			},
			{
				'replace': 'ζουμε',
				'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
			},
			{
				'replace': 'ζετε',
				'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
			},
			{
				'replace': 'ζουν',
				'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
			},
			{
				'replace': 'ζε',
				'restype': 'RhmEnergEnestProstEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ζοντας',
				'restype': 'RhmEnergEnestMetox',
			},
			{
				'replace': 'ζα',
				'restype': 'RhmEnergPrtOristEgw',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ζες',
				'restype': 'RhmEnergPrtOristEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ζε',
				'restype': 'RhmEnergPrtOristAytos',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ζαμε',
				'restype': 'RhmEnergPrtOristEmeis',
			},
			{
				'replace': 'ζατε',
				'restype': 'RhmEnergPrtOristEseis',
			},
			{
				'replace': 'ζαν',
				'restype': 'RhmEnergPrtOristAytoi',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'σα',
				'restype': 'RhmEnergAorOristEgw',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'σες',
				'restype': 'RhmEnergAorOristEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'σε',
				'restype': 'RhmEnergAorOristAytos',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'σαμε',
				'restype': 'RhmEnergAorOristEmeis',
			},
			{
				'replace': 'σατε',
				'restype': 'RhmEnergAorOristEseis',
			},
			{
				'replace': 'σαν',
				'restype': 'RhmEnergAorOristAytoi',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'σω',
				'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
			},
			{
				'replace': 'σεις',
				'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
			},
			{
				'replace': 'σει',
				'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
			},
			{ # Same with above
				'replace': 'σει',
				'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'],
			},
			{ # Variation of above
				'replace': 'σμενο',
				'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'],
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'σουμε',
				'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
			},
			{ # Variation of above
				'replace': 'σομε',
				'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
			},
			{
				'replace': 'σετε',
				'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
			},
			{
				'replace': 'σουν',
				'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
			},
			{
				'replace': 'σε',
				'restype': 'RhmEnergAorProstEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'στε',
				'restype': 'RhmEnergAorProstEseis',
			},
			{
				'replace': 'σει',
				'restype': ['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'],
			},
			{ # Variation of the above
				'replace': 'σμενο',
				'restype': ['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'],
				'callfunc': transfertonosdown,
			},
			{ # Same for Ypotaktikh
				'replace': 'σει',
				'restype': ['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'],
			},
			{ # Variation of the above
				'replace': 'σμενο',
				'restype': ['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'],
				'callfunc': transfertonosdown,
			},
			{ # Same with above for Syntelesmenos Mellontas
				'replace': 'σει',
				'restype': ['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			},
			{ # Variation of the above
				'replace': 'σμενο',
				'restype': ['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
				'callfunc': transfertonosdown,
			},
			# End of Energhtikh Fwnh
			]
	}
rules['P2.1b'] = { # αναλογίζομαι, ανασπάζομαι, αστεΐζομαι
		'match': '(ζω|ζομαι)$',
		'actions':
			[
			{
				'replace': 'ζομαι',
				'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
			},
			{
				'replace': 'ζεσαι',
				'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
			},
			{
				'replace': 'ζου',
				'restype': 'RhmPathEnestProstEsy',
			},
			{
				'replace': 'ζεται',
				'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
			},
			{
				'replace': 'ζομαστε',
				'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'ζεστε',
				'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
			},
			{
				'replace': 'ζονται',
				'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
			},
			{
				'replace': 'ζομουν',
				'restype': 'RhmPathPrtOristEgw',
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'ζοσουν',
				'restype': 'RhmPathPrtOristEsy',
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'ζοταν',
				'restype': 'RhmPathPrtOristAytos',
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'ζομασταν',
				'restype': 'RhmPathPrtOristEmeis',
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'ζοσασταν',
				'restype': 'RhmPathPrtOristEseis',
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'ζονταν',
				'restype': 'RhmPathPrtOristAytoi',
			},
			{
				'replace': 'στηκα',
				'restype': 'RhmPathAorOristEgw',
			},
			{
				'replace': 'στηκες',
				'restype': 'RhmPathAorOristEsy',
			},
			{
				'replace': 'στηκε',
				'restype': 'RhmPathAorOristAytos',
			},
			{
				'replace': 'στηκαμε',
				'restype': 'RhmPathAorOristEmeis',
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'στηκατε',
				'restype': 'RhmPathAorOristEseis',
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'στηκαν',
				'restype': 'RhmPathAorOristAytoi',
			},
			{
				'replace': 'στω',
				'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'στεις',
				'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'στει',
				'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
				'callfunc': transfertonosdown,
			},
			{ # Same with above
				'replace': 'στει',
				'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'],
				'callfunc': transfertonosdown,
			},
			{ # Variation of above
				'replace': 'σμενος',
				'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'],
				'callfunc': transfertonosdown,
			},
			{ # plural form of the above
				'replace': 'σμενοι',
				'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'],
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'στουμε',
				'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'στειτε',
				'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'στουν',
				'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'σου',
				'restype': 'RhmPathAorProstEsy',
			},
			{
				'replace': 'στειτε',
				'restype': 'RhmPathAorProstEseis',
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'στει',
				'restype': ['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'],
				'callfunc': transfertonosdown,
			},
			# FIXME: το "σμενος" είναι "σμενοι" στον πληθυντικό!
			{ # Variation of the above
				'replace': 'σμενος',
				'restype': ['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'],
				'callfunc': transfertonosdown,
			},
			{ # Same with above for Ypotaktikh
				'replace': 'στει',
				'restype': ['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'],
				'callfunc': transfertonosdown,
			},
			{ # Variation of the above
				'replace': 'σμενος',
				'restype': ['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'],
				'callfunc': transfertonosdown,
			},
			{ # Same with above for Syntelesmenos Mellontas
				'replace': 'στει',
				'restype': ['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
				'callfunc': transfertonosdown,
			},
			{ # Variation of the above
				'replace': 'σμενος',
				'restype': ['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
				'callfunc': transfertonosdown,
			},
			{ # plural of the above
				'replace': 'σμενοι',
				'restype': ['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
				'callfunc': transfertonosdown,
			},
			{
				'replace': 'σμενος',
				'restype': 'RhmPathPrkMetox',
				'callfunc': transfertonosdown,
			},
			# End of Pathhtikh Fwnh
			]
	}
rules['P2.1'] =  { # δροσίζω, προσανατολίζω
		'match': '(ζω|ζομαι)$',
		'actions': rules['P2.1a']['actions'] + rules['P2.1b']['actions'],
	}
# αλλάζω, ανταλλάζω, αρπάζω
# εκτυλίσσω, εξελίσσω
# διορύσσω, διακηρύσσω, 
# ανταλλάσσω, αναταράσσω, διαφυλάσσω
# διανοίγω, 
# διαφυλάττω, 
# εμπαίζω,
# φράζω, σφάζω, τάζω (!)
var1 = 'ξ'
var2 = 'γμ'
var3 = 'χτ'
rules['P2.2abase'] = {
	'match': '(%s+ω|%sομαι)$' % (symfwno, symfwno),
	'actions':
		[
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		# RhmEnergEnestProstEsy is added afterwards
		{
			'search' : '(ω|ομαι)$',
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		# RhmEnergAorProstEsy is added afterwards
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
rules['P2.2a'] = {
	'match': rules['P2.2abase']['match'],
	'actions': rules['P2.2abase']['actions'] +
		[
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		]
}
# 
rules['P2.2b'] = {
	'match': '(%s+ω|%sομαι)$' % (symfwno, symfwno),
	'actions':
		[
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P2.2'] =  {
	'match': '(%s+ω|%sομαι)$' % (symfwno, symfwno),
	'actions': rules['P2.2a']['actions'] + rules['P2.2b']['actions'],
}
# Same with P2.2 but with an extra form
# αγγίζω, ζουπίζω, στουμπίζω, στραγγίζω, σφαλίζω
rules['P2.3a'] = {
	'match': rules['P2.2a']['match'],
	'actions': rules['P2.2a']['actions'] +
		[
		{
			'replace': 'σα',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'σες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'σε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'σαμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': 'σατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': 'σαν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'σω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': 'σεις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': 'σει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': 'σει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': 'σμενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'σουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': 'σετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': 'σουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': 'σε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'στε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P2.3b'] = {
	'match': rules['P2.2b']['match'],
	'actions': rules['P2.2b']['actions'] +
		[
		{
			'replace': 'στηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': 'στηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': 'στηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': 'στηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'στηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'στηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': 'στω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'στεις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'στει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': 'στει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': 'σμενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': 'σμενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'στουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'στειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'στουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'σου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': 'στειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'σμενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P2.3'] =  {
	'match': rules['P2.2']['match'],
	'actions': rules['P2.3a']['actions'] + rules['P2.3b']['actions'],
}
# Same with P2.2 but with different Prostaktikh
# διαλέγω, διδάσκω, πλέκω, ανοίγω
rules['P3a'] = {
	'match': rules['P2.2abase']['match'],
	'actions': rules['P2.2abase']['actions'] +
		[
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
		},
		{
			'replace': 'ξε',
			'restype': 'RhmEnergAorProstEsy',
		},
		]
}
rules['P3b'] = {
	'match': rules['P2.2b']['match'],
	'actions': rules['P2.2b']['actions'],
}
rules['P3'] =  {
	'match': rules['P2.2']['match'],
	'actions': rules['P3a']['actions'] + rules['P3b']['actions'],
}
# κρύβω, ανάβω, ανακαλύπτω, ξεβάφω, ράβω, στέφω, τρέπω
var1 = 'ψ'
var2 = 'μμ'
var3 = 'φτ'
rules['P4a'] = {
	'match': '(%s+ω|%sομαι)$' % (symfwno, symfwno),
	'actions':
		[
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P4b'] = {
	'match': '(%s+ω|%sομαι)$' % (symfwno, symfwno),
	'actions':
		[
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search' : '(ω|ομαι)$',
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P4'] =  {
	'match': '(%s+ω|%sομαι)$' % (symfwno, symfwno),
	'actions': rules['P4a']['actions'] + rules['P4b']['actions'],
}
# δεσμεύω, καταγοητεύω, κηδεύω, προμηθεύω, φονεύω
var1 = 'σ'
var2 = 'μ'
var3 = 'τ'
rules['P5.1a'] = {
	'match': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P5.1b'] = {
	'match': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P5.1'] =  {
	'match': '(ω|ομαι)$',
	'actions': rules['P5.1a']['actions'] + rules['P5.1b']['actions'],
}
# φυτεύω, αγγαρεύω, αγριεύω, λατρεύω, ληστεύω, ξοδεύω
var1 = 'ψ'
var2 = 'μ'
var3 = 'τ'
rules['P5.2a'] = {
	'match': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P5.2b'] = {
	'match': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var1 + 'ου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(εύω|εύομαι)$',
			'replace': 'έ' + var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P5.2'] =  {
	'match': '(ω|ομαι)$',
	'actions': rules['P5.2a']['actions'] + rules['P5.2b']['actions'],
}
# τρατάρω, σερβίρω, σκανάρω, σκιτσάρω, τεζάρω
var2 = 'ισμ'
var3 = 'ιστ'
rules['P6a'] = {
	'match': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ιζα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ιζες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ιζε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ιζαμε',
			'restype': 'RhmEnergPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ιζατε',
			'restype': 'RhmEnergPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ιζαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ισα',
			'restype': 'RhmEnergAorOristEgw',
		},
		{
			'replace': 'ισες',
			'restype': 'RhmEnergAorOristEsy',
		},
		{
			'replace': 'ισε',
			'restype': 'RhmEnergAorOristAytos',
		},
		{
			'replace': 'ισαμε',
			'restype': 'RhmEnergAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ισατε',
			'restype': 'RhmEnergAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ισαν',
			'restype': 'RhmEnergAorOristAytoi',
		},
		{
			'replace': 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': 'ισμενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		#variation of the above
		{
			'replace': 'ισε',
			'restype': 'RhmEnergAorProstEsy',
		},
		{
			'replace': 'ετε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P6b'] = {
	'match': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ιζομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': 'ιζοσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': 'ιζοταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': 'ιζομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': 'ιζοσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': 'ιζονταν',
			'restype': 'RhmPathPrtOristAytoi',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdowntwice,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdowntwice,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdowntwice,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': 'ισου',
			'restype': 'RhmPathAorProstEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdowntwice,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdowntwice,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P6'] =  {
	'match': '(ω|ομαι)$',
	'actions': rules['P6a']['actions'] + rules['P6b']['actions'],
}
# μαραίνω, γλυκαίνω, ζεσταίνω, ξεραίνω, μουρλαίνω
var1 = 'ν'
var2 = 'μ'
var3 = 'άθ'
rules['P7.1a'] = {
	'match': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var1 + 'ετε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P7.1b'] = {
	'match': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': 'ά' + var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P7.1'] =  {
	'match': '(ω|ομαι)$',
	'actions': rules['P7.1a']['actions'] + rules['P7.1b']['actions'],
}
# λιπαίνω, ρυπαίνω, υγραίνω, υφαίνω
var1 = 'άν'
var2 = 'άσμ'
var3 = 'άνθ'
rules['P7.2a'] = {
	'match': '(αίνω|αίνομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ετε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P7.2b'] = {
	'match': '(αίνω|αίνομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P7.2'] =  {
	'match': '(αίνω|αίνομαι)$',
	'search': '(ω|ομαι)$',
	'actions': rules['P7.2a']['actions'] + rules['P7.2b']['actions'],
}
# Ίδιο με P7.2, αλλά με κάποιες έξτρα μορφές
# λευκαίνω, διαλευκαίνω, ψυχραίνω
var2 = 'άμ'
var3 = 'άθ'
rules['P7.3a'] = {
	'match': '(αίνω|αίνομαι)$',
	'search': '(ω|ομαι)$',
	'actions': rules['P7.2a']['actions'] +
		[
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P7.3b'] = {
	'match': '(αίνω|αίνομαι)$',
	'search': '(ω|ομαι)$',
	'actions': rules['P7.2b']['actions'] +
		[
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P7.3'] =  {
	'match': '(αίνω|αίνομαι)$',
	'search': '(ω|ομαι)$',
	'actions': rules['P7.3a']['actions'] + rules['P7.3b']['actions'],
}
# απαλαίνω, παχαίνω
var1 = 'ύν'
var2 = 'ύμ'
var3 = 'ύνθ'
rules['P7.4a'] = {
	'match': '(αίνω|αίνομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var1 + 'ετε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P7.4b'] = {
	'match': '(αίνω|αίνομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(αίνω|αίνομαι)$',
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P7.4'] =  {
	'match': '(αίνω|αίνομαι)$',
	'search': '(ω|ομαι)$',
	'actions': rules['P7.4a']['actions'] + rules['P7.4b']['actions'],
}
# ευκολύνω, πληθύνω, ελαφρύνω, ενθαρρύνω, επιταχύνω, αμβλύνω, δασύνω
var1 = 'ύν'
var2 = 'ύμ'
var3 = 'ύνθ'
rules['P8.1a'] = {
	'match': '(ύνω|ύνομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'search': '(ύνω|ύνομαι)$',
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ετε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P8.1b'] = {
	'match': '(ύνω|ύνομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'search': '(ύνω|ύνομαι)$',
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'search': '(ύνω|ύνομαι)$',
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': 'ύνσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P8.1'] =  {
	'match': '(ύνω|ύνομαι)$',
	'search': '(ω|ομαι)$',
	'actions': rules['P8.1a']['actions'] + rules['P8.1b']['actions'],
}
# μολύνω, απομακρύνω, μεγεθύνω, σμικρύνω
var1 = 'ύν'
var2 = 'ύσμ'
var3 = 'ύνθ'
rules['P8.2a'] = {
	'match': '(ύνω|ύνομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'search': '(ύνω|ύνομαι)$',
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var1 + 'ετε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P8.2b'] = {
	'match': '(ύνω|ύνομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'search': '(ύνω|ύνομαι)$',
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'search': '(ύνω|ύνομαι)$',
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': 'ύνσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύνω|ύνομαι)$',
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P8.2'] =  {
	'match': '(ύνω|ύνομαι)$',
	'search': '(ω|ομαι)$',
	'actions': rules['P8.2a']['actions'] + rules['P8.2b']['actions'],
}
# ιδρύω, αναλύω, διαλύω, διανύω, ενδύω (special case), κρούω (unsupported)
# μηνύω, πτύω
var1 = 'ύσ'
var2 = 'ύμ'
var3 = 'ύθ'
rules['P9a'] = {
	'match': '([^ο]ύω|[^ο]ύομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'α',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ες',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'αν',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'search': '(ύω|ύομαι)$',
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var1 + 'ετε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P9b'] = {
	'match': '([^ο]ύω|[^ο]ύομαι)$',
	'search': '(ω|ομαι)$',
	'actions':
		[
		{
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'search': '(ύω|ύομαι)$',
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'search': '(ύω|ύομαι)$',
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': 'ύσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search': '(ύω|ύομαι)$',
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P9'] =  {
	'match': '([^ο]ύω|[^ο]ύομαι)$',
	'search': '(ω|ομαι)$',
	'actions': rules['P9a']['actions'] + rules['P9b']['actions'],
}
# αγαπώ, κατακτώ, κατανικώ, διαλώ, δαπανώ, γρονθοκοπώ, κουνώ, λαλώ, μαδώ, χτυπώ
var1 = 'ήσ'
var2 = 'ήμ'
var3 = 'ήθ'
rules['P10.1a'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ά',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'άει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'άμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'άτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'άν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ά',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.1b'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ιέμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'ιέσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ιέται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ιόμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'ιέστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ιούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ιόμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ιόσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ιόταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ιόμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ιόσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ιόνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ήσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.1'] =  {
	'match': '(ώ|άω|ιέμαι)$',
	'actions': rules['P10.1a']['actions'] + rules['P10.1b']['actions'],
}
# ζουπώ, ζουλώ, πηδάω, σκουντώ
# Ίδιο με P10.1 αλλά με έξτρα μορφές
var1 = 'ήξ'
var2 = 'ήγμ'
var3 = 'ήχτ'
rules['P10.2a'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions': rules['P10.1a']['actions'] +
		[
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.2b'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions': rules['P10.1b']['actions'] +
		[
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ήξου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.2'] =  {
	'match': '(ώ|άω|ιέμαι)$',
	'actions': rules['P10.2a']['actions'] + rules['P10.2b']['actions'],
}
# βαστώ
var1 = 'ήξ'
var11 = 'άξ'
var2 = 'ήγμ'
var22 = 'άγμ'
var3 = 'ήχτ'
var33 = 'άχτ'
rules['P10.3a'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ά',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'άει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'άμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'άτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'άν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ά',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		{
			'replace': var11 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var11 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var11 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var11 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var11 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var11 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var11 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var11 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var11 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var11 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var22 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var11 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var11 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var11 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var11 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var11 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var11 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.3b'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ιέμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'ιέσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ιέται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ιόμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'ιέστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ιούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ιόμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ιόσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ιόταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ιόμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ιόσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ιόνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var33 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var33 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var33 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var33 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var33 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var33 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var33 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var33 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var33 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var33 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var22 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var22 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var33 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var33 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var33 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var33 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var22 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ήξου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': 'άξου',
			'restype': 'RhmPathAorProstEsy',
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.3'] =  {
	'match': '(ώ|άω|ιέμαι)$',
	'actions': rules['P10.3a']['actions'] + rules['P10.3b']['actions'],
}
# γελώ, κερνώ, διαπερνώ, κρεμώ, ξεχνώ, περνώ
var1 = 'άσ'
var2 = 'άσμ'
var3 = 'άστ'
rules['P10.4a'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ά',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'άει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'άμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'άτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'άν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ά',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.4b'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ιέμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'ιέσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ιέται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ιόμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'ιέστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ιούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ιόμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ιόσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ιόταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ιόμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ιόσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ιόνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'άσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.4'] =  {
	'match': '(ώ|άω|ιέμαι)$',
	'actions': rules['P10.4a']['actions'] + rules['P10.4b']['actions'],
}
# φορώ, παινώ, συχωρώ
var1 = 'έσ'
var2 = 'έμ'
var3 = 'έθ'
rules['P10.5a'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ά',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'άει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'άμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'άτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'άν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ά',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.5b'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ιέμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'ιέσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ιέται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ιόμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'ιέστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ιούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ιόμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ιόσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ιόταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ιόμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ιόσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ιόνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'έσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.5'] =  {
	'match': '(ώ|άω|ιέμαι)$',
	'actions': rules['P10.5a']['actions'] + rules['P10.5b']['actions'],
}
# πετώ, ξεπετώ, παραπετώ
var1 = 'άξ'
var2 = 'άγμ'
var22 = 'άμ'
var3 = 'άχτ'
rules['P10.6a'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ά',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'άει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'άμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'άτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'άν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ά',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var22 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.6b'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ιέμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'ιέσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ιέται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ιόμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'ιέστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ιούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ιόμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ιόσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ιόταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ιόμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ιόσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ιόνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var22 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var22 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'άξου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var22 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.6'] =  {
	'match': '(ώ|άω|ιέμαι)$',
	'actions': rules['P10.6a']['actions'] + rules['P10.6b']['actions'],
}
# τραβώ, βουτω, ρουφώ
var1 = 'ήξ'
var2 = 'ήγμ'
var3 = 'ήχτ'
rules['P10.7a'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ά',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'άει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'άμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'άτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'άν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ά',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.7b'] = {
	'match': '(ώ|άω|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ιέμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'ιέσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ιέται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ιόμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'ιέστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ιούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ιόμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ιόσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ιόταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ιόμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ιόσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ιόνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ήξου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.7'] =  {
	'match': '(ώ|άω|ιέμαι)$',
	'actions': rules['P10.7a']['actions'] + rules['P10.7b']['actions'],
}
# ανακλώ, αποσπώ, διαθλώ, περισπώ, διασπώ 
var1 = 'άσ'
var2 = 'άσμ'
var3 = 'άστ'
rules['P10.8a'] = {
	'match': '(ώ|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ά',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'άτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ά',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.8b'] = {
	'match': '(ώ|ιέμαι)$',
	'actions':
		[
		{
			'replace': 'ιέμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'ιέσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ιέται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ιόμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'ιέστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ιούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ιόμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ιόσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ιόταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ιόμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ιόσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ιόνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'άσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.8'] =  {
	'match': '(ώ|ιέμαι)$',
	'actions': rules['P10.8a']['actions'] + rules['P10.8b']['actions'],
}
# στερώ, δρομολογώ, δυσφημώ, εγχειρώ, ενεργώ, ενοχλώ, εννοώ
var1 = 'ήσ'
var2 = 'ήμ'
var3 = 'ήθ'
rules['P10.9a'] = {
	'match': '(ώ|ούμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'είς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'εί',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'είτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'εί',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.9b'] = {
	'match': '(ώ|ούμαι)$',
	'actions':
		[
		{
			'replace': 'ούμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'είσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'είται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ούμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'είστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ούμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ούσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ούνταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ούμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ούσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ούνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ήσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.9'] =  {
	'match': '(ώ|ούμαι)$',
	'actions': rules['P10.9a']['actions'] + rules['P10.9b']['actions'],
}
# αποτελώ, αναιρώ, αφαιρώ, διαιρώ, επαινώ
var1 = 'έσ'
var2 = 'έσμ'
var3 = 'έστ'
rules['P10.10a'] = {
	'match': '(ώ|ούμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'είς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'εί',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'είτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'εί',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.10b'] = {
	'match': '(ώ|ούμαι)$',
	'actions':
		[
		{
			'replace': 'ούμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'είσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'είται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ούμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'είστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ούμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ούσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ούνταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ούμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ούσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ούνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'έσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.10'] =  {
	'match': '(ώ|ούμαι)$',
	'actions': rules['P10.10a']['actions'] + rules['P10.10b']['actions'],
}
# μιλάω, ζητώ, κρατώ, λησμονώ
var1 = 'ήσ'
var2 = 'ήμ'
var3 = 'ήθ'
rules['P10.11a'] = {
	'match': '(ώ|άω|ούμαι)$',
	'actions':
		[
		{
			'replace': 'ώ',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		# alt.
		{
			'replace': 'άω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'replace': 'άς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		# alt.
		{
			'replace': 'είς',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'replace': 'ά',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		# alt.
		{
			'replace': 'άει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		# alt.
		{
			'replace': 'εί',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'replace': 'ούμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'replace': 'άμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'replace': 'άτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'είτε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis', 'RhmEnergEnestProstEseis'],
		},
		{
			'replace': 'ούν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'άν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'replace': 'ά',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ώντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'replace': 'ούσα',
			'restype': 'RhmEnergPrtOristEgw',
		},
		{
			'replace': 'ούσες',
			'restype': 'RhmEnergPrtOristEsy',
		},
		{
			'replace': 'ούσε',
			'restype': 'RhmEnergPrtOristAytos',
		},
		{
			'replace': 'ούσαμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'replace': 'ούσατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'replace': 'ούσαν',
			'restype': 'RhmEnergPrtOristAytoi',
		},
		{
			'replace': var1 + 'α',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ες',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'αμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': var1 + 'ατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': var1 + 'αν',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'ω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': var1 + 'εις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': var1 + 'ει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': var1 + 'ει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': var2 + 'ενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var1 + 'ουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': var1 + 'ομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': var1 + 'ετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': var1 + 'ουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': var1 + 'ε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': var1 + 'τε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P10.11b'] = {
	'match': '(ώ|άω|ούμαι)$',
	'actions':
		[
		{
			'replace': 'ιέμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'ιέσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'ιέται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'ιόμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'ιέστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ιούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'ιόμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'ιόσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'ιόταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'ιόμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'ιόσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'ιόνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ήσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P10.11'] =  {
	'match': '(ώ|άω|ούμαι)$',
	'actions': rules['P10.11a']['actions'] + rules['P10.11b']['actions'],
}
# εγγυώμαι, απεξαρτώμαι, ηττώμαι
var2 = 'ήμ'
var3 = 'ήθ'
rules['P11b'] = {
	'match': 'ώμαι$',
	'actions':
		[
		{
			'replace': 'ώμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'άσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'άται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'όμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'άστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ώνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'όμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'όσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'όταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'όμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'όσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'όνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ήσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P11'] =  {
	'match': 'ώμαι$',
	'actions': rules['P11b']['actions'],
}
# 
var2 = 'ήμ'
var3 = 'ήθ'
rules['P12b'] = {
	'match': 'άμαι$',
	'actions':
		[
		{
			'replace': 'άμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		# alt.
		{
			'replace': 'ούμαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'replace': 'άσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'replace': 'άται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'replace': 'όμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'ούμαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
		},
		{
			'replace': 'άστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathE3akolMellEseis'],
		},
		{
			'replace': 'ούνται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'replace': 'όμουν',
			'restype': 'RhmPathPrtOristEgw',
		},
		{
			'replace': 'όσουν',
			'restype': 'RhmPathPrtOristEsy',
		},
		{
			'replace': 'όταν',
			'restype': 'RhmPathPrtOristAytos',
		},
		{
			'replace': 'όμασταν',
			'restype': 'RhmPathPrtOristEmeis',
		},
		{
			'replace': 'όσασταν',
			'restype': 'RhmPathPrtOristEseis',
		},
		{
			'replace': 'όνταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': var3 + 'ηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': var3 + 'ηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': var3 + 'ηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': var3 + 'ηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': var3 + 'ω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'εις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': var3 + 'ει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': var2 + 'ενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': var2 + 'ενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': var3 + 'ουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ήσου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': var3 + 'ειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': var2 + 'ενος',
			'restype': 'RhmPathPrkMetox',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P12'] =  {
	'match': 'άμαι$',
	'actions': rules['P12b']['actions'],
}
