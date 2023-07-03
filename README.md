# PWR Data Extract

Python notebook to convert PWR forms into row data that can be processed.

## Changelog

### [1.0] - 03/07/2023

- Outputs as csv
- Works for all data tabs in 2022/23 and 2023/24 PWR forms

### [1.1] - 03/07/2023

- Added unit column to the output that specifes whether a row value is WTE, HC, or other.

## Standard use

- Add directory containing PWR files to be processed in the same directory as the extract.ipynb notebook. (Standard convention is to store them somewhere in the /data/ directory)
- Modify the .env file to choose runtime settings (details below)
- Execute all cells in the extract.ipynb notebook
- Output is stored in output folder using the same relative path as where the files were stored in the data folder
- Output will contain 1 files per tab in the PWR files

## .env Settings

- SOURCEDIR: Specifies data folder. Should remain "./data/" outside of special cases
- OUTPUTDIR: Specifies output folder. Should remain "./output/" outside of special cases
- SOURCEPATH: Relative path within the SOURCEDIR and OUTPUTDIR where the target files are located and should be stored respectively
- TARGETTABS: Binary bit pattern where 1 designates which tabs to process. For example "1011001" translates as process the first, third, fourth, and seventh tab. If the notebook is executed with this, then only those tabs will appear in the output.
- YEAR: Year value that will appear in the output. Can use whatever format is convienent but standard is yyyy/zz.
- MONTH: Month. This needs to be the numeric value of the most up to date financial year. For example a value of "2" means the output will contain April and May data only. Using this prevent non-populated data from appearing in the output (As future months exist in the forms but some values are auto-populated with 0's).

## Output Format
- fyear: Financial Year, takes the value of the YEAR .env variable
- org_code: Org code that is listed in the cover sheet of the PWR file
- occ: Occupation, takes the value of column B in the PWR file which denotes a description for the row of data, typically the occupation.
- section: Section Name, denotes the title of the table the data appeared in. There are multiple sections in each tab and some have overlapping (or a lack of) subcode id and occ values. The section name is needed to differentiate between rows with no subcode id for some tabs.
- subcode: Unqiue id code for each row except when it isn't.
- month: Numeric Month for the financial year (1 is "April", 2 is "May, etc.)
- count: Value of either the Whole Time Equivalent (WTE) or Headcount (HC)
- unit: Specifies if the count for this row is WTE, HC, or other.