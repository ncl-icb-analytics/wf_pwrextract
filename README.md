# PWR Data Extract

Python notebook to convert PWR forms into row data that can be processed.

## Changelog

### [1.0] - 03/07/2023

- Outputs as csv
- Works for all data tabs in 2022-23 and 2023-24 PWR forms

### [1.1] - 03/07/2023

- Added unit column to the output that specifes whether a row value is WTE, HC, or other.

### [1.2] - 04/07/2023

- Added upload.ipynb notebook to upload the output of the extract.ipynb notebook to sql

### [2.0] - 20/11/2024

- Moved the code from notebooks to python scripts
- Reduced functionality to only process core tabs
- Combined extract and upload code into a single executable
- Added First Time Installation instructions to the SOP

### [2.1] - 06/03/2025

- Adjusted the database connection to use DSN to establish the connection.
- Adjusted the code and toml to work from a local directory and pull data from the shared drive.

## First Time Installation

Follow the NCL scripting onboarding document for guidance on installing python (Section 7), and setting up the code (Section 4.1).
The onboarding document can be found [here](https://nhs.sharepoint.com/:f:/r/sites/msteams_3c6e53/Shared%20Documents/Data%20Science?csf=1&web=1&e=ArWnMM).

Copy the .env into the WF_PWREXTRACT folder. The .env file can be found at: 
`N:\Performance&Transformation\Performance\NELCSUNCLMTFS\_DATA\UEC and Productivity Team\Workforce\Datasets\Provider Workforce Returns`

## Standard use
Details on sourcing the PWR data is written seperate to this file. Instructions can be found at: `N:\Performance&Transformation\Performance\NELCSUNCLMTFS\_DATA\UEC and Productivity Team\Workforce\Datasets\Provider Workforce Returns`

- Create a new folder in the data directory (found here: `N:\Performance&Transformation\Performance\NELCSUNCLMTFS\_DATA\UEC and Productivity Team\Workforce\Datasets\Provider Workforce Returns`) for the new month's submissions. The full path should be /data/YYYY-ZZ/Mn where YYYY-ZZ is the financial year (i.e. 2024-25) and Mn is the financial month number (i.e. M1 for Month 1 or April).
- Modify the .env file in your project directory specify the year and month of data to process.
- Execute the src/pwr.py script (provided the virtual environment is set up as specified in the First Time Installation section).
- The code will output a processed version of the data in the output folder but will also upload the new data to the sandpit to the tables specified in the config.toml file.

## .env Settings

- YEAR: Financial Year (formatted in the form YYYY-ZZ such as 2024-25).
- MONTH: Financial Month (April -> 1, May -> 2, etc).

## Output Format
- fyear: Financial Year, takes the value of the YEAR .env variable
- org_code: Org code that is listed in the cover sheet of the PWR file
- occ: Occupation, takes the value of column B in the PWR file which denotes a description for the row of data, typically the occupation.
- section: Section Name, denotes the title of the table the data appeared in. There are multiple sections in each tab and some have overlapping (or a lack of) subcode id and occ values. The section name is needed to differentiate between rows with no subcode id for some tabs.
- subcode: Unqiue id code for each row except when it isn't.
- month: Numeric Month for the financial year (1 is "April", 2 is "May, etc.)
- count: Value of either the Whole Time Equivalent (WTE) or Headcount (HC)
- unit: Specifies if the count for this row is WTE, HC, or other.

## Licenses
This repository is dual licensed under the [Open Government v3](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) & MIT. All code can outputs are subject to Crown Copyright.
