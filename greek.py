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


rule = {
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
	},
	'P1': # Κλειδώνω
	{
		'match': 'ώνω$',
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
			{
				'replace': 'ώνομαι',
				'restype': ['RhmPathEnestOristEgw', 'RhmPathE3akolMellEgw'],
			},
			{
				'replace': 'ώνεσαι',
				'restype': ['RhmPathEnestOristEsy', 'RhmPathE3akolMellEsy'],
			},
			{
				'replace': 'ώνου',
				'restype': 'RhmPathEnestYpotEsy',
			},
			{
				'replace': 'ώνεται',
				'restype': ['RhmPathEnestOristAytos', 'RhmPathE3akolMellAytos'],
			},
			{
				'replace': 'ωνόμαστε',
				'restype': ['RhmPathEnestOristEmeis', 'RhmPathE3akolMellEmeis'],
			},
			{
				'replace': 'ώνεστε',
				'restype': ['RhmPathEnestOristEseis', 'RhmPathEnestYpotEseis', 'RhmPathE3akolMellEseis'],
			},
			{
				'replace': 'ώνονται',
				'restype': ['RhmPathEnestOristAytoi', 'RhmPathE3akolMellAytoi'],
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
	},
	'P2.1': # Δροσίζω
	{
		'match': 'ίζω$',
		'actions':
			[
			{
				'replace': 'ίζω',
				'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw'],
			},
			{
				'replace': 'ίζεις',
				'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy'],
			},
			{
				'replace': 'ίζει',
				'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos'],
			},
			{
				'replace': 'ίζουμε',
				'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis'],
			},
			{
				'replace': 'ίζομε',
				'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis'],
			},
			{
				'replace': 'ίζετε',
				'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis'],
			},
			{
				'replace': 'ίζουν',
				'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi'],
			},
			{
				'replace': 'ίζε',
				'restype': 'RhmEnergEnestProstEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ίζετε',
				'restype': 'RhmEnergEnestProstEseis',
			},
			{
				'replace': 'ίζοντας',
				'restype': 'RhmEnergEnestMetox',
			},
			{
				'replace': 'ίζα',
				'restype': 'RhmEnergPrtOristEgw',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ίζες',
				'restype': 'RhmEnergPrtOristEsy',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ίζε',
				'restype': 'RhmEnergPrtOristAytos',
				'callfunc': transfertonosup,
			},
			{
				'replace': 'ίζαμε',
				'restype': 'RhmEnergPrtOristEmeis',
			},
			{
				'replace': 'ίζατε',
				'restype': 'RhmEnergPrtOristEseis',
			},
			{
				'replace': 'ίζαν',
				'restype': 'RhmEnergPrtOristAytoi',
				'callfunc': transfertonosup,
			},
			]
	},
	'P3':
	{
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
	},
}
