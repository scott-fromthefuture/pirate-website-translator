#!/usr/bin/env python3
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

import yaml
import deepl
import re
import os
import hashlib
import json
from os.path import exists

# configuration
skip_unchanged = True # Only translate if source has been translated previously, and is unchanged since.
deepl_key = ''
translation_target_dir = "lang/"
sourcehash_db = "sourcehash.db"

source_files = [
    'branding.html',
    'community.html',
    'contact.html',
    'donations.html',
    'exchanges.html',
    'index.html',
    'mining.html',
    'privacypolicy.html',
    'terms.html',
    'wallets.html',
    'warrr.html',
    'whitepaper.html']

front_matter_to_translate = [
    "keywords",
    "description"]

languages = {
    "BG": "Bulgarian",
    "CS": "Czech",
    "DA": "Danish",
    "DE": "German",
    "EL": "Greek",
    "ES": "Spanish",
    "ET": "Estonian",
    "FI": "Finnish",
    "FR": "French",
    "HU": "Hungarian",
    "ID": "Indonesian",
    "IT": "Italian",
    "JA": "Japanese",
    "LT": "Lithuanian",
    "LV": "Latvian",
    "NL": "Dutch",
    "PL": "Polish",
    "PT": "Portuguese",
    "RO": "Romanian",
    "RU": "Russian",
    "SK": "Slovak",
    "SL": "Slovenian",
    "SV": "Swedish",
    "TR": "Turkish",
    "UK": "Ukrainian",
    "ZH": "Chinese"}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir)) + "/"

translator = deepl.Translator(deepl_key)

# make PT into PT-PT fopr deepl
def dlc(target_lang):
    if target_lang.upper() == "PT":
        target_lang = "PT-PT"
    return target_lang

# store the dict of source hashes in  file
def saveHashDB(hashdb):
    with open(sourcehash_db, "w") as outfile:
        # Write the dictionary to the file in JSON format
        json.dump(hashdb, outfile)

# get source hashes to a dict
def getHashDB():
    hashdb = {}
    if os.path.isfile(sourcehash_db):
        # Open the file for reading
        with open(sourcehash_db, "r") as infile:
            # Load the contents of the file into a dictionary
            hashdb = json.load(infile)
    return hashdb

# convert fornt matter string to a dict
def front_matter_to_dict(front_matter_str):
     front_matter_dict = yaml.safe_load(front_matter_str)
     return front_matter_dict


# convert dict to front matter string
def dict_to_front_matter(front_matter_dict):
    front_matter_str = yaml.dump(front_matter_dict, default_flow_style=False)
    return '---\n' + front_matter_str + '---\n'


# read the front matter from html, then convert to dict
def read_front_matter(html):
    front_matter_str = re.search(r'---\n(.*?)\n---', html, re.DOTALL)
    if front_matter_str:
        front_matter_str = front_matter_str.group(1)
        front_matter_dict = front_matter_to_dict(front_matter_str)
    else:
        front_matter_dict = ""
    return front_matter_dict


# create the target directory and copy over the source HTML
def prepareFile(source_file, target_file, target_lang):

    # get the target path
    target_dir = str(os.path.split(target_file)[0]) + "/"

    # open source file
    with open(BASE_DIR + source_file, 'r') as file:
        source_html = file.read()

    # create directory
    if not os.path.exists(BASE_DIR + target_dir):
        os.makedirs(BASE_DIR + target_dir)

    # remove front matter
    prepared_html = re.sub(r'---\n(.*?)\n---', '', source_html, flags=re.DOTALL)

    # write source file
    with open(BASE_DIR + target_file + ".tmp.html", 'w') as new_file:
        new_file.write(prepared_html)

    return source_html


# translate a string of text
def translate_text(text, target_lang):

    translated_text = translator.translate_text(
        text,
        source_lang="EN", 
        target_lang=dlc(target_lang).upper(),
        preserve_formatting=1)
    return translated_text


# translate meta in front matter
def translate_front_matter(front_matter, target_lang):
    # check if front matter key is in list to translate
    for key, val in front_matter.items():
        if key in front_matter_to_translate:
  
            # send string for translation
            translation = translate_text(val, target_lang)
            front_matter[key] = translation.text
    
    return front_matter


