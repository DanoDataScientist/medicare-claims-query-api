"""Load the CMS 2008-2010 Medicare Beneficiary Summary tables into Postgres.

See https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable
-Public-Use-Files/SynPUFs/DE_Syn_PUF.html
for more info on the data.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import csv
import io
import os
import urlparse
import zipfile

import psycopg2
import requests

TABLE_NAME = "medicare_beneficiary_sample_2010"

# Parse arguments
argparser = argparse.ArgumentParser(
    description="Load CMS 2010 summary beneficiary data into Postgres.",
    epilog="example: python load_data.py --host localhost --dbname Nikhil "
           "--user Nikhil")
argparser.add_argument("--host", required=True, help="location of database")
argparser.add_argument("--dbname", required=True, help="name of database")
argparser.add_argument("--user", required=True, help="user to access database")
argparser.add_argument("--password", required=False, help="password to connect")
args = argparser.parse_args()

# Declare URLs of CSV files to download
base_url = (
    "https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable"
    "-Public-Use-Files/SynPUFs/Downloads/some_file.zip"
)
# Prep base filename, with 'XX' to be replaced by a two-digit number indicating
# which file to download.
base_filename = "DE1_0_2010_Beneficiary_Summary_File_Sample_XX.zip"
DATA_FILES = [
    urlparse.urljoin(base_url, base_filename.replace('XX', '{0}').format(i))
    for i in range(1, 21)]


def download_zip(uri):
    """
    Download an zipped data file and return the unzipped file.

    Parameters
    ----------
    uri : str, unicode
        The URI for the .zip file.

    Returns
    -------
    zipfile.ZipExtFile
        A file-like object holding the file contents. This should be read like
        any other file, with one of `read()`, `readline()`, or `readlines()`
        methods::

            for line in f.readlines():
                print line
    """
    r = requests.get(uri)
    if r.status_code == requests.codes.ok:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        csv_file = z.namelist()[0]
        f = z.open(csv_file)
    else:
        raise ValueError(
            "Failed to get {0}. "
            "Returned status code {1}.".format(uri, r.status_code))
    return f


def cursor_connect(cursor_factory=None):
    """
    Connects to the DB and returns the connection and cursor, ready to use.

    Parameters
    ----------
    cursor_factory : psycopg2.extras
        An optional psycopg2 cursor type, e.g. DictCursor.

    Returns
    -------
    tuple
        A tuple of (psycopg2 connection, psycopg2 cursor).
    """
    con = psycopg2.connect(dsn=db_dsn)
    if not cursor_factory:
        cur = con.cursor()
    else:
        cur = con.cursor(cursor_factory=cursor_factory)
    return con, cur


def drop_table():
    """
    Drop the table specified by TABLE_NAME.
    """
    con, cur = cursor_connect()
    try:
        sql = "DROP TABLE IF EXISTS {0};".format(TABLE_NAME)
        cur.execute(sql)
    except psycopg2.Error:
        raise
    else:
        con.commit()
        cur.close()
        con.close()


def create_table():
    """
    Create the table given by TABLE_NAME.
    """
    con, cur = cursor_connect()
    # Create new column types to hold sex and race
    try:
        # Create enumerated types (like factors in R) to use as column types
        cur.execute("CREATE TYPE sex AS ENUM ('male', 'female');")
        cur.execute("CREATE TYPE race as ENUM ('white', 'black', 'others', "
                    "'hispanic');")
    except psycopg2.ProgrammingError as e:
        # If the types already exist just continue on
        if "already exists" in e.message:
            con, cur = cursor_connect()
        else:
            cur.close()
            con.close()
            raise
    try:
        sql = ("CREATE TABLE {0} ("
               "desynpuf_id CHAR(16) UNIQUE, "
               "bene_birth_dt CHAR(8), "  # These are converted to DATE later
               "bene_death_dt CHAR(8), "  # These are converted to DATE later
               "bene_sex_ident_cd sex, "
               "bene_race_cd race, "
               "bene_esrd_ind BOOLEAN, "
               "sp_state_code INT, "
               "bene_county_cd INT, "
               "bene_hi_cvrage_tot_mons INT, "
               "bene_smi_cvrage_tot_mons INT, "
               "bene_hmo_cvrage_tot_mons INT, "
               "plan_cvrg_mos_num INT, "
               "sp_alzhdmta BOOLEAN, "
               "sp_chf BOOLEAN, "
               "sp_chrnkidn BOOLEAN, "
               "sp_cncr BOOLEAN, "
               "sp_copd BOOLEAN, "
               "sp_depressn BOOLEAN, "
               "sp_diabetes BOOLEAN, "
               "sp_ischmcht BOOLEAN, "
               "sp_osteoprs BOOLEAN, "
               "sp_ra_oa BOOLEAN, "
               "sp_strketia BOOLEAN, "
               "medreimb_ip INT, "
               "benres_ip INT, "
               "pppymt_ip INT, "
               "medreimb_op INT, "
               "benres_op INT, "
               "pppymt_op INT, "
               "medreimb_car INT, "
               "benres_car INT, "
               "pppymt_car INT"
               ");".format(TABLE_NAME))
        cur.execute(sql)
    except psycopg2.Error:
        raise
    else:
        con.commit()
        cur.close()
        con.close()


def load_csv(csv_file):
    """
    Load data from a CSV file or file-like object into the database.

    Parameters
    ----------
    csv_file : str, unicode
        A file of file-like object returned from download_zip(). The file must
        have both `read()` and `readline()` methods.

    """
    con, cur = cursor_connect()
    try:
        with open(csv_file, 'r') as f:
            cur.copy_from(f, TABLE_NAME, sep=',', null='')
    except psycopg2.Error:
        raise
    else:
        con.commit()
        cur.close()
        con.close()


def prep_csv(csv_file):
    """
    Modifies the CMS Medicare data to get it ready to load in the DB.

    Important modifications are transforming character columns to 0 and 1 for
    import into BOOLEAN Postgres columns.

    Parameters
    ----------
    csv_file : zipfile.ZipExtFile
        A CSV-like object returned from download_zip().

    Returns
    -------
    str
        Path to a prepared CSV file on disk.
    """
    prepped_filename = 'prepped_medicare.csv'
    reader = csv.reader(csv_file)
    with open(prepped_filename, 'a') as f:
        writer = csv.writer(f)
        for row in reader:
            # Transform 'Y' for 'yes' into 1, for boolean
            if row[5] == 'Y':
                row[5] = '1'.encode('ascii')
            # Transform sex into factors
            sex = {'1': 'male'.encode('ascii'), '2': 'female'.encode('ascii')}
            row[3] = sex[row[3]]
            # Transform race into factors (note: there is no '4' value...)
            race = {
                '1': 'white'.encode('ascii'),
                '2': 'black'.encode('ascii'),
                '3': 'others'.encode('ascii'),
                '5': 'hispanic'.encode('ascii')
            }
            row[4] = race[row[4]]
            # Transform 'boolean' 1 and 2 into 0 and 1, for columns 12 - 22
            boolean_transform = {
                '1': '1'.encode('ascii'),
                '2': '0'.encode('ascii')
            }
            for i in range(12, 23):
                row[i] = boolean_transform[row[i]]
            # Transform strings to floats to ints
            for i in range(23, 32):
                row[i] = str(int(float(row[i]))).encode('ascii')
            writer.writerow(row)
    return prepped_filename


def alter_col_types():
    """
    Alter column types of the table to better suit the data.

    For example, convert the character-represented-dates to type DATE.
    """
    con, cur = cursor_connect()
    try:
        # Get column names so you can index the 2th and 3th columns
        sql = "SELECT * FROM {0} LIMIT 0;".format(TABLE_NAME)
        cur.execute(sql)
        colnames = [desc[0] for desc in cur.description]
        cols = (colnames[1], colnames[2])  # DO-Birth and DO-Death
        for col in cols:
            sql = """
            ALTER TABLE {0} ALTER COLUMN {1} TYPE DATE
            USING to_date({1}, 'YYYYMMDD');
            """.format(TABLE_NAME, col)
            cur.execute(sql)
    except psycopg2.Error:
        raise
    else:
        con.commit()
        cur.close()
        con.close()


def verify_data_load():
    """
    Verify that all the data was loaded into the DB.
    """
    con, cur = cursor_connect()
    try:
        sql = "SELECT COUNT(*) FROM {0}".format(TABLE_NAME)
        cur.execute(sql)
        result = cur.fetchone()
        num_rows = result['count']
    except psycopg2.Error:
        raise
    else:
        cur.close()
        con.close()
        expected_row_count = 2255098
        if num_rows != expected_row_count:
            raise AssertionError("{0} rows in DB. Should be {1}".format(
                                 num_rows, expected_row_count))
        print("Data load complete.")

if __name__ == '__main__':
    # Create the database's DNS to connect with using psycopg2
    db_dsn = "host={0} dbname={1} user={2} password={3}".format(
        args.host, args.dbname, args.user, args.password
    )
    # Delete the table and recreate it if it exists
    drop_table()
    create_table()
    # Download the data and load it into the DB
    try:
        for uri in DATA_FILES:
            medicare_csv = download_zip(uri)
            headers = medicare_csv.readline().replace('"', "").split(",")
            print("Downloaded CSV contains {0} headers.".format(len(headers)))
            prepped_csv = prep_csv(medicare_csv)
            load_csv(prepped_csv)
        alter_col_types()
    except:
        raise
    finally:
        try:
            os.remove(prepped_csv)
        except:
            pass

