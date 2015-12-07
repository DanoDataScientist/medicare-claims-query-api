# Medicare Synthetic Beneficiary Claims Data 2010 - RESTful Service

A simple Flask app for loading CMS 2008-2010 claims and creating a REST API to
query the data.

## Install
Set up your EC2 and RDS instances if you haven't, then update the related `HOST`
and database variables in *fabfile.py* (look for comments beginning with
`# Configure`. Then run:

```bash
vagrant up
fab vagrant bootstrap
fab aws bootstrap
# You'll be prompted to enter your RDS master password
```

You can start the dev server on vagrant with:

```bash
fab vagrant dev_server
# [127.0.0.1:2222] Executing task 'dev_server'
# [127.0.0.1:2222] run: cd /server/env.medicare-api.com; source bin/activate; python project/server.py
# [127.0.0.1:2222] out:  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

