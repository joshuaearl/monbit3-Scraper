import mysql.connector
from mysql.connector import errorcode

# MySQL setup
config = {
  'user': 'databaseUsername',
  'password': 'databasePassword',
  'host': '127.0.0.1',
  'database': 'databaseName',
  'raise_on_warnings': True
}

con =  mysql.connector.connect(**config)
cursor = con.cursor()

def check_table(tablename):
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        return True
        
    return False

def main():
    try:
        if check_table("addresses") == False: # No table? Make one
            newtable = ("CREATE TABLE IF NOT EXISTS data ("
            "  `id` INT(5) NOT NULL,"
            "  `address` VARCHAR(64) NOT NULL,"
            "  `transactions_rx` BIGINT(16) NOT NULL,"
            "  PRIMARY KEY (`id`)"
            ") ENGINE=InnoDB")
            cursor.execute(newtable)
            print("Creating new table")
            con.commit()
        for n, address in enumerate(open('address_list.txt').read().split('\n')):
            try:
                # Insert data into table
                query = ("INSERT IGNORE INTO addresses (id, address) VALUES (%s, %s)")
                val = (n, address)
                cursor.execute(query,val)
                con.commit()
                print(address + " - updated successfully")
            except mysql.connector.Error as err:
                    print(err.errno)
                    print(err.msg)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Trying to create table that exists already")
        elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Incorrect username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err.errno)  
            print(err.msg)      
    cursor.close()
    con.close()
        
if __name__ == "__main__":
    main()