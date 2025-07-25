import collections
import datetime
import numpy as np
from yattag import Doc, indent


engine_manufacts_abbr = \
    dict(PW='Pratt & Whitney', GE='General Electric', RR='Rolls Royce', CFMI='CFM International',
         IAE='International Aero Engines', PWC='Pratt & Whitney Canada', LY='Lycoming',
         EA='Engine Alliance', GAR='Garrett AiResearch', CM='Continental Motors')


cities = {'LON': ['LHR', 'LGW', 'LCY', 'LTN', 'STN', 'SEN', 'BQH'],
          'MOW': ['SVO', 'DME', 'VKO'],
          'MIL': ['MXP', 'LIN'],
          'PAR': ['CDG', 'ORY', 'LBG'],
          'ROM': ['FCO', 'CIA'],
          'STO': ['ARN', 'BMA', 'NYO'],
          'CHI': ['ORD', 'MDW'],
          'QDF': ['DFW', 'DAL'],
          'QHO': ['IAH', 'HOU'],
          'QLA': ['LAX', 'ONT', 'SNA', 'BUR', 'LGB'],
          'QMI': ['MIA', 'FLL', 'PBI'],
          'NYC': ['JFK', 'LGA', 'EWR'],
          'QSF': ['SFO', 'SJC', 'OAK'],
          'WAS': ['IAD', 'DCA', 'BWI'],
          'BJS': ['PEK', 'NAY'],
          'OSA': ['KIX', 'ITM', 'UKB'],
          'SEL': ['ICN', 'GMP'],
          'REK': ['KEF', 'RKV'],
          'YTO': ['YYZ', 'YTZ']}


city_names = {'LON':'London',
              'MOW': 'Moscow',
              'MIL': 'Milan',
              'PAR': 'Paris',
              'ROM': 'Rome',
              'STO': 'Stockholm',
              'CHI': 'Chicago',
              'QDF': 'Dallas-Fort Worth',
              'QHO': 'Houston',
              'QLA': 'Los Angeles',
              'QMI': 'Miami',
              'NYC': 'New York City',
              'QSF': 'San Francisco',
              'WAS': 'Washington DC',
              'BJS': 'Beijing',
              'OSA': 'Osaka',
              'SEL': 'Seoul',
              'REK': 'Reykjavík',
              'YTO': 'Toronto'}


cities_inv = dict(cities)
cities = dict((v, k) for k in cities_inv for v in cities_inv[k])


def write_city(city, airports_tally):
    airports = cities_inv[city]
    abbr = ''
    for airport in airports:
        count = airports_tally.count(airport)
        try:
            abbr += airport + ' (' + str(count) + '), '
        except IndexError:
            abbr += airport + ' (0), '
    abbr = abbr[:-2]
    # text = '<abbr title="' + abbr + '">' + city + '</abbr>'
    text = '<abbr title="{}">{}</abbr>'.format(abbr, city)
    return text


def write_segment(segment, direction='one-way'):
    """Generate the HTML representation of a segment.

    Args:
        segment (list): a list of two airport objects
        direction (str): one-way or return

    Returns:
        string: HTML code for the segment with arrow and abbreviations
    """
    if direction=='return':
        s = segment[0].write_airport() + ' &rlarr; ' + segment[1].write_airport()
    else:
        s = segment[0].write_airport() + ' &rarr; ' + segment[1].write_airport()
    return s


def gc_distance(airport1, airport2):
    """Calculate the distance in statute miles between two airports.

    Parameters
    ----------
    airport1 : Airport
    airport2 : Airport

    Returns
    -------
    float
        the distance in statute miles between the two airports
    """
    p1 = airport1.lat * 2.0 * np.pi/360
    p2 = airport2.lat * 2.0 * np.pi/360
    l1 = airport1.lon * 2.0 * np.pi/360
    l2 = airport2.lon * 2.0 * np.pi/360
    r = 3963.19
    gcd = 2 * r * np.arcsin(np.sqrt(np.sin((p2-p1)/2)**2 + np.cos(p1) * np.cos(p2) * np.sin((l2-l1)/2)**2))
    return gcd


