"""Test EC2 JSON api. See https://github.com/nsh87/medicare-claims-query-api
for more info on the code base.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import urllib2

# Vagrant
# SERVER = 'http://localhost:7000'

# EC2
SERVER = 'http://52.32.95.188'


def get_counts(col):
    """
    Get counts by distinct values in a given column.

    Parameters
    ----------
    col : str, unicode
        Column to count distinct values within.

    Returns
    -------
    dict
        A dictionary of values and counts.
    """
    out = dict()
    response = urllib2.urlopen(SERVER + '/api/v1/count/' + col)
    out = response.read()
    return json.loads(out)


def get_state_depression():
    """
    Get the frequency of depression claims by state in descending order.

    Returns
    -------
    list
        A list of dictionaries with state abbreviation as keys and frequency
        of depression claims as value.
    """
    out = dict()
    response = urllib2.urlopen(SERVER + '/api/v1/depressed_states')
    out = response.read()
    return json.loads(out)


def get_avg_col(col):
    """
    Get the average value of a column.

    Parameters
    ----------
    col : str, unicode
        The column to get the average of.

    Returns
    -------
    dict
        A dictionary whose key is the column name and the value is the average
        value of that column.
    """
    out = dict()
    response = urllib2.urlopen(SERVER + '/api/v1/average/{0}'.format(col))
    results = json.loads(response.read())
    return results['average']


if __name__ == '__main__':
    print("*********************************************")
    print("test of my flask app runn at {0}".format(SERVER))
    print("created by Nikhil Haas")
    print("*********************************************")
    print("")
    print("*********** count claims by sex *************")
    for k, v in get_counts('sex').iteritems():
        print("{0}: {1}".format(k, v))
    print("*********************************************")
    print("")
    print("******* count heart failures claims *********")
    for k, v in get_counts('heart_failure').iteritems():
        print("{0}: {1}".format(k, v))
    print("*********************************************")
    print("")
    print("**** get rate of state depression claims ****")
    depression_rates = get_state_depression()
    for state in depression_rates['state_depression']:
        print("{0}: {1}".format(state.keys()[0], state.values()[0]))
    print("*********************************************")
    print("")
    print("****** average inpatient reimbursement ******")
    reimb = get_avg_col('inpatient_reimbursement')
    print("{0}: {1}".format(reimb.keys()[0], reimb.values()[0]))
    print("*********************************************")
    print("")
    print("***** average outpatient reimbursement ******")
    reimb = get_avg_col('outpatient_reimbursement')
    print("{0}: {1}".format(reimb.keys()[0], reimb.values()[0]))
    print("*********************************************")
    print("")
    print("**** average beneficiary responsibility *****")
    reimb = get_avg_col('beneficiary_responsibility')
    print("{0}: {1}".format(reimb.keys()[0], reimb.values()[0]))
    print("*********************************************")
