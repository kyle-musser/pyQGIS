#imports
import os
from qgis import processing

# !!! NOTE: Need to run script 1.0 first to get the cenblock buffer shapefiles. 

#change directory.
os.chdir(r"D:/Dropbox/RA folder/raw_data/mapping/cenBlock")

# List of state fips to loop through
#list of fips codes to loop
fips = ["01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "44", "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56"]
for stFip in fips:
    
    print(stFip)
    
    #Make BASE State file name
    baseFL = "tl_2018_" + stFip + "_tabblock10"
    
    #cenblock shapefile
    cenBlockDeleteColsFL = "D:/cenBlock/del/" + baseFL + "_colDel.gpkg"
    
    #Make Centroids from each Reprojected Census Block File
    centroids = processing.run("native:centroids", { 'ALL_PARTS' : True,
        'INPUT' : cenBlockDeleteColsFL,
        'OUTPUT' : 'TEMPORARY_OUTPUT'}
    )
    
    reproj = processing.run("native:reprojectlayer", { 'INPUT' : centroids['OUTPUT'],
        'OPERATION' : '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=aea +lat_0=40 +lon_0=-96 +lat_1=20 +lat_2=60 +x_0=0 +y_0=0 +ellps=GRS80',
        'OUTPUT' : 'TEMPORARY_OUTPUT',
        'TARGET_CRS' : QgsCoordinateReferenceSystem('ESRI:102008')} 
    )
    
    #cenblock population file
    cenBlkTbl = 'D:/Dropbox/RA folder/raw_data/mapping/cenBlock/CenBlock_pop_P8_2010Cen' + stFip + '.csv'
    
    #outfile
    outFL = 'D:/cenBlock/delWpop/blkCenWpop' + stFip + '.gpkg'
    
    temp = processing.run("native:joinattributestable", 
        { 'DISCARD_NONMATCHING' : False, 'FIELD' : 'geoid10', 'FIELDS_TO_COPY' : [],
        'FIELD_2' : 'GEOID10',
        'INPUT' : reproj['OUTPUT'],
        'INPUT_2' : cenBlkTbl,
        'METHOD' : 1,
        'OUTPUT' : 'TEMPORARY_OUTPUT',
        'PREFIX' : '' }
    )
    
    processing.run("native:refactorfields",
        { 'FIELDS_MAPPING' : [{'expression': '\"fid\"','length': 0,'name': 'fid',
        'precision': 0,'type': 4},
        {'expression': '\"GEOID10\"','length': 15,'name': 'GEOID10','precision': 0,'type': 10},
        {'expression': '\"pop_tot\"','length': 0,'name': 'pop_tot','precision': 0,'type': 4},
        {'expression': '\"pop_whtAlone\"','length': 0,'name': 'pop_whtAlone','precision': 0,'type': 4},
        {'expression': '\"pop_blkAlone\"','length': 0,'name': 'pop_blkAlone','precision': 0,'type': 4},
        {'expression': '\"pop_aianAlone\"','length': 0,'name': 'pop_aianAlone','precision': 0,'type': 4},
        {'expression': '\"pop_whtCombo\"','length': 0,'name': 'pop_whtCombo','precision': 0,'type': 4},
        {'expression': '\"pop_blkCombo\"','length': 0,'name': 'pop_blkCombo','precision': 0,'type': 4},
        {'expression': '\"pop_aianCombo\"','length': 0,'name': 'pop_aianCombo','precision': 0,'type': 4},
        {'expression': '\"pop_hispCombo\"','length': 0,'name': 'pop_hispCombo','precision': 0,'type': 4},
        {'expression': '\"GEOID10_2\"','length': 0,'name': 'GEOID10_2','precision': 0,'type': 10}],
        'INPUT' : temp['OUTPUT'],
        'OUTPUT' : outFL }
    )
    
     #create spatial index to speed up processing in next steps
    processing.run("native:createspatialindex", {'INPUT' : outFL})
    
   
        
    
    