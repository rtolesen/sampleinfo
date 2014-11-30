#!/usr/bin/python
'''
    Copyright(C): Rasmus Thisgaard Olesen (rtolesen@gmail.com)

    Created on 2014/10/19
    @author: Rasmus Thisgaard Olesen
'''
"""
Running this script will create an attribution text file in the current working
directory. 

It is named after the sample it contains attributions for by appending 
"_attribution.txt" to a sample name which the user is prompted for.

If "--path" is given at the command line, and a path is supplied 
the user can append attributions to an already existing file created by the
script.

There are 2 modes for inputting attribution information. Either manually as 
prompted by the script, or by inputting a freesound.org identifier number, in 
which case the attribution is automatically created.
 
Information about the different licenses is hard coded, so the script will 
have to be changed if additional licenses are to be supported. 

Currently creative commons 0-1.0(public domain), BY-3.0, and BY-4.0 are 
recognized since those are the ones I've had to use.  
"""
import argparse
import json

import requests


attribution_entry_sortmap = {"Original filename" : 1, "License" : 2, 
                             "License link" : 3, "Author" : 4, 
                             "Obtained from" : 5, "Changed" : 6} 

# The boolean values for each field state if is required to be filled out. 
#This is only for user information, isn't checked
licenselist = {"CC-BY-4.0" : {"Author" : True, "Obtained from" : True, 
                              "Original filename" : True, "Changed" : True}, 
               "CC-BY-3.0" : {"Author" : True, "Obtained from" : True, 
                              "Original filename" : True, "Changed" : True},
               "CC0-1.0" : {"Author" : False, "Obtained from" : False, 
                            "Original filename" : False, "Changed" : False},
               }

licenselinks = {"CC-BY-4.0" : "http://creativecommons.org/licenses/by/4.0/legalcode", 
               "CC-BY-3.0" : "https://creativecommons.org/licenses/by/3.0/legalcode",
               "CC0-1.0" : "http://creativecommons.org/publicdomain/zero/1.0/legalcode",
               }


def get_api_key():
    """
    Hard coded api key from freesound.org. If you use this script a lot you should
    go get your own key I guess, it's very easy to do.
    """
    return "7fdbcc412cfc5bfbff2bfbaba224c29199d28f64"


def is_valid_input(filepath):
    """
    Check if command line input is a valid text file created by this script 
    """
    with open(filepath, "r") as file:
        for line in file:
            if line=="THIS FILE IS CREATED BY SAMPLEINFO.PY, ALTERING THIS LINE MAY CAUSE PROBLEMS\n":
                return filepath
            else:
                pass
        #The above line is not in the file so loop doesn't return
        raise SystemExit("Input does not appear to be a the location of a valid text file created by the sampleinfo.py script")


def run_script():
    """
    If the user answers ("n") without adding any attributions, an empty text file
    is created.         
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=is_valid_input, 
                        help="Location of an existing attribution text file, to which these attributions are to be added.")
    args = parser.parse_args()
    
    out_file_name = ""
    path_to_file = ""
    attributions = []
    
    if args.path == None:
        samplename = input("Name of sample?:")
        out_file_name = samplename + "_attribution.txt"
    else:
        path_to_file = args.path
    
    
    def add_by_freesound_id():
        apiKey = get_api_key()
        try:
            freesound_id = input("Freesound ID (number): ") 
            link = "http://www.freesound.org/apiv2/sounds/"+ freesound_id + "/?fields=name,url,license,username&format=json&token=" + apiKey
            response = requests.get(link)
            content = json.loads(response.content.decode())
            attribution_entry = {"Author":content["username"],"Original filename":content["name"], 
                             "License" : content["license"], "Obtained from":content["url"]}
            changed = input("Changed from original?: ")
            attribution_entry["Changed"] = changed
            attributions.append(attribution_entry)
        except: 
            print("bad ID?")
                

    def add_manual():
        menuitems = []
        menuindex = 0
        print("Valid licenses:")
        for identifier in sorted(licenselist.keys()):
            menuitems.append(identifier)  
            print("[" + str(menuindex) + "]" + ": " + identifier)
            menuindex += 1
        
        try:    
            identifier = menuitems[int(input("License?: "))]
            attribution_entry = {"License" : identifier, "License link" : licenselinks[identifier]}
            for field in licenselist[identifier]:
                if(licenselist[identifier][field]):# is required field as defined in licenselist
                    attribution_entry[field] = input("(Required)" + field + "?:")
                else:
                    attribution_entry[field] = input("(Optional)" + field + "?:")
            attributions.append(attribution_entry) 
        except (ValueError, IndexError) as e:
            print("Input doesn't make sense!")
            print(e)
    
    
    def add_attribution():
        menuitems = ["Manual", "By FreeSound ID"]
        menuindex = 0
        print("Method of adding attribution:")
        for method in menuitems:
            print("[" + str(menuindex) + "]" + ": " + method)
            menuindex += 1
            
        try: 
            userinput = int(input("Choice: ")) 
            if userinput == 0:
                add_manual()
            elif userinput == 1:
                add_by_freesound_id()
            else:
                print("Input not understood, doing nothing")
        except ValueError:
            print("Input is not a number")
    
    
    while True:
        userinput = input("Add attribution?(y/n):").lower()
        if userinput in ["y","n"]:  
            if userinput == "y":
                add_attribution()
            else:
                break
        else: #unacceptable input
            pass
        
## A bit complicated, but it's all in an effort to get the lines in the file sorted as I like
    if args.path == None: 
        with open(out_file_name, "w") as outfile:
            outfile.write("THIS FILE IS CREATED BY SAMPLEINFO.PY, ALTERING THIS LINE MAY CAUSE PROBLEMS\n")
            outfile.write("\n")
            for attribution in attributions:
                strings = []*len(attribution_entry_sortmap)#long enough for all entries
                for field in attribution:
                    string = (str(field)+": " + attribution[field])
                    strings.insert(attribution_entry_sortmap[field]-1, string)#sort 
                strings.append("\n")
                outfile.write("\n".join(str(x) for x in strings)) 
    else:
        with open(path_to_file, "a") as outfile:
            outfile.write("\n")
            for attribution in attributions:
                strings = []*len(attribution_entry_sortmap)#long enough for all entries
                for field in attribution:
                    string = (str(field)+": " + attribution[field])
                    strings.insert(attribution_entry_sortmap[field]-1, string)#sort 
                strings.append("\n")
                outfile.write("\n".join(str(x) for x in strings))   
        
        
if __name__ == '__main__':     
    run_script()
    

