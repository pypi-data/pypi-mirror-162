


import pandas as pd
import requests
import io

csvcountry = requests.get('https://www.cdc.gov/wcms/vizdata/poxvirus/monkeypox/data/MPX-Cases-by-Country.csv')
ioobjectstring = io.StringIO(csvcountry.content.decode('utf-8'))
df = pd.read_csv(ioobjectstring)


# IO streams




def csvio():
    # returns the text I/O object for csv
    return ioobjectstring


def numcases(country):
    #returns number of cases for given country
    try:
        row = df[df['Country'] == country]
        return row['Cases']
    except ValueError:
        print("Country {} is not available.".format(country)) 



def totalconfirmedcases():
    #returns the total number of cases worldwide
    return sum(df['Cases'])
def newmonkeypox():
    # returns the total number of cases in countries that have already never experienced monkeypox in the past
    has = df[df['Category'] == 'Has not historically reported monkeypox']
    return sum(has['Cases'])


def notnewmonkeypox():
     # returns the total number of cases in countries that have already experienced monkeypox in the past
    return totalconfirmedcases() - newmonkeypox()


def countrynumbers():
    #returns the total number of countries tracked
    return df.shape[0]

def countrynumberswithout():
    #returns the number of countries who have not historically reported monkeypox
    has = df[df['Category'] == 'Has not historically reported monkeypox']
    return has.shape[0]

def countrynumberswith():
    return countrynumberswith() - countrynumberswithout()


















