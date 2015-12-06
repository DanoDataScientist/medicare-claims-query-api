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
import io
import zipfile

import psycopg2
import requests

TABLE_NAME = "medicare_beneficiary_sample_2010"

# Parse arguments
argparser = argparse.ArgumentParser(
    description="Load CMS data into Postgres.",
    epilog="example: python load_data.py --host localhost --dbname Nikhil "
           "--user Nikhil --password False")
argparser.add_argument("--host", required=True, help="location of database")
argparser.add_argument("--dbname", required=True, help="name of database")
argparser.add_argument("--user", required=True, help="user to access database")
argparser.add_argument("--password", required=False, help="password to connect")
args = argparser.parse_args()

DATA_FILES = (
    "https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable"
    "-Public-Use-Files/SynPUFs/Downloads"
    "/DE1_0_2010_Beneficiary_Summary_File_Sample_1.zip",
)


def download_zip(uri):
    """
    Download an zipped data file and return the unzipped file.

    Parameters
    ----------
    uri : str
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


def cursor_connect(db_dsn, cursor_factory=None):
    """
    Connects to the DB and returns the connection and cursor, ready to use.

    Parameters
    ----------
    db_dsn: str
        A string representing the database DSN to connect to.
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


def drop_table(db_dsn):
    """
    Drop the table specified by TABLE_NAME.

    Parameters
    ----------
    db_dsn: str
        A string representing the database DSN to connect to.
    """
    con, cur = cursor_connect(db_dsn)
    try:
        sql = "DROP TABLE IF EXISTS {0};".format(TABLE_NAME)
        cur.execute(sql)
    except psycopg2.Error:
        raise
    else:
        con.commit()
        cur.close()
        con.close()


if __name__ == '__main__':
    # Create the database's DNS to connect with using psycopg2
    db_dsn = "host={0} dbname={1} user={2} password={3}".format(
        args.host, args.dbname, args.user, args.password
    )
    # Delete the database if it exists
    drop_table(db_dsn)
    for uri in DATA_FILES:
        f = download_zip(uri)
        headers = f.readline().replace('"', "").split(",")
        print("Downloaded file, "
              "contains {0} column headers.".format(len(headers)))
