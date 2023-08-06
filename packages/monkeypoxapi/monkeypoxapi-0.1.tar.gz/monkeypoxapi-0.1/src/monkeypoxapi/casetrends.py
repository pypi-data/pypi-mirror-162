
import json

import requests
import pprint
import io


res = requests.get('https://www.cdc.gov/poxvirus/monkeypox/response/modules/MX-response-case-count-US.json?v=2022-08-01T05%3A00%3A00.000Z')


parsed = json.loads(res.text)
data = parsed['data']



def numcases(state):
    # returns the number of cases for 'state'
    try:
        for i in data:
            if i["State"] == state:
                return i['Cases']
    except ValueError:
            print("State '" + state + "'is not valid. Make sure the first letter is capitalized")

def totalcases():
    # returns the number of total cases for the 
    current = 0
    for i in data:
        current += int(i['Cases'])
    return current

def date():
    # returns the date where this data comes from    
    return (parsed['general']['subtext']).removesuffix('<br>')


def csvfile():
    re
    #returns the csvfile for cases in each state
    return










pprint.pprint(data)




 


















