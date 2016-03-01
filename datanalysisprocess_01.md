**PROCESS - Data Analysis July '15 - Initial Exploration**

Tools: Primarily used Excel for data cleaning and ArcMap for spatial joins.

1 Start with 2015 Rental Registration database (“RR”) supplied as Excel files from vendor’s client export tool
“Dwelling by Type” Report
16,392 records

2 Clean/Normalize RR “Address” Data:
- Replace direction abbreviations (‘N’, ‘S’, etc.) with long versions in Owner Address for addresses where STPRE = “” and STNAME contains a direction (ex. North Hills Dr.); Find and replace function, need better system
- Replace “LA” abbreviation with “LN” - Excel formula IF(RIGHT(cell, 2) = ‘LA’, REPLACE(cell, LEN(cell) - 1, 2, ‘LN’), cell)
- Remove non-alphabetic or non-numeric characters in addressses; =IF(ISNUMBER(SEARCH("-",cell)), LEFT(cell,FIND("-",cell)-1) & RIGHT(cell,LEN(cell)-FIND(" ",cell)+1), cell)
- Excel: Create full owner address column (concatenate ADDR1, ADDR2, ADDR3), copy/paste to get values only, Trim(cell) to remove spaces

3 GeoCode based on Address Data:
- Use geocoding service “Raleigh.SDE/Raleigh.CompositeLocator” to provide precise lat/long for each address (on parcel if possible)
- Data Quality: Matching @ 95%, with ties 4%
-- Some matched geocoded to the street (~600-700?)
-- Some matched geocoded to incorrect parcels
- Join to WakePropA Parcel data
-- Dependent on Geocoding Addresses (#2)
-- Spatial Join to append parcel information (polygons) to the 2015 RR features/rows (points) where parcels fully contain points
-- Data Quality: 
--- 747 addresses that are not matched to parcels; these consist of records that are “no match” geocoded addresses or geocoded to the street
--- 2205 (13.5%) of RR matching to parcels with different addresses, potential overcounting from flagging method
--- 1489 (9.2%) of RR with own_add same as site_add, potential undercounting from flagging method

4 Obtain Zillow API Information by Address - Use Python scripts:
- Currently using addresses from original RR file after step #1
- Files - pyzillow.py, pyzillowmain.py, pyzillowerrors.py, setup.py, __version__.py
- Adjust variables - readFile, writeFile, row range to read (according to KEY’s call limit), KEY, desired result fields and column headers (add/remove #)
- Zillow results and RR database written in writeFile: “2015_RR_Zillow_API.csv”
- Data Quality: Matching @ 95%
- Transform Zillow API data from text to numbers
- Analyze Results:
-- Percentage of addresses not available in Zillow, Average statistics, summary statistics, etc.
- Map Results & Summarize by Block Group
-- Join RRwZillow Info to “Join_RR15-WakePropA” using RR “Address” to Match (Quality: ~350 records did not match)

5 Flagging Potential Rentals: Steps towards labelling property records as rentals
- Join RR Database with additional property records
-- Combine: “Join_RR15-WakePropA” dbf and “WakePropA_Res-Full_v2” dbf by abstracting RR15 records for each applicable property record (creates “WakePropA_Res-Full_v2_RR”
--- Make Pivot Table for Join_RR15-WakePropA with REID as rows, sum of Units and count of Form_ID
--- In WakePropA_Res-Full_v2, create columns NBR_RR and Sum_RR_Units using =IFERROR(VLOOKUP([REID],'[Join_RR15-WakePropA.dbf]LookupTable'!$A$1:$C$14252,column,FALSE),0)
-- Combine: “Not_Yet_Validated_Addresses_7-10-15” csv and “WakePropA_Res-Full_v2_RR” by abstracting RR15 not-yet-validated records for each applicable property record
--- Create full OWN_ADDR column by concatenating Address and City/State/Zip columns
--- Make Pivot Table for Not_Yet_Validated_Addresses_7-10-15 with OWN_ADDR as rows, count of Form ID
--- In WakePropA_Res_Full_v2, create column NBR_RR_NYV using =IFERROR(VLOOKUP([OWN_ADDR], '[Not Yet Validated Addresses_7-10-15.xlsx]Sheet5'!$A$1:$B$524, 2, FALSE), 0)

- Create Rental Flags
-- Clean/Normalize: WakePropA Site_Address & Owner Address Fields: EXPLORE EXISTING NORMALIZATION SERVICES (check with Chad, Justin)
-- RR_Rental: “1” (True) if parcel found in RR database (NBR_RR > 0)
---  =IF([NBR_RR] >0, 1, 0)
--- Data Quality: 14,011 RR parcels of 14,252 REIDs in Lookup Table

-- OWN_DNE_SITE: “1” (True) if owner address does not equal site address
--- =IF(ISNUMBER(SEARCH([SITE_ADDRE], [OWN_ADDR]))=FALSE, 1, 0)
--- Data Quality: 25,549 (24,383 w/ limits) parcels, 13,501 parcels not in RR

-- SITE_ADD_NOT_IN_OWN: “1” (True) if owner address does not equal site address; alternative method to OWN_DNE_SITE
--- =IF(AND(ISNUMBER(SEARCH([STNAME], [OWN_ADDR])), ISNUMBER(SEARCH([STNUM], [OWN_ADDR])), ISNUMBER(SEARCH([STPRE], [OWN_ADDR])), ISNUMBER(SEARCH([STSUF], [OWN_ADDR])), ISNUMBER(SEARCH([STMISC], [OWN_ADDR]))), 0, 1)
--- Data Quality: 25,007 (23,874 w/ limits) parcels, 13,099 (11,978 w/ limits) parcels not in RR

-- OWN_LLC_INC: “1” (True) if owner name contains “LLC”, “INC”, or “Properties”
--- =IF(OR(ISNUMBER(SEARCH(" LLC", [OWNER])), ISNUMBER(SEARCH(" INC", [OWNER])), ISNUMBER(SEARCH(" Properties", [OWNER]))), 1, 0)
--- Data Quality: 6,051 parcels, 122 where both RR_Rental and OWN_DNE_SITE are False

-- POTENTIAL_RENT: “1” (True) if SITE_ADD_NOT_IN_OWN and not RR_Rental
--- =IF(AND([SITE_ADD_NOT_IN_OWN], [RR_Rental]=0), 1, 0)
--- Data Quality: 13,098 (11,977 w/ limits) parcels

-- TOTAL_RENT_FLAG: “1” (True) if flagged as rental
--- =IF(OR([POTENTIAL_RENT], [RR_Rental]), 
--- Data  Quality: 27,109 (25,968 w/ limits) parcels

-- POTENTIAL_RENT_UNITS: total units if the parcel is a potential rental
--- =IF([POTENTIAL_RENT], [TOTUNITS], 0)
--- Data Quality: Sum of Units = 32,250 (30,986 w/ limits)

-- RR_WAKE_UNITS: total units if the parcel is in RR database
--- =IF([RR_RENTAL] = 1, [TOTUNITS], 0)
--- Data Quality: 63,623 units

-- TOTAL_RENT_UNITS: total units if the parcel is flagged as a rental
--- =IF([TOTAL_RENT_FLAG], [TOTUNITS], 0)
--- Data Quality: Sum of Units = 96,401 95,874 (94,607 w/ limits) (63,623 from RR)

- Set Confidence Level:

-- 100% - If Rental Registration
-- Potential Rentals (OA =/ SA):
--- Approx. 95% - LLC/INC/Properties
--- x% - PO Box as Owner Address
--- x% (75?) - Address Mismatch

6 Check for Accuracy:
- Divide Results into Categories:
Problems with Method - Errors in owner does not equal site address concept, potential non-rentals included
Database Errors - typos, errors with data from RR or property records
Geocoding Errors - errors in ArcGIS or with method of identifying/matching RR addresses in spreadsheet
Potential Rentals - to be investigated by RR

- Of 12,468 Flagged Potential Rentals in city limits (or of a sample of 336 addresses):
-- Problems with Method:
LLC, but same owner and site addresses
3 properties of Inspection sample (0.89%)
114 properties total (0.91%)
PO Box - unable to determine if owner lives on-site
5 properties of sample (1.49%)
1162 properties total (9.3%)
Where Owner Addresses /= Site Address but it is not a rental scenario (False Positive Potential Rental Flags)
New owner may be building or renovating and therefore keep the mailing address at a PO or somewhere else
Second Home - just not living there or renting
Parents have bought for kids in college
Owner prefers getting mail at a P.O. Box for privacy reasons

-- Database Errors:
5 properties of sample (1.49%)
Unable to tell total number of errors

-- Geocoding Errors:
Non-Residential
7 properties in sample (2.08%)
318 with 0 units total (2.56%)
Already Registered
25 properties in sample (7.44%)

-- Potential Rentals:
New to Registry
255 properties in sample (75.89%)
Changed Owners - sites previously registered
20 properties in sample (5.95%)

-- To-Be Fixed:
Noted as Not-Rental - in RR database
7 properties in sample (2.08%)
