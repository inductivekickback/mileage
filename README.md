The 4J School District expects employees to fill in expense reports for mileage and parking reimbursement using a form that does not automatically calculate the distance between school buildings. Employees are instructed to use Google Maps to find the shortest-possible path between all of the building pairs on their forms. There are more than 30 possible buildings to visit so this can be quite burdensome for employees that travel a lot.

### Features
This program allows the user to:

 - Use the [Google Maps Directions API](https://developers.google.com/maps/documentation/directions/overview) to find the shortest-possible path between buildings (both directions included in calculation)
 - Customize the set of school buildings to query, including colloquial names and precise addresses
 - Create a Comma Separated Value (CSV) table containing the results
 - Serialize a Python dictionary to a file that contains the results for use by other Python programs

**NOTE:** The [Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix/overview) is not used because it only offers the "best" route between buildings -- not a list from which you can determine the shortest distance.

### Requirements
The googlemaps module can be installed from the command line using pip:
```
$ cd mileage
$ pip3 install --user -r requirements.txt
```

### Usage
**compile.py** provides the user interface and help is available from the command line:

```
% python3 compile.py --help
usage: compile.py [-h] [--address_file ADDRESS_FILE] --table_file TABLE_FILE [--api_key API_KEY] [--data_out DATA_OUT] [--data_in DATA_IN]

Generate a table of distances between locations.

optional arguments:
  -h, --help            show this help message and exit
  --address_file ADDRESS_FILE
                        Path to CSV input file containing locations
  --table_file TABLE_FILE
                        Path to CSV output file
  --api_key API_KEY     Google API KEY with Distance Matrix permissions
  --data_out DATA_OUT   Path to pickle file for storing the result dict
  --data_in DATA_IN     Path to pickle file for loading a previously-stored result dict
```
A Google API key is required and each invocation will cost around $8 in API usage (as of August 2024) for a full run. If data (or partial data) from a previous run is specified then only pairs that don't already exist in the data will be calculated. Example data and CSV files are included in the 'artefacts' directory.

**Example:** A complete run using the included reference set of addresses 
```
python3 compile.py --address_file artefacts/addresses.csv --table_file path_to_table_output_file.csv --data_out path_to_data_output_file.pickle --api_key YOUR_DEVELOPER_API_KEY
```
