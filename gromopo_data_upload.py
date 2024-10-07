# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 08:04:14 2023

@author: Kristen Jordan Koenig, GIS Developer, Kansas Geological Survey
@email: kristen.kgs@ku.edu
"""

import csv, sys, json
# edit this to an on-prem gromopo installation, subfolder GroMoPo\streamlit\pages
sys.path.append(r"C:\folder\GroMoPo\streamlit\pages") 
from submit_model import push_to_hydroshare
from os.path import join
from time import sleep

# edit this to the directory where the csv is stored
root_dir = r"C:\folder\folder"

# edit this to include the name of the csv file
csv_file = join(root_dir, "MyFile.csv")

# edit this to the folder where text files of records will be saved
upload_dir = r"C:\folder\of\text\files"

# # edit equivalencies so the keys are the names in the csv, values are Streamlit names
equiv = {"YourName": "SubmittedName", "YourEmail": "SubmittedEmail", 
         "OrigDev": "OriginalDev", "DevEmail": "DevEmail",
         "ModelYear": "ModelYear", "Model data availability": "DataAvail", 
         "Model Country": "ModelCountry", "Authors": "ModelAuthors", 
         "DOI": "DOI", "Scale": "ModelScale", "Layers": "Layers",
         "Bound_TopLeft": "Bound_TopLeft", "Bound_BottomRight": "Bound_BottomRight", 
         "Depth": "Depth", "ModelTime": "ModelTime", "Model code": "ModelCode",
         "Model purpose": "ModelPurpose", "Integration or coupling": "ModelIntegration", 
         "Model evaluation or calibration": "ModelEval",
         "Abstract": "Abstract", "Dominant geologic material": "ModelGeo", 
         "Geological input data available": "GeoAvail",
         "AddlInfo": "ModelAdditional",
         "PubTitle": "PubTitle", "ModelLink": "ModelLink", "ModelName": "ModelName",
         "DevCountry": "DevCountry", "ID": "GroMoPo_ID"
    }

# edit this to username and password of HydroShare account that will own the records
un = ""
pw = ""

def main():
    
    # open CSV
    # Open the input file 
    with open(csv_file, "r") as csv_stuff:
        #Set up CSV reader and process the header
        csvReader = csv.reader(csv_stuff, delimiter =',')
        header = next(csvReader)
      
        # Loop through the lines in the file and get each coordinate
        for row in csvReader:
            
            # for each record, start dictionary
            data = {"subjects": ["GroMoPo"]}
            
            # loop through the equivalency dictionary and populate data dictionary
            for key in equiv:
                
                # get the HydroShare upload term
                hs_term = equiv[key]
                
                # get the index
                keyIndex = header.index(key)
                
                val = ''
                
                if hs_term != "files":
                    # get the value
                    val = row[keyIndex]  
        
                data[hs_term] = val.strip()
                        
            # # generate a model title
            # # use ModelCountry, ModelCode, & first part of ModelEval
            # modelName = "GroMoPo metadata for " + "%s %s %s" % (data["ModelCountry"].split(";")[0], 
            #                 data["ModelCode"], 
            #                 data["ModelEval"].split(";")[0])
            
            # for char1 in ["(", ")", "'", '"']:
            #     if char1 in modelName:
            #         modelName = modelName.replace(char1, "")
                    
            # data["ModelName"] = modelName
            
            # need to turn model authors (1.8) into a list object
            ma = data["ModelAuthors"]
            if ";" in ma:
                ma_list = ma.split(";")
            else:
                if "," in ma:
                    ma_list = ma.split(",")
                else:
                    ma_list = [ma]
                    
            data["ModelAuthors"] = ma_list
            
            # turn coordinates into north, south, east, & west codes
            # turn coordinates into north, south, east, & west codes
            topLeft = data["Bound_TopLeft"]
            botRight = data["Bound_BottomRight"]

            if topLeft != '' and botRight != '':
                splitChar = ","

                if topLeft == "GLOBAL":
                    topLeft = "89.0, -179.0"
                    botRight = "-89.0, 179.0"

                if splitChar not in topLeft:
                    splitChar = ";"
                    
                coords1 = topLeft.split(splitChar)
                coords2 = botRight.split(splitChar)
                
                y1 = round(float(coords1[0]), 5)
                x1 = round(float(coords1[1]), 5)
                y2 = round(float(coords2[0]), 5)
                x2 = round(float(coords2[1]), 5)
                
                # figure out what goes where
                if x1 > x2:
                    east = x1
                    west = x2
                else:
                    east = x2
                    west = x1
                    
                if y1 > y2:
                    north = y1
                    south = y2
                else:
                    north = y2
                    south = y1

                data["North"] = north
                data["South"] = south
                data["East"] = east
                data["West"] = west
            
            # turn into lists
            for topic in ["ModelCode", "ModelPurpose", "ModelIntegration", "ModelEval"]:
                data[topic] = data[topic].split(";")
                data[topic + "2"] = []
                
            # some data cleanup 
            # data["LocDesc"] = data["ModelCountry"]
            
            if data["ModelTime"] == '':
                data["ModelTime"] = "SS"
                
            # create a text file of the original content
            file_name = data["GroMoPo_ID"] + "_%s %s %s.txt" % (data["ModelCountry"].split(";")[0], 
                            data["ModelCode"][0], 
                            data["ModelEval"][0])
                            
            # remove weird characters
            for char in [r"/", "\\", ")", "(", "'", '"']:
                if char in file_name:
                    file_name = file_name.replace(char, "")
            file_path = join(upload_dir, file_name)
            
            # make sure an abstract exists
            if data["Abstract"] == '':
                data["Abstract"] = data["PubTitle"]
            
            # write the data dictionary to the text file
            writeToText(file_path, prettyDict(data))
            
            # use text file as upload
            data["files"] = file_path
            data["t_un"] = un
            data["t_pw"] = pw
            
            # add the data to HydroShare
            push_to_hydroshare(data, method="csv")

            # print that it was added
            print("Added reocrd " + data["GroMoPo_ID"])
                
            # give the push to hydroshare a few extra seconds
            sleep(25)
            
            
def prettyDict(uglyDict):
     
    # Pretty Print JSON
    prettyDict = json.dumps(uglyDict, indent=4)
    return prettyDict
        

def writeToText(textFile, stuff):
    from os.path import exists
    from os import remove
    mode = "w"
    if exists(textFile):
        remove(textFile)
    FILE = open(textFile,mode)
    FILE.write(stuff)
    FILE.close()     
    

if __name__ == '__main__':
    main()