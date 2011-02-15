# -*- coding: utf-8 -*-

def getRE(patttern):
	return re.compile(patttern, re.I | re.L)

def tr(fr, to, word):
	"""poor man's unicode translate"""
	new = []
	for letter in word:
		pos = fr.find(letter)
		if pos != -1:
			new.append(to[pos])
	return ''.join(new)
    
def die(msg, exitcode=1):
	print(msg)
	sys.exit(exitcode)

