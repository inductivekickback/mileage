"""Uses Google maps to compute the shortest-possible driving distances between all 4J schools."""
import sys
import csv
import argparse
import math
import pickle

import googlemaps


METERS_TO_MILES = 0.00062
SCHOOL_TYPE_INDX = 0
SCHOOL_ADDR_INDX = 1


def _import_addresses(file_name):
    d = {}
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        # NOTE: There are multiple locations with the same address but different names!
        for row in reader:
            addr = ','.join([s.strip() for s in
                          (row['Street Address'], row['City'], row['State'], row['Zip Code'])])
            d[row['Name']] = (row['Type'], addr)
    return d


def _generate_pairs(addresses):
    keys = list(addresses.keys())
    p = []
    c = []
    for i in range(0, len(keys)):
        for j in range(i+1, len(keys)):
            if addresses[keys[i]][SCHOOL_ADDR_INDX] != addresses[keys[j]][SCHOOL_ADDR_INDX]:
                p.append((keys[i], keys[j]))
            else:
                c.append((keys[i], keys[j]))
    return (p, c)


def _split_and_sort(addresses):
    result = []
    types = ('E', 'M', 'H', 'O')
    for t in types:
        l = [k for k, v in addresses.items() if v[SCHOOL_TYPE_INDX].upper() == t]
        l.sort(key=lambda s: s.upper())
        result.append(l)
    return result


def _convert_and_round(meters):
    # Round up to the nearest tenth of a mile.
    miles = meters * METERS_TO_MILES
    return math.ceil(miles * 10) / 10


def _query_dist(origin, dest, addresses, api_key):
    # Use the shortest-possible distance when traveling in either direction.
    o = addresses[origin][SCHOOL_ADDR_INDX]
    d = addresses[dest][SCHOOL_ADDR_INDX]
    gmaps = googlemaps.Client(key=api_key)
    fwd_result = gmaps.directions(o, d, mode="driving", units="imperial", alternatives=True)
    rev_result = gmaps.directions(d, o, mode="driving", units="imperial", alternatives=True)

    routes = [r['legs'][0]['distance']['value'] for r in fwd_result]
    routes.extend([r['legs'][0]['distance']['value'] for r in rev_result])
    routes.sort()

    meters = _convert_and_round(routes[0])
    return meters


def _create_output(out_file, cats, distances):
    data = [['']]

    # Offset column titles by a space.
    cols = []
    for c in cats:
        cols.extend(c)

    data[0].extend(cols)

    for c in cols:
        data.append([c])

    for c in cols:
        for i in range(0, len(cols)):
            r = data[i+1][0]
            if c == r:
                data[i+1].append('X')
            else:
                dist = distances[c][r]
                if dist != 0:
                    data[i+1].append(dist)
                else:
                    data[i+1].append('X')

    with open(out_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def _create_data(pairs, colocations, addresses, api_key):
    data = {}
    for o, d in pairs:
        # Create symmetrical entries for the origin and destination. Use existing distance
        # measurements if they are found.
        if not o in data:
            data[o] = {}
        if not d in data:
            data[d] = {}

        dist = None
        if d in data[o]:
            if data[d][o] != -1:
                print(f'Data already contains a measurement: {o}->{d}')
                dist = data[o][d]
        if o in data[d]:
            if data[d][o] != -1:
                if not dist:
                    print(f'Data already contains a measurement: {o}->{d}')
                    dist = data[d][o]
                elif dist != data[d][o]:
                    print(f'WARNING: Incompatable distance values: {dist}!={data[d][o]}')

        if not dist:
            try:
                dist = _query_dist(o, d, addresses, api_key)
            except ValueError as err:
                print(err)
                sys.exit(-2)

        data[o][d] = dist
        data[d][o] = dist

    for o, d in colocations:
        data[o][d] = 0
        data[d][o] = 0

    return data


def _main():
    parser = argparse.ArgumentParser(description='Generate a table of distances between locations.')
    parser.add_argument('--in_file', type=str, required=False,
                            help='Path to CSV input file containing locations')
    parser.add_argument('--out_file', type=str, required=True,
                            help='Path to output file')
    parser.add_argument('--key', type=str, required=False,
                            help='Google API KEY with Distance Matrix permissions')
    parser.add_argument('--data_out', type=str, required=False,
                            help='Path to file for storing parsed addresses + distances.')
    parser.add_argument('--data_in', type=str, required=False,
                            help='Path to file for storing parsed addresses + distances.')
    args = parser.parse_args()

    if not args.key and not args.data_in:
        print('ERROR: Either an API KEY or data file is required.')
        sys.exit(-3)

    if args.in_file and args.data_in:
        print('WARNING: Ignoring CSV input file because an input data file was specified.')

    if not args.in_file and not args.data_in:
        print('ERROR: Either an input file or data file is required.')
        sys.exit(-3)

    addrs = None
    data = None
    if args.data_in:
        with open(args.data_in, 'rb') as file:
            addrs, data = pickle.load(file)

    if not addrs:
        try:
            addrs = _import_addresses(args.in_file)
        except FileNotFoundError as err:
            print(err)
            sys.exit(-1)

    pairs, colocations = _generate_pairs(addrs)

    if not data:
        data = _create_data(pairs, colocations, addrs, args.key)
    cats = _split_and_sort(addrs)

    if args.data_out:
        try:
            # Don't crash just because the data file couldn't be opened.
            with open(args.data_out, 'wb') as file:
                pickle.dump((addrs, data), file)
        except Exception as err:
            print(err)
            print((addrs, data))

    _create_output(args.out_file, cats, data)
    sys.exit(0)


if __name__ == "__main__":
    _main()
