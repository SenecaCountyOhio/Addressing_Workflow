The goal of this tool is to automate the process of assigning addresses.
The tool will determine many of the attributes to an address.
Ex: House Number, Mailing City, Zip Code, Township, etc.
The script is loaded into the SenCO_Addressing_Script Tool in County_Addressing.tbx

To use the tool:
1) Create a new address point
2) Save edits
3) Open the SenCo_Addressing_Script Tool
4) Select the new addreess point and the road centerline the address will be on
5) Drag the selected address and road layers into the corresponding parameters
6) Fill out all the rest of the parameters
7) Click Run
8) Double check the new address output


Required Data Layers to run tool:
Addresses
Roads
Addressing Grid (Must be in GDB)
Township Sections (Must be in GDB)
Zip Districts (Must be in GDB)

NOTE: The user can set the path of the GDB. However, the layers that must be in GDB must be named what is described below.

Project Folder Path = B:\Projects\Addressing\County_Addressing\Addressing_GIS_Workflow


\Addressing_GIS_Workflow
	Addressing_GIS_Workflow.gdb
		Addressing_Grid
		Township_Sections
		Zip_Districts
	County_Addressing.tbx
		SenCO_Addressing_Script
	SenCo_Addressing_Script.py
	README.txt


SenCo_Addressing_Script.py generally does the following;
# SET Environment
# GET Environment From Parameters
# GET Selected Layers From Parameters
# SET Layer Selections from Selected Address Point
# Create COPY of selected addresses and REMOVE the created point to remove lock
# Dynamically CREATE Address Fields Dictionary
# Manually SET Address Fields Values from Parameters
# Dynamically SET Address Dictionary Values from Roads Layer
# Manually SET Address Dictionary Values from Township Sections Layer
# Manually SET Address Dictonary Values from ZIP layer
# Determine Addressing Axis Values and Directions
# CALCULATE HOUSE NUMBER
# SET STANDARD OR BLANK ATTRIBUTES
# Calculate LSN  and ALSN
# UPDATE row with Address Dictionary Values
# APPEND new address back to Address Layer
