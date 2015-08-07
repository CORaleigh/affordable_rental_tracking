from pyzillow import ZillowWrapper
from pyzillow import GetDeepSearchResults
import csv

#KEY = 'X1-ZWz1eu6dmd20p7_47pen' ## ZWSID - mospencer@davidson.edu
#KEY = 'X1-ZWz1a6b7rks16z_4vl2o' ## ZWSID - s1476895@sms.ed.ac.uk
KEY = 'X1-ZWz1etg2jizojv_5gnlr' ## ZWSID - Adam Martin

if __name__ == '__main__':
    
    ## Open file to read and write/append  
    with open('WakePropA_Res-Full_v2_RR.csv', 'rb') as readFile:
        with open('WakePropA_Res-Full_v2_RR_Zillow.csv', 'ab') as writeFile:
            reader = csv.reader(readFile)
            writer = csv.writer(writeFile)
            
            ## Write headers into new file (first set of rows only)
            column_names = reader.next()
            column_names.extend(['Zestimate','Rent Zestimate', 'Last Updated', 'RZ 30 Day Change', 'RZ Range Low', 'RZ Range High', 'Home Value Index', 'Use Code', 'Year Built', 'Finished Sq.Ft.', 'Lot Sq.Ft.'])
            #writer.writerow(column_names)
            
            ## For each row within call limit, call Zillow API
            for row in reader:
                if 13026 <= int(row[0]) < 14000:
                    address = row[16]
                    zipcode = row[18]
                    zillow_data = ZillowWrapper(KEY)
                    deep_search_response = zillow_data.get_deep_search_results(address, zipcode)
                    try:
                        result = GetDeepSearchResults(deep_search_response)
                        ## Add API fields into file
                        row.append(result.zestimate_amount)
                        row.append(result.rent_zestimate_amount)
                        row.append(result.rent_zestimate_lastUpdated)
                        row.append(result.rent_zestimate_valueChange)
                        row.append(result.rent_zestimate_valuationRange_low)
                        row.append(result.rent_zestimate_valuationRange_high)
                        row.append(result.home_value_index)
                        row.append(result.home_type)
                        row.append(result.year_built)
                        row.append(result.home_size)
                        row.append(result.property_size)
                    except:
                        row.extend([deep_search_response]*11) #Extend by number of columns added
                    writer.writerow(row)
            
            ## Close files
            readFile.close()     
            writeFile.close()    