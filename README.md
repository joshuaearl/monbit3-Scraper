## What does it do

It scrapes data about a list bitcoin addresses from an API (https://blockstream.info/api/address/) using asyncio and aiohttp.
Data logged to db: ID, timestamp, balance, fund sent, funds received, transactions sent, transactions received

## What was the inspiration for the project

To log and monitor the top 1000 most active bitcoin addresses to see if there was correlation between large single address balance/transaction movement and global price movement.

## Install

1) Install Python
2) Install the following dependancies, open the terminal & run:
pip install mysql-connector-python
pip install asyncio
pip install aiohttp
3) Install MySQL (Maybe choose a stack (wamp, xampp, lamp etc.) as a web server will be needed if using the web interface)

## Setup

1) Create a MySQL database
2) Open and edit 'makeaddressdb.py', change the config at the top to include your MySQL host, credentials and database name
3) Do the same for the file 'monbit3.py'
4) Add your list of btc addresses to 'address_list.txt'
5) Open the terminal and run: python makeAddressTable.py
Your database now has a table called addresses which has been populated using 'address_list.txt'

## Run

Open the terminal and run: python monbit3.py

## LICENSE

GNU GPLv3