class HtmlTable:
    def __init__(self, title, row_names, counts, html=False, html_count=False):
        self.title = title
        self.row_names = row_names
        self.counts = counts

        self.html = html
        self.html_count = html_count

    def __str__(self):
        doc, tag, text = Doc().tagtext()

        with tag('table', klass='log-table'):
            with tag('tr'):
                with tag('th', colspan=2):
                    text(self.title)
            for row, count in zip(self.row_names, self.counts):
                with tag('tr'):
                    with tag('td'):
                        if not self.html:
                            text(row)
                        else:
                            doc.asis(row)
                    with tag('td'):
                        if not self.html_count:
                            text(count)
                        else:
                            doc.asis(count)

        return indent(doc.getvalue())


class TallyTable(HtmlTable):
    def __init__(self, flights, airports):
        num_flights = len(flights)

        all_airports = []
        for flight in flights:
            all_airports += list(flight.route[0])
            for leg in flight.route[1:]:
                all_airports += [leg[1]]

        num_airports = len(set(all_airports))

        num_airplane_types = len(set([flight.type2 for flight in flights]))

        total_distance = 0
        num_segments = 0
        for flight in flights:
            for leg in flight.route:
                total_distance += gc_distance(*leg)
                num_segments += 1

        mean_segment_distance = total_distance / num_segments

        super().__init__('Tallies',
            ['Flights',
             'Unique airports',
             'Unique airplane types',
             'Total distance',
             'Mean segment distance'],
            [str(num_flights),
             str(num_airports),
             str(num_airplane_types),
             '{} mi <br> {:.02f} &#xd7; 2&#x3c0;R<sub>&#x2295;</sub>'.format(round(total_distance), total_distance/24901 ),
             '{} mi'.format(round(mean_segment_distance))], html_count=True)


class SuperTable:
    def __init__(self, flights, airports):

        segments = []
        distances = []
        visited_airports = []
        for flight in flights:
            for segment in flight.route:
                if segment[0] != segment[1]:
                    segments.append(segment)
                    distances.append(gc_distance(*segment))
                visited_airports.append(segment[0])
                visited_airports.append(segment[1])

        visited_airports = list(set(visited_airports))

        longest_segment = segments[distances.index(max(distances))]
        longest_distance = max(distances)

        shortest_segment = segments[distances.index(min(distances))]
        shortest_distance = min(distances)

        lats = [airport.lat for airport in visited_airports]

        northernmost = visited_airports[lats.index(max(lats))]
        northernmost_lat = max(lats)

        southernmost = visited_airports[lats.index(min(lats))]
        southernmost_lat = min(lats)

        self.title = 'Superlatives'
        self.rows = ['Longest segment', 'Shortest segment', 'Northernmost airport', 'Southernmost airport']
        self.values1 = [write_segment(longest_segment), write_segment(shortest_segment), northernmost.write_airport(), southernmost.write_airport()]
        self.values2 = ['{} mi'.format(round(longest_distance)), '{:.01f} mi'.format(shortest_distance), '{:.02f}&#176;'.format(northernmost_lat), '&#x2212;{:.02f}&#176;'.format(-southernmost_lat)]

    def __str__(self):
        doc, tag, text = Doc().tagtext()

        with tag('table', klass='log-table'):
            with tag('tr'):
                with tag('th', colspan=3):
                    text(self.title)
            for row, value1, value2 in zip(self.rows, self.values1, self.values2):
                with tag('tr'):
                    with tag('td'):
                        text(row)
                    with tag('td'):
                        doc.asis(value1)
                    with tag('td'):
                        doc.asis(value2)

        return indent(doc.getvalue())


