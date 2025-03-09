import datetime
import matplotlib.pyplot as plt
import cartopy.feature
import cartopy.crs as ccrs
from cartopy.feature.nightshade import Nightshade
import cartopy.feature as cfeature

import matplotlib

matplotlib.use('agg')



import maps


airports = maps.read_airports('data/airports.csv')
flights = maps.read_flights_json('data/flights.json', airports)

fig = maps.plot_miles(flights)
fig.savefig('public/distances.png', bbox_inches='tight')

result = maps.make_html(flights, airports)
f2 = open('public/index.html', mode='w')
f2.write(result)
f2.close()

fig = maps.plot_map(flights, airports)
fig.savefig('public/earth.png', bbox_inches='tight')

fig = maps.plot_map(flights, airports, globe_north=True)
fig.savefig('public/globe_north.png', bbox_inches='tight')

fig = maps.plot_map(flights, airports, globe_south=True)
fig.savefig('public/globe_south.png', bbox_inches='tight')

fig = maps.plot_map(flights, airports, europe=True)
fig.savefig('public/europe.png', bbox_inches='tight')

fig = maps.plot_map(flights, airports, america=True)
fig.savefig('public/america.png', bbox_inches='tight')

fig = maps.plot_map(flights, airports, australia=True)
fig.savefig('public/australia.png', bbox_inches='tight')
