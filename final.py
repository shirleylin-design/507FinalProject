from secrets import *
import requests
import json
from bs4 import BeautifulSoup
import plotly.graph_objs as go
from plotly.graph_objs import *
import sys
import sqlite3
import csv


# ========================== build a data base ==========================
# Part 1: Read data from CSV and JSON into a new database called choc.db
DBNAME = 'Heritage_Sites.db'

def init_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    # Drop tables
    statement = '''
        DROP TABLE IF EXISTS 'Countries';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'HeritageSites';
    '''
    cur.execute(statement)

    conn.commit()

    statement = '''
        CREATE TABLE 'Countries' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'CountryName' TEXT,
            'Region' TEXT
);
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'HeritageSites' (
              'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
              'SiteName' TEXT NOT NULL,
              'CountryId' TEXT NOT NULL,
              'Criteria' TEXT NOT NULL,
              'Longtitude' INTEGER,
              'Latitude' INTEGER,
              'Area' TEXT,
              'Year' INTEGER,
              'Description' TEXT,
              FOREIGN KEY(CountryId) REFERENCES Countries(Id)
);
    '''
    cur.execute(statement)

    conn.commit()
    conn.close()

if len(sys.argv) > 1 and sys.argv[1] == '--init':

    print('Deleting db and starting over from scratch.')
    init_db()

else:
    print('Leaving the DB alone.')

# init_db()
# ========================== cache ==========================

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}

# A helper function that accepts 2 parameters
# and returns a string that uniquely represents the request
# that could be made with this info (url + params)

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_" + "_".join(res)


def get_unique_key(url):
  return url

def make_request_using_cache(url, header):
    unique_ident = get_unique_key(url)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url, headers=header)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

# ========================== other functions ==========================
baseurl = 'https://en.wikipedia.org'
header = {'User-Agent': 'SI_CLASS'}

def get_gps(gps_url):
    url = 'http://' + gps_url
    gps_page = make_request_using_cache(url, header)
    soup = BeautifulSoup(gps_page, 'html.parser')
    latitude = soup.find(class_ = 'latitude').text
    longtitude = soup.find(class_ = 'longitude').text
    gps = [latitude, longtitude]
    return (gps)

def convert(list):
    return tuple(list)

def get_country_id(name):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    base_statement = 'SELECT Id, CountryName FROM Countries WHERE '
    statement = ''
    filter_statement =  'Countries.CountryName = "{}"'.format(str(name))
    statement = base_statement + filter_statement
    cur.execute(statement)
    lst = cur.fetchall()
    id = lst[0][0]
    return id

def load_help_text():
    with open('help.txt') as f:
        return f.read()
# ========================== writing data to database==========================

def insert_stuff_countries(list):

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    countries_dic = {}
    for country in list:
        insertion = convert(country)
        statement = 'INSERT INTO "Countries" (CountryName, Region)'
        statement += 'VALUES (?, ?)'
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()


def insert_stuff_sites(list):

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    countries_dic = {}
    for site in list:
        insertion = convert(site)
        statement = 'INSERT INTO "HeritageSites" (SiteName, CountryId, Criteria, Latitude, Longtitude, Area, Year, Description)'
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()


# ========================== crawling from wiki ==========================


def get_sites_for_region(region_url, region):

    url = baseurl + region_url
    region_sites_list = make_request_using_cache(url, header)
    soup = BeautifulSoup(region_sites_list, 'html.parser')
    table_div = soup.find(class_='wikitable')
    table_body = table_div.find('tbody')
    table_rows = table_body.find_all('tr')

    countries = []
    for row in table_rows[1:len(table_rows)]:

        td_container = row.find_all('td')
        if len(td_container) == 6:
            countryName= td_container[1].find_all('a')[-2].text.strip()

            country = []
            if any(countryName in sublist for sublist in countries) == False:
                country.append(str(countryName))
                country.append(str(region))
                countries.append(country)

    insert_stuff_countries(countries)

    sites = []
    for row in table_rows[1:len(table_rows)]:
        if len(td_container) == 6:
            td_container = row.find_all('td')
            site = []
            sitename = row.find('th').text.strip()
            site.append(sitename)

            countryName= td_container[1].find_all('a')[-2].text
            site.append(get_country_id(countryName))

            criteria = td_container[2].text.split(':')[0]
            site.append(criteria)

            gps_url = td_container[1].find_all('a')[-1]['href'][2:]
            gps = get_gps(gps_url)
            site.append(gps[0])
            site.append(gps[1])

            area = td_container[3].text.strip()

            if area == '—':
                site.append('NULL')
            else:
                site.append(area)

            year = td_container[4].text.strip()
            site.append(year)

            description = td_container[5].text.strip()
            site.append(description)

            sites.append(site)

    insert_stuff_sites(sites)



# ========================== process data==========================

class WorldHeritage():

    def __init__(self, row):

            self.sitename = row[0]
            self.country = row[1]
            self.region = row[2]
            self.criteria = row[3]
            self.longtitude = row[4]
            self.latitude = row[5]
            if row[6] != 'NULL':
                self.area = row[6]
            else:
                self.area = 'No Info'
            self.year = row[7]
            self.description = row[8]

    def __str__(self):
         return ("{} is a {} heritage site in {}").format(self.sitename, self.criteria, self.country)

