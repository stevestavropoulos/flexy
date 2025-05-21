# Flexy - A tool to inflect and in other ways "flex" words.

The included `greek.py` file defines rules for Greek word inflection based on Triantafyllidis resources:
- [Triantafyllidis Grammar Rules](http://www.komvos.edu.gr/dictionaries/triantafyllidis/TriLegent.htm)  
- [Triantafyllidis Dictionary](http://www.greek-language.gr/greekLang/modern_greek/tools/lexica/triantafyllides/index.html)

## USAGE

```bash
python3 flexy.py [<options>] <word> [<rule id>]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -l LANGUAGE, --language=LANGUAGE
                        use LANGUAGE for rules definitions
  --list-rules          list all valid rules defined
```

## Test

You can test the greek rules with:
```bash
python3 tests/test_greek_samples.py
```
