import aiohttp
import asyncio
import json
import mysql.connector
from mysql.connector import errorcode
import random
import sys
import time


data = []
loopdelay = 300

# MySQL setup
basedir = "./scrape/"
config = {
  'user': 'databaseUsername',
  'password': 'databasePassword',
  'host': '127.0.0.1',
  'database': 'databaseName',
  'raise_on_warnings': True
}
con =  mysql.connector.connect(**config)
cursor = con.cursor()


async def download_file(url, timeout=16):
    print(f'Started downloading {url}')
    async with aiohttp.ClientSession() as session:
        delay = random.uniform(0,10)
        await asyncio.sleep(delay)
        content = None
        while content is None:
            try:
                async with session.get(url, timeout=timeout) as resp:
                    content = await resp.read()
                    return content
            except asyncio.TimeoutError as e:
                print(f"FAIL! Timed out!")
                print(f"Error: {e}\n")
                pass
            except aiohttp.client_exceptions.ClientConnectorError as e:
                print(f"FAIL! Couldn't connect")
                print(f"Error: {e}\n")
                pass
            except aiohttp.client_exceptions.ClientResponseError as e:
                print(f"FAIL! Client response error")
                print(f"Error: {e}\n")
            except Exception as e:
                print(f"Uh oh. Something fucked up: {e}\n")
                pass


async def scrape_task(n, url):
    content = await download_file(url)
    if content != None:
        await write_file(n, content)
    else:
        print("FAIL! Scrape task can't write file, content is empty!")
        pass


async def write_file(n, content):
    content = content.decode("utf-8")
    content = content[1:]
    content = '{"id":"%s",%s' % (n, content)
    data.append(content)
    print(f'Appended data with address ID {n} to list')


def address_lookup():
    try:
        query = ("SELECT * FROM addresses")
        cursor.execute(query)
        fetched = cursor.fetchall()
        n = cursor.rowcount
        print("Total number of addresses: ", n)
        i = 0
        a = []
        for row in fetched:
            id = row[0]
            address = row[1]
            a.append([id])
            a[i].append(address)
            i += 1
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (con.is_connected()):
            cursor.close()
            con.close()
            print("MySQL connection is closed")
    return a


def check_table(tablename):
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        return True
        
    return False


def update_db():
    con =  mysql.connector.connect(**config)
    cursor = con.cursor()
    timestamp = time.time()

    with open('data.json') as json_file:
        data = json.load(json_file)
        
        for i in range(0,len(data)):
            id = data[i]['id']
            address = data[i]['address']
            transactions_rx = data[i]['chain_stats']['funded_txo_count']
            funds_rx = data[i]['chain_stats']['funded_txo_sum']
            transactions_tx = data[i]['chain_stats']['spent_txo_count']
            funds_tx = data[i]['chain_stats']['spent_txo_sum']
            tx_count = data[i]['chain_stats']['tx_count']
            mempool_f_count = data[i]['mempool_stats']['funded_txo_count']
            mempool_f_sum = data[i]['mempool_stats']['funded_txo_sum']
            mempool_s_count = data[i]['mempool_stats']['spent_txo_count']
            mempool_s_sum = data[i]['mempool_stats']['spent_txo_sum']
            mempool_tx = data[i]['mempool_stats']['tx_count']       
            balance = funds_rx - funds_tx                       
            try:
                if check_table("data") == False: # No table? Make one
                    newtable = ("CREATE TABLE IF NOT EXISTS data ("
                    "  `id` INT(5) NOT NULL,"
                    "  `timestamp` INT(11) NOT NULL,"
                    "  `transactions_rx` BIGINT(16) NOT NULL,"
                    "  `funds_rx` BIGINT(16) NOT NULL,"
                    "  `transactions_tx` BIGINT(16) NOT NULL,"
                    "  `funds_tx` BIGINT(16) NOT NULL,"
                    "  `tx_count` BIGINT(16) NOT NULL,"
                    "  `balance` BIGINT(16) NOT NULL,"
                    "  PRIMARY KEY (`id`, `timestamp`)"
                    ") ENGINE=InnoDB")
                    cursor.execute(newtable)
                    print("Creating new table")
                    con.commit()
                # Insert data into table
                query = ("INSERT INTO data (id, timestamp, transactions_rx, funds_rx, transactions_tx, funds_tx, tx_count, balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
                val = (id, timestamp, transactions_rx, funds_rx, transactions_tx, funds_tx, tx_count, balance)
                cursor.execute(query,val)
                con.commit()
                print(address + " - updated successfully")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("Trying to create table that exists already")
                elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Incorrect username or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                elif err.errno == 1264:
                    print(err.msg)
                    print("ID: %s" % id)
                    print("Address: %s" % address)
                    print("Transactions: %s" % transactions)
                elif err.errno == 1265:
                    print(err.msg)
                    print("ID: %s" % id)
                    print("Address: %s" % address)
                    print("Transactions: %s" % transactions)
                else:
                    print(err.errno)  
                    print(err.msg)  
            i += 1        
    cursor.close()
    con.close()
    return


async def main():
    a = address_lookup()    
    tasks = []
    for i in range(len(a)):
        n =  a[i][0]
        url =  "https://blockstream.info/api/address/" + a[i][1]
        tasks.append(scrape_task(n, url))
    await asyncio.wait(tasks)


if __name__ == '__main__':
    while True:
        data.clear()
        t = time.perf_counter()
        asyncio.run(main())
        t2 = time.perf_counter() - t
        print(f'Download time taken: {t2:0.2f} seconds')
        
        parsed_data = [json.loads(s) for s in data]
        with open('data.json', 'w', encoding='utf-8') as fs:
            json.dump(parsed_data, fs, ensure_ascii=False, indent=4)
        print("File write successful")
        
        update_db()
        t3 = time.perf_counter() - t
        print(f'Total time taken: {t3:0.2f} seconds')
        sleeptime = loopdelay - t3
        sleeptime = int(sleeptime)
        print(f'Sleep time: {sleeptime}')     
        for i in range(sleeptime):
            sys.stdout.write(str(sleeptime - i) + ' ')
            sys.stdout.flush()
            time.sleep(1)