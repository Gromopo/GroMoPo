# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 13:53:41 2023

@author: k221j606_a
@documentation:
    geojson: https://github.com/jazzband/geojson
"""
import requests, zipfile
from geojson import Polygon, Feature, FeatureCollection, dumps
from geopandas import read_file
from os.path import exists, dirname, basename, join
from os import remove, listdir
from shutil import copy2
from hsclient import HydroShare

# set storage location
storage = r"E:\Kristen\Data\GroMoPo"

# define HydroShare index resource ID number
indexID = "114b76f89d1c41c38e0e235443c7544c"

# set HydroShare un & pw
un = ""
pw = ""

def ZipShp (inShp):

    """
    Creates a zip file containing the input shapefile
    inputs -
    inShp: Full path to shapefile to be zipped
    Delete: Set to True to delete shapefile files after zip
    KJK borrowed code from http://emilsarcpython.blogspot.com/2015/10/zipping-shapefiles-with-python.html on 8/17/2017
    """

    #List of shapefile file extensions
    extensions = [".shp",".shx",".dbf", ".sbn", ".sbx",".fbn",".fbx",".ain",".aih",".atx",".ixs",".mxs",".prj",".xml",".cpg"]

    #Directory of shapefile
    inLocation = dirname(inShp)
    #Base name of shapefile
    inName = basename(inShp)
    #Create zipfile name
    zipfl = join(inLocation, inName + ".zip")
    #Create zipfile object
    ZIP = zipfile.ZipFile(zipfl, "w")

    #Iterate files in shapefile directory
    for fl in listdir (inLocation):
        #Iterate extensions
        for extension in extensions:
            #Check if file is shapefile file
            if fl == inName + extension:
                #Get full path of file
                inFile = join(inLocation, fl)
                #Add file to zipfile
                ZIP.write (inFile, fl)
                break

    #Close zipfile object
    ZIP.close()

    #Return zipfile full path
    return zipfl


def getGeoJSONShape(stuffString):
    
    try:
    
        boxDict = stuffString[0]['value']
        
        poly = Polygon([[(boxDict['eastlimit'], boxDict['northlimit']),
                  (boxDict['eastlimit'], boxDict['southlimit']),
                  (boxDict['westlimit'], boxDict['southlimit']),
                  (boxDict['westlimit'], boxDict['northlimit']),
                  (boxDict['eastlimit'], boxDict['northlimit'])]])
        # example from documentation
        # Polygon([[(2.38, 57.322), (-120.43, 19.15), (23.194, -20.28), (2.38, 57.322)]])
    except:
        poly="nope"
    
    return poly
        
        
def writeToText(textFile, stuff):
    mode = "w"
    if exists(textFile):
        mode = "a"
    FILE = open(textFile,mode)
    FILE.write(stuff)
    FILE.close()
    

def updateHSfiles(geojson, shp):
    
    hs_id = indexID
    
    hs = HydroShare(un, pw)
    
    record = hs.resource(hs_id)
    
    # Upload one or more files to your resource 
    record.file_upload(geojson, shp)
 
        
def main():
    # query data out of hydroshare
    
    # start by querying for data with the GroMoPo tag
    tag = 'GroMoPo'
    
    # url = 'https://www.hydroshare.org/hsapi/resource/?subject=%s&edit_permission=false&published=false&include_obsolete=false' % tag
    url = 'https://www.hydroshare.org/hsapi/resource/?subject=%s' % tag
    
    hs_gmp_results = []
    new_results = True
    page = 1
    
    # loop through pages of results
    while new_results:
        hs_api = requests.get(url + f"&page={page}").json()
        new_results = hs_api.get("results", [])
        hs_gmp_results.extend(new_results)
        page += 1
    
    
    # set file paths
    geojson = join(storage, "GroMoPo_MapData.json")
    shp = join(storage, "GroMoPo_MapData.shp")
    issuesTxt = join(storage, "GMP_Mapping_Issues.txt")
        
    # create lists for storage
    features = []
    issues = []
    
    # set up HydroShare session
    hs = HydroShare(un, pw)
    
    # loop through the results & create list of features
    for result in hs_gmp_results:
        
        # make geometry
        geom = getGeoJSONShape(result["coverages"])
        if geom=="nope":
            issues.append(result["resource_id"])
            
        else:
        
            # get properties
            props = {"id": result["resource_id"],
                     "devdate": result["date_created"],
                     "name": result["resource_title"],
                     "url": result["resource_url"],
                     "hsuser": result["creator"],
                     # "spscale": result[""], # in additional metadata
                     "abstract": result["abstract"][0:253]
                     # "archive": result[""],
                     # "coupling": result[""],# in additional metadata
                     #"contribu_1": result["author"] # see below
                     }
            
            # get authors as a string
            if len(result["authors"]) > 1:
                lstAuthors = result["authors"][1:]
                authors = ", ".join(lstAuthors)
                
            else:
                if result["authors"] != [None]:
                    authors = result["authors"][0]
                else:
                    authors = ""
                    
            props["contribu1"] = authors
            
            # get attributes from additional metadata
            
            # spatial scale- Scale
            # verification- IsVerified
            # coupling- Integration or Coupling
            # authors- Model Authors
            
            # get record from HydroShare using resource ID
            record = hs.resource(props["id"])
            
            addlMetadata = record.metadata.additional_metadata
            
            # key: attribute name in HydroShare additional metadata
            # value: attribute name in GroMoPo shapefile & geojson
            addlM_dict = {"Scale": "spscale",
                          "IsVerified": "gmpverify",
                          "Integration or Coupling": "coupling",
                          "Model Authors": "authors"}
            
            for hs_key in addlM_dict:
                shp_key = addlM_dict[hs_key]
                
                # make sure the HydroShare key exists
                if hs_key in addlMetadata:
                    # if the value is in the HydroShare additional metadata,
                    # add it to the shapefile properties dictionary
                    value = addlMetadata[hs_key][0:253]
                    
                    # standardize values
                    if value == "None of the above":
                        value = "N/A"
                        
                    props[shp_key] = value
                else:
                    if "Verified" not in hs_key:
                        props[shp_key] = "N/A"
                    else:
                        props[shp_key] = "False"
                        
            del record, addlMetadata, addlM_dict
            
            if props["id"] != indexID:
            
                # create a geojson feature
                feature = Feature(geometry=geom,properties=props)
                
                features.append(feature)
                
    # clear out old files
    #extensions = ["json", "shp", "cpg", "dbf", "shx", "prj"]
    for f in [geojson, shp, shp.replace(".shp", ".cpg"), 
              shp.replace(".shp", ".dbj"),
                shp.replace('.shp', ".shx"), shp.replace(".shp", ".prj"), issuesTxt]:
        if exists(f):
            remove(f)
        
    # turn list of features into a geojson feature collection
    gmp_fc = FeatureCollection(features)
    
    # create dump
    gmp_dump = dumps(gmp_fc)
    
    # write dump to geojson file
    writeToText(geojson, gmp_dump)
    
    # convert to shapefile
    gdf = read_file(geojson)
    gdf.to_file(shp)
    
    # zip up shapefile
    zippedShp = ZipShp(shp)

    # write down IDs of records that couldn't be mapped
    for issueID in issues:
        writeToText(issuesTxt, issueID + "\n")
        
    # copy geojson to freeze
    freezeLoc = "Z:\KgsMaps\GroMoPo\GroMoPo_MapData.json"
    if exists(freezeLoc):
        remove(freezeLoc)
    copy2(geojson, freezeLoc)
    
    print("Copied geojson to freeze")
    
    # update shp and geojson in HydroShare
    updateHSfiles(geojson, zippedShp)
            
if __name__ == '__main__':
    main()
    
