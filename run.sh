#!/bin/sh

isoconvert='iconv -f utf-8 -t iso-8859-7'
utfconvert='iconv -t utf-8 -f iso-8859-7'
mkdir -p .stage/

cat flexy.py | sed -e '1,10s/utf-8/iso-8859-7/' | $isoconvert > .stage/flexy.py
cat greek.py | sed -e '1,10s/utf-8/iso-8859-7/' | $isoconvert > .stage/greek.py

cd .stage/
chmod 755 flexy.py

./flexy.py `echo "$@" | $isoconvert` | $utfconvert
