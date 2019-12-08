
This is a program that help user generate a list of national heritage site in Africa based on their search query

The data were gathered by scraping the National Heritage Sites in Africa on wikipedia (https://en.wikipedia.org/wiki/List_of_World_Heritage_Sites_in_Africa). For each location, I then found its link to GeoHack page (https://tools.wmflabs.org/geohack/geohack.php?pagename=List_of_World_Heritage_Sites_in_Africa&params=20.158611_S_57.503056_E_&title=Aapravasi+Ghat) and got its longitude and latitude. All the data were then store in to the sqlite3 data base.

This program uses plotly(https://plot.ly/python/getting-started/)to generate the map for the users.

The user can start the program by running the final.py file in the terminal. The program will ask users to input the commend. There's three main command line that users can choose from:

1. SiteName
	Description: Lists the detail of the site.


2. CountryName

	Description: Lists all the sites in that country

	Options:
		* Criteria=<criteria>
		Description: Specifies a criteria of the sites in that country
		- Cultural / Natural

		* Year
		Description: Sorted by year. Default sort by name

3. Criteria
	Description: Lists all the sites of that criteria

	Options:
	* Year
	Description: Sorted by year. Default sort by name

Once the user inputs the query, the program will get the data from the database and processes it through the class "HeritageSite". The HeritageSite instance will have the site's name, country, region, criteria, longitude and latitude, year and description.

The search result will be displayed in the terminal. The user can download the csv file of the search result by typing "csv" into the commend line or type "map" to see the map on browser.
