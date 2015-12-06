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
