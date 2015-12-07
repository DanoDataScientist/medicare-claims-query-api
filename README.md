# Medicare Synthetic Beneficiary Claims Data 2010 - RESTful Service

A simple Flask app for loading the Center for Medicare & Medicaid Services (CMS)
2010 Medicare claims and creating a REST API to query the data.

## Install
Set up your EC2 and RDS instances if you haven't, then update the related 
`HOST`, pem, and database variables in *fabfile.py* and *db/config.py* (look for
comments beginning with `# Change`). 

Make sure your EC2 instance has inbound access to RDS on port 5432.

Next, create a file *db/rds_password.py* and populate it with your password,
like so:

```python
"""Secret RDS password that doesn't get store in Git."""
rds_pass = "123456abcdefg"  # Change accordingly (RDS)
```

Then run:

```bash
vagrant up
fab vagrant bootstrap
fab aws bootstrap # You'll be prompted to enter your RDS master password at some point
```

You can start the dev server on vagrant with:

```bash
fab vagrant dev_server
# [127.0.0.1:2222] Executing task 'dev_server'
# [127.0.0.1:2222] run: cd /server/env.medicare-api.com; source bin/activate; python project/server.py
# [127.0.0.1:2222] out:  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

## Deploying Changes

Several commands are available for deploying you Flask app changes to AWS.

```bash
fab cut_production  # Merge master branch to production and push production 

fab aws pull  # Pull the latest production changes on AWS (doesn't restart web server)


fab aws deploy  # Does a cut_production and aws pull then restarts Gunicorn so the changes can be seen
```

Once RDS is set up during `fab aws bootstrap`, there will be no more changes to
the database.