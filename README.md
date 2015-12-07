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
```