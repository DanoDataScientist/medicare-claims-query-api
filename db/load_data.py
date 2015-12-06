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

TABLE_NAME = "medicare2010sample"

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
            "Failed to get {0}. Returned status code {1}.".format(uri,
                                                                  r.status_code))
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
