```HTML
##########################################################
#                                                        #
# translate.py                                           #
#                                                        #
# This script translates the english version of          #
# the website. It creates a new language directory       #
# and makes a copy of the translated HTML pages          #
# into it. Uses the DeepL API.                           #
#                                                        #
# # pip install --upgrade deepl, yaml                    #
#                                                        #
##########################################################
```

A translation script made for the pirate.black website. Uses DeepL to translate the English version to other languages in the list.

Records the hash of each html source file, so only the source files that have been changed will be translated. 

This script is purpose built for a specific application, feel free to use to build on, but do not use blindly as is. 

DeepL free account is 500k characters a month. If all 26 languages and all html files are selected, that limit may be exceeded. If only certain files are edited, the free account should be enough for multiple translations a month

Example terminal output
```HMTL
langauge: Bulgarian | 1 of 26 | translating pages...
 - skipping    | source unchanged: branding.html
 - skipping    | source unchanged: community.html
 - skipping    | source unchanged: contact.html
 - skipping    | source unchanged: donations.html
 - skipping    | source unchanged: exchanges.html
 - skipping    | source unchanged: index.html
 - skipping    | source unchanged: mining.html
 - skipping    | source unchanged: privacypolicy.html
 - skipping    | source unchanged: terms.html
 - skipping    | source unchanged: wallets.html
 - skipping    | source unchanged: warrr.html
 - skipping    | source unchanged: whitepaper.html

langauge: Czech | 2 of 26 | translating pages...
 - skipping    | source unchanged: branding.html
 - skipping    | source unchanged: community.html
 - skipping    | source unchanged: contact.html
 ✓ translating | new file created: lang/cs/donations.html
 ✓ translating | new file created: lang/cs/exchanges.html
 ✓ translating | new file created: lang/cs/index.html
 ✓ translating | new file created: lang/cs/mining.html
 ✓ translating | new file created: lang/cs/privacypolicy.html
 ...
```