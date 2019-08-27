import json
import argparse

from sys import argv
from datetime import datetime, timedelta


def date(date):
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


def merge(wildfire_file, julio_file):
    with open(wildfire_file) as f:
        wildfires = json.load(f)
    
    def mapw(w):
        w['start'] = date(w['start'])
        duration = max(1.0, w['duration'])
        # ensure every wildfire will be present
        w['end'] = w['start'] + timedelta(hours=duration)
        return w

    wildfires = [mapw(w) for w in wildfires]
    wildfires.sort(key=lambda w: w['start'])

    train_file = 'risco-train.json'
    with open(train_file) as f:
        riscos = json.load(f)

    def mapr(r):
        r['ts'] = date(r['ts'])
        r['wildfires'] = []
        return r

    riscos = [mapr(r) for r in riscos]
    riscos.sort(key=lambda r: r['ts'])

    with open(julio_file) as f:
        julio = json.load(f)

    def mapj(j):
        j['ts'] = date(j['ts'])
        j['ots'] = date(j['ots'])
        return j
    
    julio = [mapj(j) for j in julio]
    julio.sort(key=lambda j: j['ts'])

    if len(julio) != len(riscos):
        raise RuntimeError('len(julio) = {} != len(riscos) = {}'
            .format(len(julio), len(riscos)))

    for wildfire in wildfires:
        for risco in riscos:
            if risco['ts'] > wildfire['end']:
                break
            if risco['ts'] >= wildfire['start'] and\
                risco['ts'] <= wildfire['end']:
                risco['wildfires'].append(wildfire)

    merged = [{ **r, 'julio': j['julio'], 'jots': j['ots'] }
        for r, j in zip(riscos, julio)]

    print(json.dumps(merged, default=lambda x: str(x)))


def usage():
    print('Usage: {} wildfires [{{wildfires}}]'.format(argv[0]))


def parseopts():
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--julio', help='Filled julio db',
        required=True)
    parser.add_argument('wildfires', help='Wildfire files', nargs='+')
    return parser.parse_args()


def main():
    if len(argv) == 1:
        usage()
        return
    opts = parseopts()
    for arg in opts.wildfires:
        merge(arg, opts.julio)


if __name__ == '__main__':
    main()
