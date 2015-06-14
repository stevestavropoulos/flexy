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
import re, string
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

wordencoding += [{'from': 'λι', 'to': 'λx'}]
# This doesn't work:
#wordencoding += [{'from': 'λιώνω', 'to': 'λxώνω'}]

tonismenafwnhenta = 'abcdefάέήύίόώΐΰ';
atonafwnhenta = 'nopqrsαεηυιοωϊϋ';
fwnhenta = tonismenafwnhenta + atonafwnhenta;
# We add x, y, z, for use by the rules
symfwna = 'βγδζθκλμνξπρστφχψxyz';

tonismenofwnhen = '[' + tonismenafwnhenta + ']'
atonofwnhen = '[' + atonafwnhenta + ']'
fwnhen = '[' + fwnhenta + ']'
symfwno = '[' + symfwna + ']'

def preaction(word):
	return translate(wordencoding, word)

def postaction(word):
	return translateback(wordencoding, word)

def transfertonostwice(word):
	word = transfertonos(word)
	return transfertonos(word)

def transfertonos(word):
	return _transfertonos(word, 'down')

def transfertonosdown(word):
	return transfertonos(word)

def transfertonosdowntwice(word):
	return transfertonostwice(word)

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
# κανάγιας, τυχεράκιας
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'αδων',
			'restype': 'OusPlGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		]
}
# γίγας, γίγαντας, άτλας, άτλαντας, ελέφας
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
				'callfunc': transfertonos,
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
				'callfunc': transfertonos,
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
				'callfunc': transfertonos,
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
				'callfunc': transfertonos,
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
			'callfunc': transfertonostwice,
		},
		{
			'replace': 'αδων',
			'restype': 'OusPlGen',
			'callfunc': transfertonostwice,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ηδων',
			'restype': 'OusPlGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonostwice,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'εων',
			'restype': 'OusPlGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ους',
			'restype': 'OusPlAit',
			'callfunc': transfertonos,
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ου',
			'restype': 'OusEnGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonos,
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'callfunc': transfertonos,
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ους',
			'restype': 'OusEnGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ων',
			'restype': 'OusPlGen',
			'callfunc': transfertonostwice,
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'callfunc': transfertonos,
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ατος',
			'restype': 'OusEnGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ατων',
			'restype': 'OusPlGen',
			'callfunc': transfertonostwice,
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
		},
		{
			'replace': 'ατος',
			'restype': 'OusEnGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ατων',
			'restype': 'OusPlGen',
			'callfunc': transfertonostwice,
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'callfunc': transfertonos,
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonostwice,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ων',
			'restype': 'EpArsPlGen',
			'callfunc': transfertonos,
		},
		{
			'replace': 'ους',
			'restype': 'EpArsPlAit',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ων',
			'restype': 'EpThPlGen',
			'callfunc': transfertonos,
		},
		{
			'replace': 'ους',
			'restype': 'EpThPlAit',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
		},
		{
			'replace': 'ων',
			'restype': 'EpOuPlGen',
			'callfunc': transfertonos,
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
			'callfunc': transfertonos,
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
				'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis'],
			},
			{
				'replace': 'ώνουν',
				'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
			},
			{
				'replace': 'ώνε',
				'match2' : '^%s+%s' % (symfwno, tonismenofwnhen),
				'search2': '^',
				'replace2': 'ε',
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
				'restype': 'RhmPathPrkMtx',
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
				'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis'],
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
				'restype': 'RhmPathPrkMtx',
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
rules['P2.2a'] = {
	'match': '(%s+ω|%sομαι)$' % (symfwno, symfwno),
	'actions':
		[
		{
			'search' : 'ω|ομαι',
			'replace': 'ω',
			'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw', 'RhmEnergE3akolMellEgw'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'εις',
			'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy', 'RhmEnergE3akolMellEsy'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ει',
			'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos', 'RhmEnergE3akolMellAytos'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ουμε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		# alt.
		{
			'search' : 'ω|ομαι',
			'replace': 'ομε',
			'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis', 'RhmEnergE3akolMellEmeis'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ετε',
			'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis', 'RhmEnergE3akolMellEseis'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ουν',
			'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi', 'RhmEnergE3akolMellAytoi'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ε',
			'restype': 'RhmEnergEnestProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'οντας',
			'restype': 'RhmEnergEnestMetox',
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'α',
			'match2' : '^%s+%s' % (symfwno, tonismenofwnhen),
			'search2': '^',
			'replace2': 'ε',
			'restype': 'RhmEnergPrtOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ες',
			'match2' : '^%s+%s' % (symfwno, tonismenofwnhen),
			'search2': '^',
			'replace2': 'ε',
			'restype': 'RhmEnergPrtOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ε',
			'match2' : '^%s+%s' % (symfwno, tonismenofwnhen),
			'search2': '^',
			'replace2': 'ε',
			'restype': 'RhmEnergPrtOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'αμε',
			'restype': 'RhmEnergPrtOristEmeis',
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ατε',
			'restype': 'RhmEnergPrtOristEseis',
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'αν',
			'match2' : '^%s+%s' % (symfwno, tonismenofwnhen),
			'search2': '^',
			'replace2': 'ε',
			'restype': 'RhmEnergPrtOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ξα',
			'match2' : '^%s+%s' % (symfwno, tonismenofwnhen),
			'search2': '^',
			'replace2': 'ε',
			'restype': 'RhmEnergAorOristEgw',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ξες',
			'match2' : '^%s+%s' % (symfwno, tonismenofwnhen),
			'search2': '^',
			'replace2': 'ε',
			'restype': 'RhmEnergAorOristEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ξε',
			'match2' : '^%s+%s' % (symfwno, tonismenofwnhen),
			'search2': '^',
			'replace2': 'ε',
			'restype': 'RhmEnergAorOristAytos',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ξαμε',
			'restype': 'RhmEnergAorOristEmeis',
		},
		{
			'replace': 'ξατε',
			'restype': 'RhmEnergAorOristEseis',
		},
		{
			'replace': 'ξαν',
			'match2' : '^%s+%s' % (symfwno, tonismenofwnhen),
			'search2': '^',
			'replace2': 'ε',
			'restype': 'RhmEnergAorOristAytoi',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ξω',
			'restype': ['RhmEnergAorYpotEgw', 'RhmEnergStigmMellEgw'],
		},
		{
			'replace': 'ξεις',
			'restype': ['RhmEnergAorYpotEsy', 'RhmEnergStigmMellEsy'],
		},
		{
			'replace': 'ξει',
			'restype': ['RhmEnergAorYpotAytos', 'RhmEnergAorApar', 'RhmEnergStigmMellAytos'],
		},
		{ # Same with above
			'replace': 'ξει',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
		},
		{ # Variation of above
			'replace': 'γμενο',
			'restype': ['RhmEnergYpersEgw', 'RhmEnergYpersEsy', 'RhmEnergYpersAytos', 'RhmEnergYpersEmeis', 'RhmEnergYpersEseis', 'RhmEnergYpersAytoi'] +
				['RhmEnergPrkOristEgw', 'RhmEnergPrkOristEsy', 'RhmEnergPrkOristAytos', 'RhmEnergPrkOristEmeis', 'RhmEnergPrkOristEseis', 'RhmEnergPrkOristAytoi'] +
				['RhmEnergPrkYpotEgw', 'RhmEnergPrkYpotEsy', 'RhmEnergPrkYpotAytos', 'RhmEnergPrkYpotEmeis', 'RhmEnergPrkYpotEseis', 'RhmEnergPrkYpotAytoi'] +
				['RhmEnergSyntelMellEgw', 'RhmEnergSyntelMellEsy', 'RhmEnergSyntelMellAytos', 'RhmEnergSyntelMellEmeis', 'RhmEnergSyntelMellEseis', 'RhmEnergSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ξουμε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{ # Variation of above
			'replace': 'ξομε',
			'restype': ['RhmEnergAorYpotEmeis', 'RhmEnergStigmMellEmeis'],
		},
		{
			'replace': 'ξετε',
			'restype': ['RhmEnergAorYpotEseis', 'RhmEnergStigmMellEseis'],
		},
		{
			'replace': 'ξουν',
			'restype': ['RhmEnergAorYpotAytoi', 'RhmEnergStigmMellAytoi'],
		},
		{
			'replace': 'ξε',
			'restype': 'RhmEnergAorProstEsy',
			'callfunc': transfertonosup,
		},
		{
			'replace': 'ξτε',
			'restype': 'RhmEnergAorProstEseis',
		},
		# End of Energhtikh Fwnh
		]
}
# 
rules['P2.2b'] = {
	'match': '(%s+ω|%sομαι)$' % (symfwno, symfwno),
	'actions':
		[
		{
			'search' : 'ω|ομαι',
			'replace': 'ομαι',
			'restype': ['RhmPathEnestOristEgw', 'RhmPathEnestYpotEgw', 'RhmPathE3akolMellEgw'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'εσαι',
			'restype': ['RhmPathEnestOristEsy', 'RhmPathEnestYpotEsy', 'RhmPathE3akolMellEsy'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ου',
			'restype': 'RhmPathEnestProstEsy',
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'εται',
			'restype': ['RhmPathEnestOristAytos', 'RhmPathEnestYpotAytos', 'RhmPathE3akolMellAytos'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ομαστε',
			'restype': ['RhmPathEnestOristEmeis', 'RhmPathEnestYpotEmeis', 'RhmPathE3akolMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'εστε',
			'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis',  'RhmPathEnestProstEseis', 'RhmPathE3akolMellEseis'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ονται',
			'restype': ['RhmPathEnestOristAytoi', 'RhmPathEnestYpotAytoi', 'RhmPathE3akolMellAytoi'],
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ομουν',
			'restype': 'RhmPathPrtOristEgw',
			'callfunc': transfertonosdown,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'οσουν',
			'restype': 'RhmPathPrtOristEsy',
			'callfunc': transfertonosdown,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'οταν',
			'restype': 'RhmPathPrtOristAytos',
			'callfunc': transfertonosdown,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ομασταν',
			'restype': 'RhmPathPrtOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'οσασταν',
			'restype': 'RhmPathPrtOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'search' : 'ω|ομαι',
			'replace': 'ονταν',
			'restype': 'RhmPathPrtOristAytoi',
		},
		{
			'replace': 'χτηκα',
			'restype': 'RhmPathAorOristEgw',
		},
		{
			'replace': 'χτηκες',
			'restype': 'RhmPathAorOristEsy',
		},
		{
			'replace': 'χτηκε',
			'restype': 'RhmPathAorOristAytos',
		},
		{
			'replace': 'χτηκαμε',
			'restype': 'RhmPathAorOristEmeis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'χτηκατε',
			'restype': 'RhmPathAorOristEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'χτηκαν',
			'restype': 'RhmPathAorOristAytoi',
		},
		{
			'replace': 'χτω',
			'restype': ['RhmPathAorYpotEgw', 'RhmPathStigmMellEgw'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'χτεις',
			'restype': ['RhmPathAorYpotEsy', 'RhmPathStigmMellEsy'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'χτει',
			'restype': ['RhmPathAorYpotAytos', 'RhmPathAorApar', 'RhmPathStigmMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # Same with above
			'replace': 'χτει',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos', 'RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos', 'RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos', 'RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos', 'RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{ # Variation of above
			'replace': 'γμενος',
			'restype': ['RhmPathYpersEgw', 'RhmPathYpersEsy', 'RhmPathYpersAytos'] +
				['RhmPathPrkOristEgw', 'RhmPathPrkOristEsy', 'RhmPathPrkOristAytos'] +
				['RhmPathPrkYpotEgw', 'RhmPathPrkYpotEsy', 'RhmPathPrkYpotAytos'] +
				['RhmPathSyntelMellEgw', 'RhmPathSyntelMellEsy', 'RhmPathSyntelMellAytos'],
			'callfunc': transfertonosdown,
		},
		{ # plural form of the above
			'replace': 'γμενοι',
			'restype': ['RhmPathYpersEmeis', 'RhmPathYpersEseis', 'RhmPathYpersAytoi'] +
				['RhmPathPrkOristEmeis', 'RhmPathPrkOristEseis', 'RhmPathPrkOristAytoi'] +
				['RhmPathPrkYpotEmeis', 'RhmPathPrkYpotEseis', 'RhmPathPrkYpotAytoi'] +
				['RhmPathSyntelMellEmeis', 'RhmPathSyntelMellEseis', 'RhmPathSyntelMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'χτουμε',
			'restype': ['RhmPathAorYpotEmeis', 'RhmPathStigmMellEmeis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'χτειτε',
			'restype': ['RhmPathAorYpotEseis', 'RhmPathStigmMellEseis'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'χτουν',
			'restype': ['RhmPathAorYpotAytoi', 'RhmPathStigmMellAytoi'],
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'ξου',
			'restype': 'RhmPathAorProstEsy',
		},
		{
			'replace': 'χτειτε',
			'restype': 'RhmPathAorProstEseis',
			'callfunc': transfertonosdown,
		},
		{
			'replace': 'γμενος',
			'restype': 'RhmPathPrkMtx',
			'callfunc': transfertonosdown,
		},
		# End of Pathhtikh Fwnh
		]
}
rules['P2.2'] =  {
	'match': '(%s+ω|%sομαι)$' % (symfwno, symfwno),
	'actions': rules['P2.2a']['actions'] + rules['P2.2b']['actions'],
}
rules['P3'] = { # NOT complete. Just for testing of some corner cases
		'match': 'ω$',
		'actions':
			[
			{
				'replace': 'ω',
				'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw'],
			},
			{
				'replace': 'εις',
				'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy'],
			},
			{
				'replace': 'ει',
				'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos'],
			},
			{
				'replace': 'ουμε',
				'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis'],
			},
			{
				'replace': 'ετε',
				'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis'],
			},
			{
				'replace': 'ουν',
				'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi'],
			},
			{
				'replace': 'ε',
				'restype': 'RhmEnergEnestProstEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ετε',
				'restype': 'RhmEnergEnestProstEseis',
			},
			{
				'replace': 'οντας',
				'restype': 'RhmEnergEnestMetox',
			},
			{
				'replace': 'α',
				'match2' : '^%s*%s' % (symfwno, tonismenofwnhen),
				'search2': '^',
				'replace2': 'ε',
				'restype': 'RhmEnergParatOristEgw',
				'callfunc': transfertonosup,
			},
			]
	}
