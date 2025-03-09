import collections
import matplotlib
import matplotlib.pyplot as plt
import cartopy.feature
import cartopy.crs as ccrs
from cartopy.feature.nightshade import Nightshade
import cartopy.feature as cfeature
import numpy as np

import maps

def plot_miles(flights):
    distances = collections.defaultdict(list)

    for flight in flights:
        distance = 0
        for leg in flight.route:
            distance += maps.gc_distance(*leg)
        distances[flight.date.year].append(distance)

    annual_distances = []
    for year in distances.keys():
        annual_distances.append(sum(distances[year]))


    fig = plt.figure(figsize=(5, 3))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(distances.keys(), annual_distances, color='#8eb8b4', lw=2)

    ax.set_ylabel('Distance (miles)')
    ax.set_xlabel('Year')

    return fig


def plot_map(flights,
             airports,
             europe=False,
             america=False,
             australia=False,
             globe_north=False,
             globe_south=False):

    if europe:
        labels = True
        states = False
        projection = ccrs.Mercator(max_latitude=71.5, min_latitude=35.5,)
        projection._threshold = projection._threshold / 100.0

        fig = plt.figure(figsize=(10.5, 10.5))
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        # ax.set_global()
        ax.set_extent((-24, 30, 35.5, 71.5), crs=ccrs.PlateCarree())
        bounds = (-24, 30, 35.5, 71.5)

    elif america:
        labels = True
        states = True
        projection = ccrs.Mercator(max_latitude=62, min_latitude=-65)
        projection._threshold = projection._threshold / 100.0

        fig = plt.figure(figsize=(14, 14))
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        # ax.set_global()
        ax.set_extent((-161, -58, 16.5, 62), crs=ccrs.PlateCarree())
        bounds = (-161, -58, 16.5, 62)

    elif australia:
        labels = True
        states = True
        projection = ccrs.Mercator(max_latitude=62, min_latitude=-65)
        projection._threshold = projection._threshold / 100.0
      
        fig = plt.figure(figsize=(9.5, 9.5))
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        # ax.set_global()
        ax.set_extent((112.5, 179, -48, -8), crs=ccrs.PlateCarree())
        bounds = (112.5, 179, -48, -8)

    elif globe_north:
        labels = True
        states = False
        projection = ccrs.Orthographic(central_longitude=-60, central_latitude=60, globe=None)
        projection.threshold = projection.threshold / 100.0

        fig = plt.figure(figsize=(7, 7))
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.gridlines()
        ax.set_global()
        # ax.set_extent((-180, 180, -48, 90), crs=ccrs.PlateCarree())
        bounds = (-180, 180, -90, 90)

    elif globe_south:
        labels = True
        states = False
        projection = ccrs.Orthographic(central_longitude=-165, central_latitude=-7.5, globe=None)
        projection.threshold = projection.threshold / 100.0

        fig = plt.figure(figsize=(7, 7))
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.gridlines()
        ax.set_global()
        # ax.set_extent((-180, 180, -48, 90), crs=ccrs.PlateCarree())
        bounds = (-180, 180, -90, 90)
               
    else:
        labels = False
        states = False
        projection = ccrs.Mercator(max_latitude=80, min_latitude=-65)
        projection._threshold = projection._threshold / 100.0

        fig = plt.figure(figsize=(15, 15))
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.set_global()
        bounds = (-180, 180, -90, 90)


    ax.add_feature(cartopy.feature.LAND, color='#fad9ae', zorder=1)
    ax.add_feature(cartopy.feature.OCEAN, color='#8eb8b4', alpha=0.6)
    ax.add_feature(cartopy.feature.LAKES, color='#8eb8b4', alpha=0.6)
    ax.add_feature(cartopy.feature.COASTLINE,linewidth=0.4, zorder=2)
    ax.add_feature(cartopy.feature.BORDERS, linewidth=0.4, zorder=3)


    if states:
        usa_states = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='110m',
            edgecolor='k',
            facecolor='none')
        ax.add_feature(usa_states, linewidth=0.3, zorder=4)

    if australia:
        usa_states = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='50m',
            edgecolor='k',
            facecolor='none')
        ax.add_feature(usa_states, linewidth=0.3, zorder=4)

    airport_counts = collections.Counter()
    for flight in flights:
        for leg in flight.route:
            airport_counts[leg[0]] += 1
            airport_counts[leg[1]] += 1
            start = (leg[0].lat, leg[0].lon)
            end = (leg[1].lat, leg[1].lon)
            ax.plot((start[1], end[1]),
                    (start[0], end[0]),
                    color='k',
                    lw=1,
                    zorder=5,
                    transform=ccrs.Geodetic())

    texts = []
    for airport in airports.values():
        ax.scatter(
            airport.lon, airport.lat,
            color='k', s=20, zorder=6, transform=ccrs.PlateCarree())
        ax.scatter(
            airport.lon, airport.lat,
            color='white', s=3.25, zorder=7, transform=ccrs.PlateCarree())

        if labels:
            if bounds[0] < airport.lon < bounds[1] and bounds[2] < airport.lat < bounds[3]:
                t = ax.text(airport.lon, airport.lat, airport.iata, size=6.75,
                    zorder=6 + airport_counts[airport],
                    transform=ccrs.PlateCarree(), ha='center', va='center',
                    bbox={'facecolor': 'white', 'alpha': 1.0, 'edgecolor': 'k',
                          'boxstyle': 'round'})

    return fig
