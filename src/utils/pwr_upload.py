#Import modules
import pandas as pd
import toml

#Import user modules
import ncl_sqlsnippets as snips

#Import env
from os import getenv
from sqlalchemy import create_engine, MetaData, text, insert
from dotenv import load_dotenv

#Import env

load_dotenv(override=True)
config = toml.load("./config.toml")

OUTPUTDIR = "./" + config["struct"]["output_dir"] + "/"
UPLOADPATH = getenv("YEAR") + "/M" + getenv("MONTH") + "/"

TARGETTABS = config["form"]["target_tabs"]

SQL_DATABASE = config["database"]["sql_database"]
SQL_SCHEMA = config["database"]["sql_schema"]
SQL_ADDRESS = getenv("SQL_ADDRESS")

#Get years in data file
def derrive_years(df):
    #Return all years present in the df file (might be multiple in the case of the historic file)
    years_arr =  df["fyear"].drop_duplicates().values
    #Add quotations to each array element as they need to be within quotations when used in the query string
    years_arr = ["'" + value + "'" for value in years_arr]
    return years_arr

#Establish a connection to the database
def db_connect(server_address, database, 
               server_type="mssql", driver="SQL+Server"):
    
    #Create Connection String
    conn_str = (f"{server_type}://{server_address}/{database}"
                f"?trusted_connection=yes&driver={driver}")
    
    #Create SQL Alchemy Engine object
    engine = create_engine(conn_str, use_setinputsizes=False)
    return engine

#Construct delete query to remove old data 
#(Maybe in future replace with UPDATE statement but this is easier for now)
def build_delete_query(years, sql_table):
    query = f"DELETE FROM [{SQL_SCHEMA}].[{sql_table}] "\
            f"WHERE fyear IN ({', '.join(years)})"
    
    return query

#Delete existing data in table as we only want to overwrite some of the data
def delete_old_pwr(engine, df, sql_table):
    years = derrive_years(df)

    delete_query = build_delete_query(years, sql_table)

    snips.execute_query(engine, delete_query)


#Table needs to replace uploadtab whitespace in the table name
table_prefix = "wf_pwr_"

#Execute the pipeline for each tab
print("Upload starting...")
for tab in TARGETTABS:
    #Get tab name
    tab_name = tab.split(".")[1].lower()
    print(f"Uploading {tab_name} data")

    #Load data
    df_data = pd.read_csv(f"{OUTPUTDIR}{UPLOADPATH}{tab_name}.csv")
    #Derrive destination table name
    sql_table = table_prefix + tab_name

    #Set up Database Connection
    server_address = SQL_ADDRESS
    sql_database = SQL_DATABASE

    #Connect to the database
    engine = db_connect(server_address, sql_database)

    #Check if table exists

    if snips.table_exists(engine, sql_table, SQL_SCHEMA):
        #If it exists delete old data
        delete_old_pwr(engine, df_data, sql_table)

    #Upload the data
    snips.upload_to_sql(df_data, engine, sql_table, SQL_SCHEMA, replace=False)