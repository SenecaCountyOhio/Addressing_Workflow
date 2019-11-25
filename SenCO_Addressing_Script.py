"""Addressing Script."""
import arcpy

# Environment
arcpy.env.overwriteOutput = True

# GET Environment From Parameters
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# GET Selected Layers From Parameters
selected_address = arcpy.GetParameterAsText(1)
selected_road = arcpy.GetParameterAsText(2)

# SET Layer Selections from Selected Address Point
address_grid = arcpy.SelectLayerByLocation_management(
    "Addressing_Grid",
    'COMPLETELY_CONTAINS',
    selected_address
)
twp_sct = arcpy.SelectLayerByLocation_management(
    "Township_Sections",
    "COMPLETELY_CONTAINS",
    selected_address
)
zip_dist = arcpy.SelectLayerByLocation_management(
    "ZIP_Districts",
    "COMPLETELY_CONTAINS",
    selected_address
)

# Create COPY of selected addresses and REMOVE the created point to remove lock
arcpy.CopyFeatures_management(selected_address, "selected_address")
arcpy.DeleteFeatures_management(selected_address)
selected_address = "selected_address"

# Dynamically CREATE Address Fields Dictionary
address_fields = arcpy.ListFields(selected_address)
address_dict = {}
cursor = arcpy.SearchCursor(selected_address)
for row in cursor:
    for each in address_fields:
        address_dict[each.name] = row.getValue(each.name)

# Manually SET Address Fields Values from Parameters
address_dict['UNITNUM'] = arcpy.GetParameterAsText(3)
address_dict['BUILDING'] = arcpy.GetParameterAsText(4)
address_dict['FLOOR'] = arcpy.GetParameterAsText(5)
address_dict['ABSSIDE'] = arcpy.GetParameterAsText(6)
address_dict['SUBDIV'] = arcpy.GetParameterAsText(7)
address_dict['STRUC_TYPE'] = arcpy.GetParameterAsText(8)
address_dict['COMMENT'] = arcpy.GetParameterAsText(9)
address_dict['DATEMODIFI'] = arcpy.GetParameterAsText(10)


# Dynamically SET Address Dictionary Values from Roads Layer
def set_address_values(layer):
    """Set common fields in layer to addressing dictonary."""
    cursor = arcpy.SearchCursor(layer)
    for row in cursor:
        layer_fields = arcpy.ListFields(layer)
        for x in range(len(layer_fields)):
            layer_fields[x] = layer_fields[x].name
        for key in address_dict:
            if key in layer_fields and address_dict.get(key) is None:
                address_dict[key] = row.getValue(key)


set_address_values(selected_road)

# Manually SET Address Dictionary Values from Township Sections Layer
cursor = arcpy.SearchCursor(twp_sct, fields="PLSSID")
for row in cursor:
    address_dict['COMM'] = (row.getValue("PLSSID") + ' Twp')

# Manually SET Address Dictonary Values from ZIP layer
cursor = arcpy.SearchCursor(zip_dist, fields="GEOID10; MAILING_CI")
for row in cursor:
    address_dict['ZIPCODE'] = row.getValue("GEOID10")
    address_dict['USPS_CITY'] = row.getValue("MAILING_CI")

# Determine Addressing Axis Values and Directions
cursor = arcpy.SearchCursor(
    address_grid,
    fields="AxisX_Val; AxisY_Val; AxisX_Dir; AxisY_Dir"
)
axis = []
for row in cursor:
    axis.append(row.getValue("AxisX_Val"))
    axis.append(row.getValue("AxisY_Val"))
    axis.append(row.getValue("AxisX_Dir"))
    axis.append(row.getValue("AxisY_Dir"))


