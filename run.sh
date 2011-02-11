#!/bin/sh

isoconvert='iconv -f utf-8 -t iso-8859-7'
utfconvert='iconv -t utf-8 -f iso-8859-7'
mkdir -p .stage/

for i in flexy.py greek.py; do
	cat $i | sed -e '1,10s/utf-8/iso-8859-7/' | $isoconvert > .stage/$i
done

cd .stage/
chmod 755 flexy.py

./flexy.py `echo "$@" | $isoconvert` | $utfconvert
