# -*- coding: iso-8859-7 -*-
#
#   Copyright 2006,2009 Steve Stavropoulos <steve@math.upatras.gr>
#
#   This file is part of Flexy.
#
#   Flexy is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   Foobar is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Foobar.  If not, see <http://www.gnu.org/licenses/>.


def translate(alist, word):
	for what in alist:
		word = word.replace(what['from'], what['to'])
	return word

def translateback(alist, word):
	for what in alist:
		word = word.replace(what['to'], what['from'])
	return word

wordencoding = [
	{'from': '��', 'to': 'a'},
	{'from': '��', 'to': 'b'},
	{'from': '��', 'to': 'c'},
	{'from': '��', 'to': 'd'},
	{'from': '��', 'to': 'e'},
	{'from': '��', 'to': 'f'},

	{'from': '��', 'to': 'k'},
	{'from': '��', 'to': 'l'},
	{'from': '��', 'to': 'm'},
	{'from': '��', 'to': 'n'},
	{'from': '��', 'to': 'o'},
	{'from': '��', 'to': 'p'},
]
tonismenafwnhenta = 'abcdef���������';
atonafwnhenta = 'klmnop���������';
fwnhenta = tonismenafwnhenta + atonafwnhenta;
symfwna = '�����������������';

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
			paliostonos = symplegma.group(2).translate(string.maketrans(tonismenafwnhenta, atonafwnhenta))
			neostonos = symplegma.group(4).translate(string.maketrans(atonafwnhenta, tonismenafwnhenta))
		else:
			paliostonos = symplegma.group(4).translate(string.maketrans(tonismenafwnhenta, atonafwnhenta))
			neostonos = symplegma.group(2).translate(string.maketrans(atonafwnhenta, tonismenafwnhenta))
	else:
		return word # No match, no accent, do nothing more
	if direction == 'down':
		word = symplegma.group(1) + paliostonos + symplegma.group(3) + neostonos + symplegma.group(5)
	else:
		word = symplegma.group(1) + neostonos + symplegma.group(3) + paliostonos + symplegma.group(5)
	return word



