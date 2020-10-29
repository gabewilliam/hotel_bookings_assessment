# Developer Assessment - Hotel Bookings Reporting #

## Installation ##

This code was written in Python3.7 and uses [Pandas](https://pandas.pydata.org/), which can be installed with pip:

`pip install pandas`

or Anaconda

`conda install -c anaconda pandas`.

## Usage ##

`python bookings_report.py data_file query_date [--verbose]`

Positional arguments:
  data_file   The path to the desired comma-separated (csv) bookings file.
  query_date  The date to query (YYYY-MM-DD)

Optional arguments:
  -h, --help  show help message and exit
  --verbose   Print full table of query results to console
  
## Function ##

The program will produce two reports:

1. The records from the bookings file which correspond to bookings that are currently active for the given date, or will be active within 7 days of this date. This will be written to the file "active_bookings_YYYY-MM-DD.csv".
2. The total number of adults, children and babies expected to be in residents for each day in the next 7 days from the given date. This will be written to the file "expected_residents_by_date_YYYY-MM-DD.csv".