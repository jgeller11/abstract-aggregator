# abstract aggregator

## what is this
this is a wip app to aggregate and display abstracts from a few journals, including a feature to rank the abstracts according to preferences set by user for what sort of terms/authors/journals are most interesting

## setup
before using this you're going to need to update everything in `params.py`. eventually it will be possible to edit this all within the app but for testing this is what we've got

## usage
in app, use left/right arrows to proceed to next/previous paper in current feed, up arrow to open the webpage associated with a paper, down arrow to download the paper automatically (if allowed by the journal) and write a citation to your .bib file, `.` key to move to the previous day/feed, `Return` key to move to the next day/feed. it will be possible to modify all these keybindings in app eventually but for now they must be modified in `params.py`. `q` key quites the program.

can press `s` to open a settings menu where these keybindings can be re-written, but be warned that this menu is barely functional as of now. click a button until it says "listening", at which point you can press your new key.

## build to .app:
must work in python >=3.11 environment with `bibtexparser`, `html5lib`, `bs4`, `requests`, `feedparser`, and `pyinstaller`

run `pyinstaller build.spec`