# translate the html document
def translate_html(target_path, target_lang):
    try:
        # Using translate_document_from_filepath() with file paths 
        tmp_file = target_path + ".tmp.html"
        translator.translate_document_from_filepath(
            BASE_DIR + tmp_file,
            BASE_DIR + target_path,
            source_lang="EN",
            target_lang=dlc(target_lang).upper())
        os.remove(BASE_DIR + tmp_file)

    except deepl.DocumentTranslationException as error:
        # If an error occurs during document translation after the document was
        # already uploaded, a DocumentTranslationException is raised. 
        doc_id = error.document_handle.id
        doc_key = error.document_handle.key
        print(f"Error after uploading ${error}, id: ${doc_id} key: ${doc_key}")
        return False
    except deepl.DeepLException as error:
        # Errors during upload raise a DeepLException
        print("deepl exception: " + str(error))
        return False

    return True


# Insert the translated front matter back into the translated HTML
def inject_front_matter(translated_front_matter, target_file):
    # convert front matter dict to string
    front_matter = dict_to_front_matter(translated_front_matter)

    append_copy = open(BASE_DIR + target_file, "r")
    html = append_copy.read()
    append_copy.close()

    append_copy = open(BASE_DIR + target_file, "w")
    append_copy.write(front_matter)
    append_copy.write(html)
    append_copy.close()


# main translation process
def translate(source_file, target_file, target_lang):

    # open source file, and move to new directory
    source_html = prepareFile(source_file, target_file, target_lang)    

    # get front matter and update language
    front_matter = read_front_matter(source_html)
    front_matter["lang"] = target_lang.lower()

    # translate each front matter
    translated_front_matter = translate_front_matter(front_matter, target_lang)

    # translate html
    translation_success = translate_html(target_file, target_lang)
    if not translation_success:
        print(f" x ALERT!!!!   | translation failed for {source_file}")
        return

    # add transalted front matter to translated file
    inject_front_matter(translated_front_matter, target_file)

    return


# get a hash of each source file 
# so we can translate only changed files
def updateSourceHash(source_files):

    # set a couple vars
    hasher = hashlib.md5()
    new_hashes = {}

    # get a dict of hashes for each source file
    for source_file in source_files:
        # open source file in binary mode
        with open(BASE_DIR + source_file, 'rb') as file:
            buffer = file.read()
        
        # hash the file
        hasher.update(buffer)
        hash = hasher.hexdigest()

        # store the new hash
        result = {"changed": True, "hash": hash}
        new_hashes[source_file] = result

    # get the stored hashes
    hashdb = getHashDB()

    # compare new and old hashes
    for filename,data in new_hashes.items():
 
      
        # if the file is already in the hashdb
        if filename in hashdb:
            old_hash = hashdb[filename]["hash"]
            new_hash = new_hashes[filename]["hash"]

            # if they matched, it is unchanged
            if old_hash == new_hash:
                hashdb[filename]["changed"] = False

            # if they dont match, update the hashdb
            else:
                hashdb[filename]["changed"] = True
                old_hash = new_hash

        # if the file is not in there, add it       
        else:
            hashdb[filename] = data

    saveHashDB(hashdb)
    return hashdb


# check if the hash for the source file has changed
def checkSourceChange(source_file, source_hash):
    # check if source file is in the hashes
    changed = True
    if source_file in source_hash:
        changed = source_hash[source_file]["changed"]
    return changed

# controller iterates through languages translated
def controller():

    total_langs = len(languages)
    lang_count = 0

    # check hash of source files
    source_hash = updateSourceHash(source_files)

    # iterate through languages
    for symbol,name in languages.items():
        lang_count += 1
        print(f"\nlangauge: {name} | {lang_count} of {total_langs} | translating pages...")

        # translate each page in this language
        for source_file in source_files:

            # define file names and paths
            target_dir = translation_target_dir + symbol.lower() + "/"
            file_name = os.path.basename(source_file)
            target_file = target_dir + file_name           

            # check if page needs translated
            changed = checkSourceChange(source_file, source_hash)
            translation_exists = exists(BASE_DIR + target_file)

            if skip_unchanged and not changed and translation_exists:
                print(f" - skipping    | source unchanged: {source_file}")
                continue
            else:
                # translate
                translate(source_file, target_file, symbol)       
                print(f" ✓ translating | new file created: {target_file}")

# send it
if __name__=="__main__":
    controller()