# ========================== process user command ==========================

def process_command(command):

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    command_lst = command.split()

    statement = ''
    base = 'SELECT SiteName, c.CountryName, c.Region, Criteria, Longtitude, Latitude, Area, [Year], Description FROM HeritageSites JOIN Countries as c ON HeritageSites.CountryId = c.Id WHERE '
    sort = 'ORDER BY SiteName'

    command_len = len(command_lst)

    if 'SiteName' in command:

        if '_'in command.split('=')[1]:
            sitename = command.split('=')[1].replace('_',' ')
        else:
            sitename = command


        statement = "SELECT SiteName, c.CountryName, c.Region, Criteria, Longtitude, Latitude, Area, [Year], Description FROM HeritageSites JOIN Countries as c ON HeritageSites.CountryId = c.Id WHERE SiteName = '{}'".format(sitename)


    else:

        if "Year" in command:
            sort = "ORDER BY [Year]"
            command_len = command_len-1
            command_lst.remove('Year')

        if command_len > 1:

            for command in command_lst:

                if 'CountryName' in command:
                        country = command.split('=')[1]

                if 'Criteria' in command:
                    criteria = command.split('=')[1]


            filter_statement = 'CountryName = "{}" AND Criteria = "{}" '.format(country, criteria)

        else:
            filterName = command_lst[0].split('=')[0]
            filterQuery = command_lst[0].split('=')[1]
            filter_statement = '{} = "{}"'.format(filterName,filterQuery)


        statement = base + filter_statement + sort

    cur.execute(statement)
    lst = cur.fetchall()
    return lst
    conn.close()

# ========================== plot site map ==========================

def plot_sites_for_site(lst):

    lat_vals = []
    lon_vals = []
    text_vals = []

    for row in lst:

        site = WorldHeritage(row)
        lat_vals.append(site.latitude)
        lon_vals.append(site.longtitude)
        text_vals.append('{}:{}'.format(site.sitename, site.description))


    min_lat = float(min(lat_vals))
    max_lat = float(max(lat_vals))
    min_lon = float(min(lon_vals))
    max_lon = float(max(lon_vals))

    lat_axis = [min_lat, max_lat]
    lon_axis = [max_lon, min_lon]


    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    fig = go.Figure(go.Scattermapbox(
            lat=lat_vals,
            lon=lon_vals,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14
            ),
            text=text_vals,
        ))


    layout = dict(
        # title =
        hovermode='closest',
        mapbox=dict(
            accesstoken=MAPBOX_TOKEN,
            center = go.layout.mapbox.Center(
                lat=center_lat,
                lon=center_lon
            ),
            bearing=0,
            pitch=0,
            zoom=5),
        )

    fig.update_layout(
            title = 'Heritage Sites in Africa Based on Your Queries',
        )

    fig.update_layout(layout)
    fig.show()


def plot_bar_chart(lst):

    x = []
    y = []
    year_count = {}
    text = []
    for row in lst:
        site = WorldHeritage(row)

        if site.year in year_count.keys():
            year_count[site.year] += 1

        else:
            year_count[site.year] = 1

    year = list(year_count.keys())
    count = list(year_count.values())

    fig = go.Figure([go.Bar(x=year, y=count)])

    fig.update_layout(
            title = 'Heritage Sites Count By Year',
        )


    fig.show()


# ========================== write csv ==========================

def write_csv (lst):


    with open('heritage.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['SiteName','Country','Criteria','Year','Description'])

        for row in lst:
            site = WorldHeritage(row)
            spamwriter.writerow([site.sitename, site.country, site.criteria, site.year, site.description])

# ========================== interactrive promot ==========================

def check_paras(response):
    user_parameters = response.split()
    check = True

    for parameter in user_parameters:

        params = ['CountryName','Criteria','Year','SiteName']

        if '=' in parameter:
            parameter = parameter.split('=')[0]

        if parameter not in params:
            check = False
            break

    return check


def interactive_prompt():

    help_text = load_help_text()
    response = ''

    while response != 'exit':

        response = input('Enter a command: ')

        if response and response.isspace() == False:

            if response == 'help':
                print(help_text)

            elif check_paras(response) == True:

                lst = process_command(response)

                if len(lst) > 1:
                    n = 1
                    for row in lst:
                        site = WorldHeritage(row)
                        print(str(n) + "{: >50} {: >50} {: >50} {: >50}".format(site.sitename, site.country, site.criteria,site.year))
                        n = n+1

                    choice = input("Type 'csv' to download the result, 'map' to see the map, 'bar' to see barchart or 'all' to see all the charts")

                    if choice == 'csv':
                        write_csv (lst)

                    elif choice == 'map':
                        plot_sites_for_site(lst)


                    elif choice =='bar':
                        plot_bar_chart(lst)


                    elif choice =='all':
                        write_csv (lst)
                        plot_sites_for_site(lst)
                        plot_bar_chart(lst)

                    else:
                        print("No commend found. Type 'csv' to download the result, 'map' to see the map, 'bar' to see barchart or 'all' to see all the charts")


                else:
                    print('No result found. Please enter another search')

            else:
                print('Command not recognized: ' + response)

        else:
            print('Command not recognized: ' + response)

    else:
        print('bye')
        sys.exit()


if __name__ == "__main__":

     interactive_prompt()