rule = {'O1':
		{0:
			{'match': '��$',
			 'actions':
				[
				 	{
					 'replace': '��',
					 'restype': 'OusEnOnom',
					},
				 	{
					 'replace': '�',
					 'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
					},
				 	{
					 'replace': '����',
					 'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
					},
				 	{
					 'replace': '����',
					 'restype': 'OusPlGen',
					},
				]
			}
		},
	'O2':
		{0:
			{'match': '��$',
			 'actions':
				[
				 	{
					 'replace': '��',
					 'restype': 'OusEnOnom',
					},
				 	{
					 'replace': '�',
					 'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
					},
				 	{
					 'replace': '��',
					 'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
					},
				 	{
					 'replace': '��',
					 'restype': 'OusPlGen',
					},
				]
			}
		},
	'O3':
		{0:
			{'match': '��$',
			 'actions':
				[
				 	{
					 'replace': '��',
					 'restype': 'OusEnOnom',
					},
				 	{
					 'replace': '�',
					 'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
					},
				 	{
					 'replace': '��',
					 'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
					},
				 	{
					 'replace': '��',
					 'restype': 'OusPlGen',
					 'callfunc': transfertonos,
					},
				]
			}
		},
	'O3a':
		{0:
			{'match': '��$',
			 'actions':
				[
				 	{
					 'replace': '��',
					 'restype': 'OusEnOnom',
					},
				 	{
					 'replace': '��',
					 'restype': 'OusEnGen',
					 'callfunc': transfertonos,
					},
				 	{
					 'replace': '�',
					 'restype': ['OusEnGen' 'OusEnAit', 'OusEnKlit'],
					},
				 	{
					 'replace': '��',
					 'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
					},
				 	{
					 'replace': '��',
					 'restype': 'OusPlGen',
					 'callfunc': transfertonos,
					},
				]
			}
		},
	'O4':
		{0:
			{'match': '��$',
			 'actions':
				[
				 	{
					 'replace': '��',
					 'restype': 'OusEnOnom',
					},
				 	{
					 'replace': '�',
					 'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
					},
				 	{
					 'replace': '����',
					 'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
					 'callfunc': transfertonos,
					},
				 	{
					 'replace': '����',
					 'restype': 'OusPlGen',
					 'callfunc': transfertonos,
					},
				]
			}
		},
	'O5':
		{'match': '��$',
		 'actions':
			[
				{
				 'replace': '��',
				 'restype': 'OusEnOnom',
				},
				{
				 'replace': '�',
				 'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
				},
				{
				 'replace': '��',
				 'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
				},
				{
				 'replace': '��',
				 'restype': 'OusPlGen',
				 'callfunc': transfertonos,
				},
			]
		},
	'O5a':
		{0:
			{'match': '[^(?:���)]��$',
			 'search': '��$',
			 'actions':
				[
				 	{
					 'replace': '��',
					 'restype': 'OusEnOnom',
					},
				 	{
					 'replace': '�',
					 'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
					},
				 	{
					 'replace': '�����',
					 'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
					},
				 	{
					 'replace': '�����',
					 'restype': 'OusPlGen',
					 'callfunc': transfertonos,
					},
				]
			},
		1:
			{'match': '�����$',
			 'actions':
				[
				 	{
					 'replace': '�����',
					 'restype': 'OusEnOnom',
					},
				 	{
					 'replace': '����',
					 'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
					},
				 	{
					 'replace': '�����',
					 'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
					},
				 	{
					 'replace': '�����',
					 'restype': 'OusPlGen',
					 'callfunc': transfertonos,
					},
				]
			}
		},
	'O6':
		{0:
			{'match': '��$',
			 'actions':
				[
				 	{
					 'replace': '��',
					 'restype': 'OusEnOnom',
					},
				 	{
					 'replace': '�',
					 'restype': ['OusEnGen', 'OusEnAit', 'OusEnKlit'],
					},
				 	{
					 'replace': '����',
					 'restype': ['OusPlOnom', 'OusPlAit', 'OusPlKlit'],
					 'callfunc': transfertonostwice,
					},
				 	{
					 'replace': '����',
					 'restype': 'OusPlGen',
					 'callfunc': transfertonostwice,
					},
				]
			}
		},
	'P1':
		{0:
			{'match': '���$',
			 'actions':
				[
				 	{
					 'replace': '���',
					 'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw'],
					},
				 	{
					 'replace': '�����',
					 'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy'],
					},
				 	{
					 'replace': '����',
					 'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos'],
					},
				 	{
					 'replace': '������',
					 'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis'],
					},
				 	{
					 'replace': '�����',
					 'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis'],
					},
					{
					 'replace': '�����',
					 'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi'],
					},
					{
					 'replace': '���',
					 'restype': 'RhmEnergEnestProstEsy',
					 'callfunc': transfertonosup,
					},
					{
					 'replace': '�������',
					 'restype': 'RhmEnergEnestMetox',
					},
					{
					 'replace': '���',
					 'restype': 'RhmEnergPrtOristEgw',
					 'callfunc': transfertonosup,
					},
					{
					 'replace': '����',
					 'restype': 'RhmEnergPrtOristEsy',
					 'callfunc': transfertonosup,
					},
					{
					 'replace': '���',
					 'restype': 'RhmEnergPrtOristAytos',
					 'callfunc': transfertonosup,
					},
					{
					 'replace': '�����',
					 'restype': 'RhmEnergPrtOristEmeis',
					},
					{
					 'replace': '�����',
					 'restype': 'RhmEnergPrtOristEseis',
					},
					{
					 'replace': '����',
					 'restype': 'RhmEnergPrtOristAytoi',
					 'callfunc': transfertonosup,
					},
				]
			}
		},
	'P3':
		{0:
			{'match': '�$',
			 'actions':
				[
				 	{
					 'replace': '�',
					 'restype': ['RhmEnergEnestOristEgw', 'RhmEnergEnestYpotEgw'],
					},
				 	{
					 'replace': '���',
					 'restype': ['RhmEnergEnestOristEsy', 'RhmEnergEnestYpotEsy'],
					},
				 	{
					 'replace': '��',
					 'restype': ['RhmEnergEnestOristAytos', 'RhmEnergEnestYpotAytos'],
					},
				 	{
					 'replace': '����',
					 'restype': ['RhmEnergEnestOristEmeis', 'RhmEnergEnestYpotEmeis'],
					},
				 	{
					 'replace': '���',
					 'restype': ['RhmEnergEnestOristEseis', 'RhmEnergEnestYpotEseis'],
					},
					{
					 'replace': '���',
					 'restype': ['RhmEnergEnestOristAytoi', 'RhmEnergEnestYpotAytoi'],
					},
					{
					 'replace': '�',
					 'restype': 'RhmEnergEnestProstEsy',
					 'callfunc': transfertonosup,
					},
					{
					 'replace': '���',
					 'restype': 'RhmEnergEnestProstEseis',
					},
					{
					 'replace': '�����',
					 'restype': 'RhmEnergEnestMetox',
					},
					{
					 'replace': '�',
					 'match2' : '^%s*%s' % (symfwno, tonismenofwnhen),
					 'search2': '^',
					 'replace2': '�',
					 'restype': 'RhmEnergParatOristEgw',
					 'callfunc': transfertonosup,
					},
				]
			}
		},
	}
