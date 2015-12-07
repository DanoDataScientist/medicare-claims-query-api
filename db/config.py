from . import rds_password

# Change the following settings to match your RDS instance
rds_dbhost = "medicare.chtdutbma0ig.us-west-2.rds.amazonaws.com"
rds_dbname = "BENEFICIARYDATA"
rds_dbuser = "nikhil"
rds_dbpass = rds_password.rds_pass  # Set this in db/rds_password.py

# These settings do not need to be changed
vagrant_dbhost = "localhost"
vagrant_dbname = "beneficiary_data"  # Keep lowercase
vagrant_dbuser = "vagrant"
vagrant_dbpass = None

# Global table name to use on RDS and Vagrant
db_tablename = "beneficiary_sample_2010"  # Change if you like...keep lowercase
