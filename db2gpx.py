#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
#
# Make a query and export to a GPX track file.
#
# sudo apt install python3-gpxpy

import sys
import sqlite3
import gpxpy
import argparse
import datetime

class gpx_writer:
    def __init__(self):
        self.gpx = gpxpy.gpx.GPX()
        # Create first track in our GPX:
        self.gpx_track = gpxpy.gpx.GPXTrack()
        self.gpx.tracks.append(self.gpx_track)

        # Create first segment in our GPX track:
        self.gpx_segment = gpxpy.gpx.GPXTrackSegment()
        self.gpx_track.segments.append(self.gpx_segment)

    def save(self, output_filename):
        with open(output_filename, 'w') as o:
            o.write(self.gpx.to_xml())

    def add_point(self, lat, lng, alt, time):
        pt = gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=lng,
                                     elevation=alt, time=time)
        self.gpx_segment.points.append(pt)

class points_query:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)

    def get(self, t0, t1):
        cur = self.conn.cursor()
        sel = """SELECT points.lat, points.lng, points.alt, reports.reported_at_ms
                 FROM (reports
                 INNER JOIN points ON points.report_id = reports.id)
                 WHERE reports.reported_at_ms >= ? AND reports.reported_at_ms < ?
                 ORDER BY reports.reported_at_ms ASC;"""

        cur.execute(sel, (int(t0),int(t1)))
        result = cur.fetchall()
        return result


def isodate2ms(datestr):
    return datetime.datetime.fromisoformat(datestr).timestamp() * 1000

def ms2time(ms):
    return datetime.datetime.utcfromtimestamp(ms / 1000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a GPX track.')
    parser.add_argument('-i', '--database', required=True,
        help = 'Input SQLite3 database to query.')
    parser.add_argument('-f', '--from-date', required=True,
        help = 'Record from given start date (e.g. 2023-03-18)')
    parser.add_argument('-b', '--before-date', required=True,
        help = 'Record before given date (e.g. 2023-03-19)')
    parser.add_argument('-o', '--output', required=True,
        help = 'Filename where to output the GPX track.')
    args = parser.parse_args()

    t0 = isodate2ms(args.from_date)
    t1 = isodate2ms(args.before_date)

    out = gpx_writer()
    db = points_query(args.database)
    points = db.get(t0, t1)
    for p in points:
        t = ms2time(p[3])
        out.add_point(p[0], p[1], p[2], t)
    out.save(args.output)
