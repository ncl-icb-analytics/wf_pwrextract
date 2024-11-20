#Import Modules
import pandas as pd
import os
import toml

from os import getenv
from dotenv import load_dotenv

#Import env settings
load_dotenv(override=True)
#Load toml settings from config
config = toml.load("./config.toml")

SOURCEDIR = "./" + config["struct"]["data_dir"] + "/"
OUTPUTDIR = "./" + config["struct"]["output_dir"] + "/"
SOURCEPATH = getenv("YEAR") + "/M" + getenv("MONTH") + "/"

TARGETTABS = config["form"]["target_tabs"]

YEAR = getenv("YEAR")
MONTH = int(getenv("MONTH"))

#Function to return the column indices based on the relevant tab
def return_idc(month):
    
    #Think this can be constant for all tabs
    idc = [0,1,18,5,6,7,8,9,10,11,12,13,14,15,16]
    
    #Only return the 3 info columns and the months with filled in data
    return idc[:month+3]

#Function to return the number of sections for each tab
def return_sections(df):
    #Remove all nulls from the num column
    df_num = df[pd.notnull(df['num'])]
    #Remove all rows that don't align with the section's subcode heading
    df_num = df_num[(df_num['subcode'] == "Maincode")]

    #Return the length of the filtered dataframe (1 row for each section)
    return df_num.shape[0]
    
#Function to return the name of a given section
def return_section_name(df, num):   
    #The section name is immediately to the right of the section num so get the row with the section num and extract the occ value
    section_name = df.loc[df["num"] == num, "occ"].values[0]
    return section_name

#Get all files in the source folder
def get_files(source):
    
    #Get all files
    filenames = os.listdir(source)

    #Remove temp files
    filenames = list(filter(lambda x: not x.startswith("~"), filenames))

    #Remove non macro excel files
    filenames = list(filter(lambda x: x.endswith(".xlsm"), filenames))

    return filenames

#Get the org code from the file
def get_org(fullpath):

    try:
        #The org code is written in the PWR file in cell D37 on the Cover page
        #Doing this means I don't need to rename the files to use them
        df_cover = pd.read_excel(fullpath, sheet_name="Cover")
        org = df_cover.iloc[35,3]

        return org
    except:
        raise Exception (f"Getorg error for {fullpath}")   

#Remove unused columns from sheet
def trim_noise(df, idc, cols):
    #Only keep the columns specified in the indicies of idc
    df_trim = df.iloc[:, idc]
    #Rename the remaining columns to something readable
    df_trim.columns = cols

    return df_trim

#Get the index of the provided num from column 0
def get_row_from_num(df, num):
    #Each tab on the PWR form contains a number in the first column at the beginning of each section. 
    #Using this as a reference point we can extract the tabular table from the forms without hardcoding the locations
    try:
        idx = df.index[df.iloc[:,0] == num].tolist()[0]
        return idx
    #Exception if an invalid section number was given to the function
    except:
        raise Exception(f"The provided num ({num}) was not found.")

#Get a dataframe containing just the tabular data from a given section
def get_df_cut_from_num(df, num):
    #Get start index of section
    start_index = get_row_from_num(df, num)

    #Fixed defined start point for each section
    start_value = "Subcode"

    #Get data frame after starting index
    df_after_start = df.iloc[start_index:].reset_index(drop=True)

    #Get the index of the first instance of the start_value appearing in the section
    # +1 to not include the header row
    next_start_index = df_after_start[df_after_start.iloc[:,2] == start_value].index[0] + 1

    #Get the remaining dataframe after the next_start_index
    df_after_next = df_after_start.iloc[next_start_index:].reset_index(drop=True)
    
    #Get the end index which is the first row not containing a subcode value
    try:
        end_index = df_after_next['num'].first_valid_index()
        #end_index = df_after_next[df_after_next['occ'].isnull()].index[0]

        return df_after_next.iloc[:end_index].drop(columns=['num'])
    #Need a try statement for the last section as there is no data after the last section
    except:
        #Return the tabular data for the section
        #The index column can be trimmed here as we don't want it in the output
        return df_after_next.drop(columns=['num'])
    
#Get the column unit for a given section
def return_unit(df, num):
    #Get start index of section
    section_index = get_row_from_num(df, num)

    #Get dataframe cut for this section
    df_section = df.iloc[section_index:].reset_index(drop=True)

    #Get index of the header containing the unit data
    header_index = df_section[df_section.iloc[:,2] == "Subcode"].index[0]

    #Return the value of the first month column (Should be consistent for all months)
    unit = df_section['1'].iloc[header_index]

    return unit

#Get files
files = get_files(SOURCEDIR + SOURCEPATH)

#Get indices of relevant columns for this tab (Realised later this is constant for all tabs so this just returns a fixed array)
idc = return_idc(MONTH)

#Define column names
cols = ["num", "occ", "subcode", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

#For each tab
print("Extract starting...")

for tab in TARGETTABS:
    print(f"Extarcting {tab.split(".")[1]} data")

    #Define main collate dataframe for pwr data
    output_columns = ["fyear", "org_code", "occ", "section", "subcode", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "unit"]
    df_collate = pd.DataFrame(columns = output_columns[:MONTH+4])

    #For each pwr file
    for pwr in files:
        #Define the full path to the file
        fullpath = SOURCEDIR + SOURCEPATH + pwr

        #Get the org code
        org = get_org(fullpath)

        #Get the data
        df_pwr = pd.read_excel(fullpath, sheet_name=tab)

        #Trim extra columns
        df_pwr = trim_noise(df_pwr, idc, cols[:MONTH+3])

        #For each section
        for i in range(return_sections(df_pwr)):

            #Get the dataframe for this section and assign the section name
            df_section = get_df_cut_from_num(df_pwr, i+1)

            #Drop rows with a blank occ value
            df_section = df_section.dropna(subset=['occ'])

            #Drop rows with a subcode ending in "ap"
            df_section["subcode"] = df_section["subcode"].astype(str)
            mask = ~df_section["subcode"].str.endswith("ap")
            df_section = df_section[mask]

            df_section['section'] = return_section_name(df_pwr, i+1)
            
            #Get the column unit for this section
            df_section['unit'] = return_unit(df_pwr, i+1)

            #For initial loop, assign df_pwr_c
            if i == 0:
                df_pwr_c = df_section

            #Concat sections together otherwise
            else:
                df_pwr_c = pd.concat([df_pwr_c, df_section])

        #Set year and org
        df_pwr_c['fyear'] = YEAR
        df_pwr_c['org_code'] = org

        #Add to main collate dataframe for this tab
        df_collate = pd.concat([df_collate, df_pwr_c])

    #Unpivot data
    df_unpivot = pd.melt(df_collate, id_vars=['fyear', 'org_code', 'occ', 'section', 'subcode', 'unit'], var_name='month', value_name='count')

    outputdir = OUTPUTDIR + SOURCEPATH

    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    #Export data
    df_unpivot.to_csv(f"{outputdir + tab.split('.')[1]}.csv", index=False, mode="w")