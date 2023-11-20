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

    def add_point(self, lat, lng, alt, accuracy, satellites, time):
        if satellites < 3:
            return
        pt = gpxpy.gpx.GPXTrackPoint(latitude=lat,
                                     longitude=lng,
                                     elevation=alt,
                                     position_dilution=accuracy,
                                     time=time)
        pt.satellites = satellites
        self.gpx_segment.points.append(pt)

    def add_hotspotpoint(self, lat, lng, name):
        pt = gpxpy.gpx.GPXWaypoint(latitude=lat,
                                   longitude=lng,
                                   symbol=name,
                                   name=name,
                                   description='Helium hotspot')
        self.gpx.waypoints.append(pt)

class points_query:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)

    def get(self, t0, t1):
        cur = self.conn.cursor()
        sel = """SELECT points.lat, points.lng, points.alt, points.accuracy, points.satellites, reports.reported_at_ms
                 FROM (reports
                 INNER JOIN points ON points.report_id = reports.id)
                 WHERE reports.reported_at_ms >= ? AND reports.reported_at_ms < ?
                 ORDER BY reports.reported_at_ms ASC;"""

        cur.execute(sel, (int(t0),int(t1)))
        result = cur.fetchall()
        return result

    def get_hotspots(self, t0, t1):
        cur = self.conn.cursor()
        sel = """SELECT hotspot_names.lat, hotspot_names.lng, hotspot_names.name
                 FROM ((reports
                 INNER JOIN hotspot_connections ON hotspot_connections.report_id = reports.id)
                 INNER JOIN hotspot_names ON hotspot_connections.name_id = hotspot_names.id)
                 WHERE reports.reported_at_ms >= ? AND reports.reported_at_ms < ?;"""

        cur.execute(sel, (int(t0),int(t1)))
        result = cur.fetchall()
        return result


def isodate2ms(datestr):
    return datetime.datetime.fromisoformat(datestr).timestamp() * 1000

def ms2time(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.UTC)

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
    parser.add_argument('-n', '--no-hotspots',
        action='store_true',
        help = 'Do not output observed hotspots as WayPoints.')
    args = parser.parse_args()

    t0 = isodate2ms(args.from_date)
    t1 = isodate2ms(args.before_date)

    out = gpx_writer()
    db = points_query(args.database)
    points = db.get(t0, t1)
    for p in points:
        t = ms2time(p[5])
        out.add_point(p[0], p[1], p[2], p[3], p[4], t)
    if not args.no_hotspots:
        waypoints = db.get_hotspots(t0, t1)
        for wp in waypoints:
            out.add_hotspotpoint(wp[0], wp[1], wp[2])
    out.save(args.output)
