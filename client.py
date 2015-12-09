from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import urllib2
import json

SERVER = 'http://localhost:7000'

current_dir = os.path.dirname(os.path.realpath(__file__))
if os.path.isfile(os.path.join(current_dir, 'PRODUCTION')):
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
