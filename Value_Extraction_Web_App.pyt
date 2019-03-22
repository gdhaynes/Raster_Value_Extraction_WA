# Value_Extraction.pyt
# Version: II
# Spring 2019
# Author: Grant Haynes  
# grant.d.haynes@wmich.edu
# 
# Arc Version:
# This tool was developed and tested with Arcmap 10.6
#
# IDE:
# This tool was developed in Visual Studio Code
#
# Purpose:
# This tool will extract values of rasters in a folder and create a resulting feature 
# class with a related table of temporal data. This service will be used in a web app
#-----------------------------------------------------------------------------

# Start script
#-----------------------------------------------------------------------------
import arcpy
import os

# Tool initialization
#-----------------------------------------------------------------------------
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Value_Extraction_Tool"
        self.alias = "Value Extraction Tool"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]

class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Value Extraction Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        DataSource = arcpy.Parameter(
		    displayName="DataSource",
		    name="DataSource",
		    datatype="DEWorkspace",
		    parameterType="Required",
		    direction="Input")

        InputPoint = arcpy.Parameter(
            displayName="InputPoint",
		    name="InputPoint",
		    datatype="DEFeatureClass",
		    parameterType="Required",
		    direction="Input")

        OutputFC = arcpy.Parameter(
            displayName="OutputFC",
		    name="OutputFC",
		    datatype="DEFeatureClass",
		    parameterType="Required",
		    direction="Output")

        params = [DataSource, InputPoint, OutputFC]
        return params

    def isLicensed(self):
        # Set whether tool is licensed to execute.
        return True

    def updateParameters(self, parameters):
        # Modify the values and properties of parameters before internal
        # validation is performed.  This method is called whenever a parameter
        # has been changed.
        return

    def updateMessages(self, parameters):
        #Modify the messages created by internal validation for each tool
        #parameter.  This method is called after internal validation.
        return

    def execute(self, parameters, messages):
        arcpy.env.overwriteOutput = True

        # User input arguments
        DataSource = parameters[0].valueAsText
        InputPoint = parameters[1].valueAsText
        OutputFC = parameters[2].valueAsText 

        # Handle all input point procesing
        arcpy.CopyFeatures_management(InputPoint, OutputFC)
        
        # Add fields to hold temporal data
        arcpy.AddField_management(OutputFC, "LABEL", "TEXT")
        arcpy.AddField_management(OutputFC, "VALUE", "SHORT")

        # Loop through geometry attributes and get the x and y
        with arcpy.da.SearchCursor(InputPoint,['SHAPE@X', 'SHAPE@Y']) as cursor:
            PointIndex = 1
            for row in cursor:
                X = row[0]
                Y = row[1]

                # Get rasters and extract data at an X and Y        
                index = 0
                for (path, dirs, files) in os.walk(DataSource):
                    for ThisFile in files:
                        fName,fExt = os.path.splitext(ThisFile)
                        if fExt.upper() == ".IMG" or fExt.upper() == ".TIF":
                            RasterPath = path + "\\" + ThisFile      
                            data = (arcpy.GetCellValue_management(RasterPath, str(X) + " " + str(Y), "").getOutput(0))
                            aquisition_date = arcpy.GetRasterProperties_management(in_raster = RasterPath, property_type = "ACQUISITIONDATE")

                            if str(aquisition_date).upper() == "UNKNOWN":
                                insertcursor = arcpy.InsertCursor(OutputFC)
                                row = insertcursor.newRow()
                                row.setValue("LABEL", "{}, Point: {}".format(index, PointIndex))
                                if data.isdigit() == True:
                                    row.setValue("VALUE", int(data))
                                insertcursor.insertRow(row)
                                del insertcursor
                                index += 1

                PointIndex += 1
        return