# CALCULATE HOUSE NUMBER
class house_address:
    """Process to calculate house number of new address."""

    def __init__(self, selected_address, side, ST_PREFIX, axis):
        """Only function in class."""
        if ST_PREFIX == "W" or ST_PREFIX == "E":
            self.axis_val = int(axis[0])
            self.axis_dir = axis[2]
            self.Neighbor_GRID_Val = str(self.axis_val - 1000)
            self.axis_val_field = "AxisX_Val"
            self.axis_dir_field = "AxisX_Dir"
        else:
            self.axis_val = int(axis[1])
            self.axis_dir = axis[3]
            self.Neighbor_GRID_Val = str(self.axis_val - 1000)
            self.axis_val_field = "AxisY_Val"
            self.axis_dir_field = "AxisY_Dir"
        self.selection = (
            "{0}='{1}' AND {2}='{3}'".format(
                self.axis_val_field,
                self.Neighbor_GRID_Val,
                self.axis_dir_field,
                ST_PREFIX
            )
        )
        arcpy.SelectLayerByAttribute_management(
            "Addressing_Grid",
            "NEW_SELECTION",
            self.selection
        )
        arcpy.CopyFeatures_management(
            "Addressing_Grid",
            "neighbor_grid"
        )
        self.near_table = arcpy.GenerateNearTable_analysis(
            in_features=selected_address,
            near_features="neighbor_grid",
            out_table="Near_Table"
        )
        self.cursor = arcpy.SearchCursor(self.near_table)
        Address_Dist = 0
        for row in self.cursor:
            Address_Dist = int((row.getValue("NEAR_DIST") / 5280) * 1000)
        if side == "E" or side == "N":
            EorO_1 = "O"
        else:
            EorO_1 = "E"
        if (Address_Dist % 2) == 0:
            EorO_2 = "E"
        else:
            EorO_2 = "O"
        if EorO_1 == EorO_2:
            pass
        else:
            Address_Dist = (Address_Dist + 1)
        self.Address_Dist = Address_Dist
        self.HOUSENUM = self.axis_val + self.Address_Dist


house = house_address(
    selected_address,
    address_dict['ABSSIDE'],
    address_dict['ST_PREFIX'],
    axis
)
address_dict['HOUSENUM'] = house.HOUSENUM

# SET STANDARD OR BLANK ATTRIBUTES
address_dict['FEATUREID'] = 0
address_dict['HNRANGE'] = ""
address_dict['UNITEXTRA'] = ""
address_dict['MUNI'] = ""
address_dict['VILLAGE'] = ""
address_dict['SIDE'] = 999
address_dict['SOURCE'] = 999
address_dict['STATE'] = "OH"
address_dict['COUNTY'] = "SEN"
address_dict['LHN'] = address_dict['HOUSENUM']
address_dict['NLFIDNEW'] = ""
address_dict['SEGID'] = 0
address_dict['TSSEGID'] = 0
address_dict['PT_LEN'] = 0
address_dict['MPVAL'] = 0
address_dict['FIPSCODE'] = ""
address_dict['X'] = 0
address_dict['Y'] = 0
address_dict['FIELDNOTE'] = ""

# Calculate LSN  and ALSN
temp_address = [
    address_dict['HOUSENUM'],
    address_dict['UNITNUM'],
    address_dict['BUILDING'],
    address_dict['FLOOR'],
    address_dict['ST_PREFIX'],
    address_dict['ST_NAME'],
    address_dict['ST_TYPE'],
    address_dict['USPS_CITY'],
    address_dict['STATE'],
    address_dict['ZIPCODE']
]

temp_alt_address = [
    address_dict['HOUSENUM'],
    address_dict['UNITNUM'],
    address_dict['BUILDING'],
    address_dict['FLOOR'],
    address_dict['ALTPREFIX'],
    address_dict['ALTNAME'],
    address_dict['ALTTYPE'],
    address_dict['USPS_CITY'],
    address_dict['STATE'],
    address_dict['ZIPCODE']
]

temp_LSN = []
temp_ALSN = []

for x in temp_address:
    if x == "" or x == " ":
        pass
    else:
        temp_LSN.append(x)
        temp_LSN.append(" ")
for x in temp_alt_address:
    if x == "" or x == " ":
        pass
    else:
        temp_ALSN.append(x)
        temp_ALSN.append(" ")
LSN = ""
ALSN = ""
for x in temp_LSN:
    LSN += str(x)
for x in temp_ALSN:
    ALSN += str(x)
address_dict['LSN'] = LSN
address_dict['ALSN'] = ALSN

# UPDATE row with Address Dictionary Values
cursor = arcpy.UpdateCursor(selected_address)
for row in cursor:
    for key in address_dict:
        if row.getValue(key) != address_dict[key]:
            row.setValue(key, address_dict[key])
    cursor.updateRow(row)
# APPEND new address back to Address Layer
arcpy.Append_management(selected_address, arcpy.GetParameterAsText(1))
