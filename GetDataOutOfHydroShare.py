# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 13:53:41 2023

@author: k221j606_a
"""
import requests
from arcpy.da import InsertCursor
from arcpy import SpatialReference, Array, Polygon, Point

def getShape(stuffString, sr):
    boxDict = stuffString[0]['value']
    
    array = Array([Point(boxDict['eastlimit'], boxDict['northlimit']),
              Point(boxDict['eastlimit'], boxDict['southlimit']),
              Point(boxDict['westlimit'], boxDict['southlimit']),
              Point(boxDict['westlimit'], boxDict['northlimit']),
              Point(boxDict['eastlimit'], boxDict['northlimit'])])
    
    poly = Polygon(array, sr)
    
    return poly

def main():
    
    # query data out of hydroshare
    
    # start by querying for data with the GroMoPo tag
    tag = 'GroMoPo'
    
    url = 'https://www.hydroshare.org/hsapi/resource/?subject=%s&edit_permission=false&published=false&include_obsolete=false' % tag
    
    r = requests.get(url)
    
    content = r.json()
    
    if int(content["count"]) > 0:
        
        # start an insert cursor
        fc = "E:\Kristen\Data\GroMoPo_output.shp"
        fields = ('ResourceID', 'Authors', 'Title', 'Abstract', 'HSLink', 'SHAPE@')
        cursor = InsertCursor(fc, fields)
        sr = SpatialReference(4326)
        
        # get the results
        results = content["results"]
        
        print(len(results))
        
        # loop through the results
        for result in results:
            
            # get string of authors
            lstAuthors = result["authors"]
            authors = ", ".join(lstAuthors)
            
            # get the polygon
            newPoly = getShape(result["coverages"], sr)
            newInfo = (result["resource_id"], authors, result['resource_title'],
                        result['abstract'], result['resource_url'], newPoly)
            
            print(newInfo)
            
            cursor.insertRow(newInfo)

        del cursor

if __name__ == '__main__':
    main()