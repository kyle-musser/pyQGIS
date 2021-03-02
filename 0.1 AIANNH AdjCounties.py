#NOTE: Script is indended to be run within the qgis python console.

#imports
import os
from qgis import processing


os.chdir(r"C:/Users/kylem/Dropbox/Frye_Parker_DataCollection/data/gis")


#Filepath for AIANNH and County Shapefiles
#NOTE Using 2017 reservtion and counties but should be constant from 2010-2019.
aiannhFL = 'tl_2017_us_aiannh'
cntyFL = 'tl_2017_us_county'

#Reproject both County and AIAN Files and create spatial index
for FILE in [aiannhFL, cntyFL]:
    
    #APPend .shp onto filename
    FileIN = FILE + ".shp"
    
    #Make FileOut NAme after Reproject to Alberts Equal Area
    FileOut = FILE + "Reproj.shp"

    #Then reproject to Alberts Equal Area
    processing.run("native:reprojectlayer", { 'INPUT' : FileIN,
        'OPERATION' : '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=aea +lat_0=40 +lon_0=-96 +lat_1=20 +lat_2=60 +x_0=0 +y_0=0 +ellps=GRS80',
        'OUTPUT' : FileOut,
        'TARGET_CRS' : QgsCoordinateReferenceSystem('ESRI:102008')} 
    )
    
    #Make Spatial Index so Buffer Runs Faster
    processing.run("native:createspatialindex", {'INPUT' : FileOut})



#Dissolve Reprojected Reservation Shapefile into AIANHCE (One Feature for each 4 digit "GEO ID")
DissolveFL = aiannhFL + "Dissolve.shp"
processing.run("native:dissolve",
    {'FIELD' : ['AIANNHCE'],
    'INPUT' : 'tl_2017_us_aiannhReproj.shp',
    'OUTPUT' : DissolveFL }
)

#Calculate Geomerry Attributes for AIAN area
processing.run("qgis:exportaddgeometrycolumns",
    { 'CALC_METHOD' : 1,
    'INPUT' : 'tl_2017_us_aiannhDissolve.shp',
    'OUTPUT' : 'tl_2017_us_aiannhDissolve2.shp' }
)

 
#Now Make 25 Mile Buffers Around Reservation 
BufferFL = aiannhFL + "Buffer.shp"
processing.run("native:buffer",
    { 'DISSOLVE' : False,
    'DISTANCE' : 40233.6,
    'END_CAP_STYLE' : 2, 
    'INPUT' : 'tl_2017_us_aiannhDissolve2.shp',
    'JOIN_STYLE' : 0,
    'MITER_LIMIT' : 2,
    'OUTPUT' : BufferFL,
    'SEGMENTS' : 10 }
)

#Calculate Geomerry Attributes for AIAN Buffer
processing.run("qgis:exportaddgeometrycolumns",
    { 'CALC_METHOD' : 1,
    'INPUT' : 'tl_2017_us_aiannhBuffer.shp',
    'OUTPUT' : 'tl_2017_us_aiannhBuffer2.shp' }
)


#Calculate Geomerry Attributes for County
processing.run("qgis:exportaddgeometrycolumns",
    { 'CALC_METHOD' : 1,
    'INPUT' : 'tl_2017_us_countyReproj.shp',
    'OUTPUT' : 'tl_2017_us_countyReproj2.shp' }
)



#Then Intersect counties with the buffer file of AIAN
#To find counties that intersect w/ reservations. 
processing.run("native:intersection",
    { 'INPUT' : 'tl_2017_us_aiannhBuffer2.shp',
    'INPUT_FIELDS' : [],
    'OUTPUT' : 'tl_2017_us_aiannhIntersect.shp',
    'OVERLAY' : 'tl_2017_us_countyReproj2.shp',
    'OVERLAY_FIELDS' : [],
    'OVERLAY_FIELDS_PREFIX' : 'CNTY_' }
)



#Now Calculate Geometric Attributes one more time to get 
#The percent the county overlaps with each reservation buffer.
#Calculate Geomerry Attributes for AIAN
processing.run("qgis:exportaddgeometrycolumns",
    { 'CALC_METHOD' : 1,
    'INPUT' : 'tl_2017_us_aiannhIntersect.shp',
    'OUTPUT' : 'tl_2017_us_aiannhIntersect2.shp'}
)

#Then do it the opposite way w/ Counties as the Input

processing.run("native:intersection",
    { 'INPUT' : 'tl_2017_us_countyReproj2.shp',
    'INPUT_FIELDS' : [],
    'OUTPUT' : 'tl_2017_us_countyIntersect.shp',
    'OVERLAY' : 'tl_2017_us_aiannhBuffer2.shp',
    'OVERLAY_FIELDS' : [],
    'OVERLAY_FIELDS_PREFIX' : 'AIAN_' }
)

processing.run("qgis:exportaddgeometrycolumns",
    { 'CALC_METHOD' : 1,
    'INPUT' : 'tl_2017_us_countyIntersect.shp',
    'OUTPUT' : 'tl_2017_us_countyIntersect2.shp'}
)
