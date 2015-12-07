# Medicare Synthetic Beneficiary Claims Data 2010 - RESTful Service

A simple Flask app for loading CMS 2008-2010 claims and creating a REST API to
query the data.

## Install
Set up your EC2 and RDS instances if you haven't, then update the related HOST
and database variables in _fabfile.py_ (ook for comments beginning with
`# Configure`.

```bash
vagrant up
fab vagrant bootstrap
fab aws bootstrap
```