# =============================================================================
# Developer Assessment - Hotel Bookings reporting
# Author: Gabriel Haddon-Hill
# Date: 29/10/2020
# =============================================================================
import logging
import argparse
import datetime
import pandas as pd

logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)

#Create cmd line argument parser
parser = argparse.ArgumentParser(description='Retrieve hotel booking details')

parser.add_argument('data_file',
                    help='The path to the desired comma-separated (csv) bookings file.')
parser.add_argument('query_date',
                    help='The date to query (YYYY-MM-DD)')
parser.add_argument('--verbose',
                    help='Print full table of query results to console',
                    action='store_true')

args = parser.parse_args()

try: #Parse date string as datetime object
    start_date = datetime.date.fromisoformat(args.query_date)
except ValueError:
    raise argparse.ArgumentTypeError(
            f"Invalid date specified: '{args.query_date}'. Required format is: 'YYYY-MM-DD'")

try: #Load file into dataframe
    bookings_df = pd.read_csv(args.data_file)
except FileNotFoundError:
    raise argparse.ArgumentError(
            f"File '{args.data_file}' not found. Please specify a valid path")

if args.verbose:
    logging.info("VERBOSE OUTPUT ENABLED\n")
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',None)
    
logging.info(f"Querying bookings for {start_date}\n")

# =============================================================================
# DataFrame functions
# =============================================================================

def df_multicolumn_date_to_datetime(row):
    """
    Convert date over multiple columns to datetime object
    """
    year = row['arrival_date_year']
    month = row['arrival_date_month']
    day = row['arrival_date_day_of_month']
    # create datetime object from string of form "YearMonthDay" using full month name
    return datetime.datetime.strptime(f"{year}{month}{day}", '%Y%B%d').date()

def df_departure_datetime(row):
    """
    Get the departure date from arrival date and length of stay
    """
    return row['arrival_date_full'] + datetime.timedelta(
            days = (row['stays_in_weekend_nights'] + row['stays_in_week_nights']))

def df_total_residents_by_day(row, df):
    """
    Get the total number of residents per day
    """
    current_day = row['date'] #Ignore warning- it's used in the next line
    bookings_by_day = df.query(
            '(arrival_date_full <= @current_day & departure_date_full >= @current_day)')
    row['expected_adults'] = int(bookings_by_day['adults'].sum())
    row['expected_children'] = int(bookings_by_day['children'].sum())
    row['expected_babies'] = int(bookings_by_day['babies'].sum())
    return row

# =============================================================================
# General functions
# =============================================================================

def output_dataframe(df, outfile, header="Dataframe output:"):
    """
    Print a dataframe to console and write it to a csv file
    """
    print(header)
    print(df)
    logging.info(f"Writing to output file: '{outfile}'\n")
    df.to_csv(outfile)
# =============================================================================
## Active bookings reporting
    
# Filter canceled bookings
bookings_df.query('is_canceled == 0', inplace=True)

# Add arrival and departure date columns in datetime format
# (this would probably be better and more pandafied if it was done on whole columns using assign
# but this approach works for the given datafile and its readable)
bookings_df['arrival_date_full'] = bookings_df.apply(df_multicolumn_date_to_datetime, axis=1)
bookings_df['departure_date_full'] = bookings_df.apply(df_departure_datetime, axis=1)

# Change to 'days=7' if the 7 day window is inclusive (i.e. 8 days total)
end_date = start_date + datetime.timedelta(days = 6)

# Query bookings to get active bookings, or bookings scheduled within 7 days
active_bookings = bookings_df.query(
        '(arrival_date_full <= @end_date & departure_date_full >= @start_date)')

output_dataframe(active_bookings,
                 f"active_bookings_{start_date}.csv",
                 header=f"Active bookings in the next 7 days from {start_date}:")
# =============================================================================
## Expected residency reporting

# Get series of all dates from start to end
dates_within_week = pd.date_range(start_date,end_date) 
expected_residents_df = pd.DataFrame({"date": dates_within_week})
# The next line gets rid of the timestamp leaving just the date
expected_residents_df['date'] = expected_residents_df['date'].dt.date

# Fill dataframe with total expected residents per day
expected_residents_df = expected_residents_df.apply(
        lambda row: df_total_residents_by_day(row,active_bookings), axis=1)

output_dataframe(expected_residents_df,
                 f"expected_residents_by_date_{start_date}.csv",
                 header="Expected residents per day:")

logging.info('Finished')