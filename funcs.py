import time 
import re
import os 
import json

# replace all whitespace with single spaces
def fix_whitespace(string : str) -> str:
    # some wizardry from https://stackoverflow.com/questions/2077897/substitute-multiple-whitespace-with-single-whitespace-in-python
    _RE_COMBINE_WHITESPACE = re.compile(r"(?a:\s+)")
    return _RE_COMBINE_WHITESPACE.sub(" ", string).strip()
    
# not used in gui
def safe_print(string : str, width : int, remaining_height : int) -> int:
    string = fix_whitespace(string)
    if remaining_height == 0:
        return 0
    elif remaining_height == 1:
        if len(string) > width:
            safe_print(string[:width-3]+"...", width, remaining_height)
            return 1
        else:
            print(string)
            return 1
    new_string = string.replace("\n", " ")
    if len(new_string) < width:
        print(new_string)
        return 1
    else:
        counter = min(width, len(new_string)-1)
        while (new_string[counter] != " ") and (counter > 0):
            counter -= 1
        if counter == 0:
            counter = width - 1
            print(new_string[:counter]+"-")
            return 1 + safe_print(new_string[counter+1:], width, remaining_height-1)
        print(new_string[:counter])
        return 1 + safe_print(new_string[counter+1:], width, remaining_height-1)

# remove all html tags from string
def scrub_html_tags(string : str) -> str:
    output = ""
    open = False
    for c in string:
        if (c == "<"):
            open = True
        elif (c == ">"):
            open = False
            output += " "
        elif not open:
            output += c
    while "  " in output:
        output = output.replace("  ", " ")
    return output

# run on separate thread; continuously loads next paper while there is a new paper to load
def background_load(reader) -> None:
    while True:
        if reader.load_next_unloaded_paper(): # if not done with current feed
            time.sleep(0.05)
        else: # wait longer for user to proceed to next feed
            time.sleep(5)

# pass a relative filepath from app's directory and a json file; if file exists, updates json file with info in directory, otherwise writes directory to file at location
def update_to_or_from_saved_json(filepath: str, dictionary: dict):
    # create absolute filepath from relative filepath    
    fullfilepath = os.path.join(os.getenv("HOME"), ".abstract-aggregator", filepath)
    # check if file already exists    
    if os.path.exists(fullfilepath):
        with open(fullfilepath, 'r') as f:
            dictionary.update(json.load(f))
    # otherwise, create associated json file
    else:
        with open(fullfilepath, 'w') as fout:
            fout.write(str(json.dumps(dictionary, indent=4, sort_keys=True,separators=(",",": "), ensure_ascii=False)))