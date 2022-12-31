# Helium integration server for location tracking

## Introduction

The [helium_mapper](https://github.com/retfie/helium_mapper) is a neat device firmware for GPS location sharing using [LoRaWAN](https://en.wikipedia.org/wiki/LoRa#LoRaWAN). It works great with the public [Mapper](https://mappers.helium.com/) integration server.

This project provides an alternative to the public [Mapper](https://mappers.helium.com/) integration, which you can run on your own premises. Your own data stays on your own equipment.

This server is rather simple. Currently all it does is to record the POSTed location data in a local [SQLite](https://www.sqlite.org) database. Even then, it fulfills my own need to track assets.

## Helium setup

From the Helium [console](https://console.helium.com/flows) do:
  1. Add your [device](https://console.helium.com/devices). Make sure you can see packets coming from the device.
  2. Add a new HTTP [integration](https://console.helium.com/integrations). Leave the default POST method option. Write the URL of your server.
  3. Go to the [Flows](https://console.helium.com/flows) menu and connect your device straight to your new integration. A decoder function is not needed.

With the above steps you should be able to see Helium POST requests to the URL you have provided.

## Server setup

Before you start the HTTP server on your premises, you need to initialize the database:

    $ ./init-db.py

Then you may run the server. It defaults to listening on port 8080:

    $ ./server.py

## Usage

There is no front-end yet to visualize the recorded data. For now you may run SQL queries to obtain location logs. A few examples are provided:

    $ cat queries/dump-path.sql | sqlite3 tracker.db

## Future work

In order to keep data private, I plan to work on the following enhancements:

 - Enable SSL for the HTTP connection. Helium refuses the [Let's Encrypt](https://letsencrypt.org/) certificate for some reason.
 - Encrypt the payload data. Approximate location would still leak through the hotspot metadata, though.