class HtmlTableLocations(HtmlTable):
    def __init__(self, flights, airports, attr=None, restrict=None, title=None, dropdown_attrs1=None, dropdown_attr2=None):
        """
        restrict : (attr(str), value(str))
        """
        all_airports_objects = []
        for flight in flights:
            all_airports_objects += list(flight.route[0])
            for leg in flight.route[1:]:
                all_airports_objects += [leg[1]]

        if attr is not None:
            if restrict is not None:
                all_airports = [getattr(a, attr) for a in all_airports_objects if getattr(a, restrict[0]) == restrict[1]]
            else:
                all_airports = [getattr(a, attr) for a in all_airports_objects]

            counts = collections.Counter(all_airports)
            counts = sorted(counts.most_common(), key=lambda x: (-x[1], x[0]))

        else:
            counts = collections.Counter(all_airports_objects)
            counts = sorted(counts.most_common(), key=lambda x: (-x[1], x[0].iata or x[0].name))

        if title is None:
            title = 'Locations'
        if attr is None:
            super().__init__(title, [x[0].write_airport() for x in counts], [x[1] for x in counts], html=True)
        else:
            super().__init__(title, [x[0] for x in counts], [x[1] for x in counts], html=True)

        self.dropdown = False
        if dropdown_attrs1 is not None and dropdown_attr2 is not None:
            row_names = [x[0] for x in counts]
            counts = [x[1] for x in counts]
            row_subtables = []
            
            for row in row_names:
                if row in dropdown_attrs1:
                    list_of_attrs = [getattr(a, dropdown_attr2) for a in all_airports_objects if getattr(a, attr) == row]

                    if len(set(list_of_attrs)) == 1 and list_of_attrs[0] == '':
                        row_subtables.append(None)

                    else:
                        list_of_attrs = [x for x in list_of_attrs if x != '']
                        subcounts = collections.Counter(list_of_attrs)
                        subcounts = sorted(subcounts.most_common(), key=lambda x: (-x[1], x[0]))
                        row_subtables.append(([x[0] for x in subcounts], [x[1] for x in subcounts]))
                else:
                    row_subtables.append(None)
                    
            self.row_subtables = row_subtables
            super().__init__(title, row_names, counts)
            self.dropdown = True
            self.dropdown_table = HtmlTableDropdown(flights, 'cxr', 'ope_cxr', title='Countries')
            self.dropdown_table.row_names = row_names
            self.dropdown_table.counts = counts
            self.dropdown_table.row_subtables = row_subtables

    def __str__(self):
        if not self.dropdown:
            return super().__str__()
        else:
            return self.dropdown_table.__str__()


class HtmlTableCities(HtmlTable):
    def __init__(self, flights, airports):
        all_airports = []
        for flight in flights:
            all_airports += list(flight.route[0])
            for leg in flight.route[1:]:
                all_airports += [leg[1]]

        counts = collections.Counter(all_airports)
        counts = sorted(counts.most_common(), key=lambda x: (-x[1], x[0].iata or x[0].name))

        row_names = [x[0].iata for x in counts]
        counts = [x[1] for x in counts]

        cities_tally = collections.Counter()

        for airport, count in zip(row_names, counts):
            try:
                cities_tally[cities[airport]] += count
            except KeyError:
                pass

        counts = sorted(cities_tally.most_common(), key=lambda x: (-x[1], x[0]))

        city_rows = [x[0] for x in counts]
        city_counts = [x[1] for x in counts]

        for i, city in enumerate(city_rows):
            name = write_city(city, [a.code for a in all_airports])
            city_rows[i] = name

        super().__init__('Cities', city_rows, city_counts, html=True)


class HtmlTableAirplanes(HtmlTable):
    def __init__(self, flights, attrs, title=None):
        list_of_attrs = [' '.join(getattr(flight, attr) for attr in attrs) for flight in flights]
        counts = collections.Counter(list_of_attrs)
        counts = sorted(counts.most_common(), key=lambda x: (-x[1], x[0]))

        if title is None:
            title = attrs[0]

        super().__init__(title, [x[0] for x in counts], [x[1] for x in counts])


