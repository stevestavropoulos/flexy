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

	{'from': 'αι', 'to': 'k'},
	{'from': 'ου', 'to': 'l'},
	{'from': 'ει', 'to': 'm'},
	{'from': 'οι', 'to': 'n'},
	{'from': 'ευ', 'to': 'o'},
	{'from': 'αυ', 'to': 'p'},
]
tonismenafwnhenta = 'abcdefάέήύίόώΐΰ';
atonafwnhenta = 'klmnopαεηυιοωϊϋ';
fwnhenta = tonismenafwnhenta + atonafwnhenta;
symfwna = 'βγδζθκλμνξπρστφχψ';

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
		else:
			paliostonos = tr(tonismenafwnhenta, atonafwnhenta, symplegma.group(4))
			neostonos = tr(atonafwnhenta, tonismenafwnhenta, symplegma.group(2))
	else:
		print('Could not detect ascent in %s (original: %s)' % (word, postaction(word)), file=sys.stderr)
		return word # No match, no accent, do nothing more
	if direction == 'down':
		word = symplegma.group(1) + paliostonos + symplegma.group(3) + neostonos + symplegma.group(5)
	else:
		word = symplegma.group(1) + neostonos + symplegma.group(3) + paliostonos + symplegma.group(5)
	return word


rules = {
	'O1':
	{
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
			{
				'replace': 'άδες',
				'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			},
			{
				'replace': 'άδων',
				'restype': 'OusPlGen',
			},
			]
	},
	'O2':
	{
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
			{
				'replace': 'ες',
				'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
			},
			{
				'replace': 'ων',
				'restype': 'OusPlGen',
			},
			]
	},
	'O3':
	{
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
	'O3a':
	{
		'match': 'ας$',
		'actions':
			[
			{
				'replace': 'ας',
				'restype': 'OusEnOnom',
			},
			{
				'replace': 'ος',
				'restype': 'OusEnGen',
				'callfunc': transfertonos,
			},
			{
				'replace': 'α',
				'restype': ['OusEnGen' 'OusEnAit', 'OusEnKlit'],
			},
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
	'O4':
	{
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
	},
	'O5':
	{
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
	'O5a':
	{
		0:
		{
			'match': '[^(?:αντ)]ας$',
			'search': 'ας$',
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
			'actions':
				[
				{
					'replace': 'αντας',
					'restype': 'OusEnOnom',
				},
				{
					'replace': 'αντα',
					'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
				},
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
		}
	},
	'O6':
	{
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
				'replace': 'μενο',
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