class HtmlTableDropdown(HtmlTable):
    def __init__(self, flights, attr1, attr2, title=None):
        if title is None:
            title = attr1

        list_of_attrs = [getattr(flight, attr1) for flight in flights]
        counts = collections.Counter(list_of_attrs)
        counts = sorted(counts.most_common(), key=lambda x: (-x[1], x[0]))

        row_names = [x[0] for x in counts]
        counts = [x[1] for x in counts]

        row_subtables = []

        for row in row_names:
            list_of_attrs = [getattr(flight, attr2) for flight in flights if getattr(flight, attr1) == row]

            if len(set(list_of_attrs)) == 1 and list_of_attrs[0] == '':
                row_subtables.append(None)

            else:
                list_of_attrs = [x for x in list_of_attrs if x != '']
                subcounts = collections.Counter(list_of_attrs)
                subcounts = sorted(subcounts.most_common(), key=lambda x: (-x[1], x[0]))
                row_subtables.append(([x[0] for x in subcounts], [x[1] for x in subcounts]))

        self.row_subtables = row_subtables
        super().__init__(title, row_names, counts)

    def __str__(self):
        doc, tag, text = Doc().tagtext()

        with tag('table', klass='log-table'):
            with tag('tr'):
                with tag('th', colspan=2):
                    text(self.title)
            for row, count, subtable in zip(self.row_names, self.counts, self.row_subtables):
                if subtable is None:
                    with tag('tr'):
                        with tag('td'):
                            text(row)
                        with tag('td'):
                            text(count)

                else:
                    subrows = subtable[0]
                    subcounts = subtable[1]
                    expand_script = '''$(this).nextAll(':lt(''' + \
                                    str(len(subrows)) + \
                                    ''')').toggle()'''
                    with tag('tr', onClick=expand_script):
                        with tag('td'):
                            doc.asis(row + '<span style="font-size: 8px"> &#9654;</span>')
                        with tag('td'):
                            text(count)
                    for subrow, subcount in zip(subrows, subcounts):
                        with tag('tr', style='display:none;'):
                            with tag('td'):
                                with tag('span', style='color:gray;font-style:italic;'):
                                    doc.asis('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
                                    text(subrow)
                            with tag('td', style='text-align:right;'):
                                with tag('span', style='color:gray;font-style:italic;'):
                                    text(subcount)

        return indent(doc.getvalue())


class LogTable:
    def __init__(self, flights, airports):
        self.flights = flights
        self.airports = airports

    def __str__(self):
        doc, tag, text = Doc().tagtext()

        cols = ['Date', 'Number', 'Route', 'Airline', 'Airplane', 'Photographs', '...']

        with tag('table', klass='log-table'):
            with tag('tr'):
                for col in cols:
                    with tag('th'):
                        text(col)

            for i, flight in enumerate(self.flights):
                with tag('tr'):
                    with tag('td'):
                        text(flight.date.strftime("%Y %b %d"))

                    with tag('td'):
                        text((flight.desig or '') + (flight.number or ''))

                    with tag('td'):
                        doc.asis(flight.route_str)

                    with tag('td'):
                        if flight.ope_cxr != flight.cxr and flight.cxr != None and flight.ope_cxr != '':
                            doc.text(f'{flight.cxr} (operated by {flight.ope_cxr})')
                        else:
                            doc.text(flight.cxr)

                    with tag('td'):
                        doc.text(f'{flight.manufacturer} {flight.type3} ({flight.registration})')

                    with tag('td'):
                        if flight.pics is not None:
                            for pic in flight.pics:
                                with tag('a', target='_blank', href=pic):
                                    doc.stag('img', loading='lazy', src=pic, klass='log')
                            if flight.trip_pics is not None:
                                # doc.asis('<span class="material-symbols-rounded" style="font-size:140%;">travel</span>')
                                doc.asis('<span class="material-symbols-rounded" style="font-size:140%;">landscape</span>')
                        else:
                            if flight.trip_pics is not None:
                                # doc.asis('<span class="material-symbols-rounded" style="font-size:140%;">travel</span>')
                                doc.asis('<span class="material-symbols-rounded" style="font-size:140%;">landscape</span>')
                            else:
                                doc.text('')


                    with tag('td'):
                        with tag('a', klass='expand', onclick=f'toggle2("f{i}","f{i}ud");clean(document.body)'):
                            with tag('span', id=f'f{i}ud', klass='downarrowk'):
                                text()

                    with tag('tr', klass='row_closed', id=f'f{i}'):
                        with tag('td', colspan=7, style='text-align:right;'):

                            if flight.pics is not None:
                                with tag('div', style='display:inline-block;'):
                                    for pic in flight.pics:
                                        with tag('a', href=pic, target='_blank'):
                                            doc.stag('img', loading='lazy', src=pic, klass='zoom')
                            if flight.trip_pics is not None:
                                if flight.pics is not None:
                                    if len(flight.trip_pics) > 4:
                                        doc.stag('br')
                                #    doc.asis('<div style="border-left:1px solid #000;height:150px;display:inline-block;vertical-align:middle;"></div>')
                                
                                with tag('div', style='display:inline-block;'):
                                    i = 0
                                    for pic in flight.trip_pics:
                                        if i % 4 == 0 and i > 0:
                                            doc.stag('br')
                                            
                                        with tag('a', href=pic, target='_blank'):
                                            doc.stag('img', loading='lazy', src=pic, klass='zoom')
                                        i += 1

                            with tag('div', style='display:inline-block;vertical-align:top;'):
                                with tag('table', klass='bare'):
                                    dist = 0
                                    for leg in flight.route:
                                        dist += gc_distance(*leg)
                                    with tag('tr'):
                                        with tag('td'):
                                            text('gc distance')
                                        with tag('td'):
                                            text('{} mi'.format(round(dist)))

                                    if flight.cabin is not None:
                                        if flight.seat is not None:
                                            with tag('tr'):
                                                with tag('td'):
                                                    text('seat')
                                                with tag('td'):
                                                    text(flight.seat + ' (' + flight.seat_type + ', ' +
                                                         flight.cabin + ')')

                                    for attr in ['msn', 'ln']:
                                        if getattr(flight, attr) is not None:
                                            with tag('tr'):
                                                with tag('td'):
                                                    text(attr)
                                                with tag('td'):
                                                    text(getattr(flight, attr))

                                    if flight.sta is not None:
                                        with tag('tr'):
                                            with tag('td'):
                                                text('std/sta')
                                            with tag('td'):
                                                text('{}/{}'.format(flight.std, flight.sta))

                                    if flight.first_flight is not None:
                                        d = flight.first_flight
                                        if len(d) == 8:
                                            date_first_flight = datetime.datetime(int(d[:4]), int(d[4:6]), int(d[6:]))
                                            ff_str = date_first_flight.strftime("%Y %b %d")
                                        elif len(d) == 6:
                                            date_first_flight = datetime.datetime(int(d[:4]), int(d[4:6]), 14)
                                            ff_str = date_first_flight.strftime("%Y %b")
                                        elif len(d) == 4:
                                            date_first_flight = datetime.datetime(int(d[:4]), 6, 14)
                                            ff_str = date_first_flight.strftime("%Y")
                                        else:
                                            raise

                                        with tag('tr'):
                                            with tag('td'):
                                                text('airplane age')
                                            with tag('td'):
                                                text('{} years'.format(round((flight.date - date_first_flight).days / 365.25)))

                                        with tag('tr'):
                                            with tag('td'):
                                                text('first flight')
                                            with tag('td'):
                                                text(ff_str)

        return indent(doc.getvalue())

def make_html(flights, airports):
    doc, tag, text = Doc().tagtext()

    with tag('html'):
        with tag('head'):
            doc.stag('meta', charset='utf-8')
            doc.stag('meta', name='robots', content='noindex,nofollow,noimageindex')
            doc.stag('link', rel='stylesheet', type='text/css', href='style.css')
            with tag('script', src='toggle.js'):
                pass
            with tag('script', src='jquery-3.7.1.slim.min.js'):
                pass
            with tag('title'):
                text('Flights')

            doc.asis('<link rel="preconnect" href="https://fonts.googleapis.com">')
            doc.asis('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')

            doc.asis('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,400,0,0" />')
            # doc.asis('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&icon_names=travel" />')

            doc.asis('<link rel="stylesheet" href="https://indestructibletype.com/fonts/Jost.css" type="text/css" charset="utf-8" />')

        with tag('body', onload='clean(document.body)'):
            with tag('div', klass='titles', onclick='toggle("airplanes","airplanesud");clean(document.body)'):
                with tag('span', id='airplanesud', klass='downarrow'):
                    text()
                text('Airplanes')
            doc.stag('hr')

            with tag('div', id='airplanes', klass='tab_closed'):
                table = HtmlTableAirplanes(flights, ['manufacturer', 'type2'], title='Airplanes')
                doc.asis(str(table))

                table = HtmlTableDropdown(flights, 'cxr', 'ope_cxr', title='Airlines')
                doc.asis(str(table))

                table = HtmlTableAirplanes(flights, ['manufacturer'], title='Manufacturers')
                doc.asis(str(table))

            with tag('div', klass='titles', onclick='toggle("locations","locationsud");clean(document.body)'):
                with tag('span', id='locationsud', klass='downarrow'):
                    text()
                text('Locations')
            doc.stag('hr')

            with tag('div', id='locations', klass='tab_closed'):
                table = HtmlTableLocations(flights, airports, title='Airports')
                doc.asis(str(table))

                table = HtmlTableCities(flights, airports)
                doc.asis(str(table))

                table = HtmlTableLocations(flights, airports, attr='region', restrict=('country', 'United States'), title='American states')
                doc.asis(str(table))

                # table = HtmlTableLocations(flights, airports, attr='region', restrict=('country', 'France'), title='French Regions')
                # doc.asis(str(table))

                # table = HtmlTableLocations(flights, airports, attr='region', restrict=('country', 'Australia'), title='Australian states')
                # doc.asis(str(table))

                table = HtmlTableLocations(flights, airports, attr='country', title='Countries', dropdown_attrs1=('France', 'Australia'), dropdown_attr2='region')
                doc.asis(str(table))

                table = HtmlTableLocations(flights, airports, attr='continent', title='Continents &c.')
                doc.asis(str(table))

            with tag('div', klass='titles', onclick='toggle("misc","miscud");clean(document.body)'):
                with tag('span', id='miscud', klass='downarrow'):
                    text()
                text('Misc')
            doc.stag('hr')

            with tag('div', id='misc', klass='tab_closed'):
                with tag('div'):
                    table = TallyTable(flights, airports)
                    doc.asis(str(table))

                    table = SuperTable(flights, airports)
                    doc.asis(str(table))

                with tag('div'):
                    doc.stag('img', src='distances.png', klass='graphs')

            # with tag('div', klass='titles', onclick='toggle("globes","globesud");clean(document.body)'):
            #     with tag('span', id='globesud', klass='uparrow'):
            #         text()
            #     text('Globes')
            # doc.stag('hr')

            # with tag('div', id='globes', style='margin-bottom:18px;display:block;'):
                with tag('div'):
                    with tag('a', href='globe_north.png', target='_blank'):
                        doc.stag('img', src='globe_north.png', klass='globes_thumbs')

                    with tag('a', href='globe_south.png', target='_blank'):
                        doc.stag('img', src='globe_south.png', klass='globes_thumbs')

            with tag('div', klass='titles', onclick='toggle("maps","mapsud");clean(document.body)'):
                with tag('span', id='mapsud', klass='uparrow'):
                    text()
                text('Maps')
            doc.stag('hr')

            with tag('div', id='maps', style='margin-bottom:18px;display:block;'):
                with tag('div'):
                    with tag('a', href='america.png', target='_blank'):
                        doc.stag('img', src='america.png', klass='maps_thumbs')

                    with tag('a', href='earth.png', target='_blank'):
                        doc.stag('img', src='earth.png', klass='maps_thumbs')

                    with tag('a', href='europe.png', target='_blank'):
                        doc.stag('img', src='europe.png', klass='maps_thumbs')

                    with tag('a', href='australia.png', target='_blank'):
                        doc.stag('img', src='australia.png', klass='maps_thumbs')

            with tag('div', klass='titles', onclick='toggle("log","logud");clean(document.body)'):
                with tag('span', id='logud', klass='uparrow'):
                    text()
                text('Log')
            doc.stag('hr')

            with tag('div', id='log', style='margin-bottom:18px;display:block;'):
                with tag('div'):
                    table = LogTable(flights, airports)
                    doc.asis(str(table))

        with tag('script', id='jsbin-javascript'):
            text('$(".log-table td a.expand").click(function(){$(this).closest("tr").next().toggle();});')
        with tag('script'):
            doc.asis('function clean(node){for(var n = 0; n < node.childNodes.length; n ++){var child = node.childNodes[n];if(child.nodeType === 8 || (child.nodeType === 3 && !/\S/.test(child.nodeValue))){node.removeChild(child);n --;}else if(child.nodeType === 1){clean(child);}}}')

    return indent(doc.getvalue())
