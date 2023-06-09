
<!-- ABOUT THE PROJECT -->
## About The Project

This is a simple combination of an OLTP database holding transactions
data and an OLAP database for analytical processing of the transaction 
data.
The transactions data is synchronized from the OLTP to the OLAP database
and a balance table derived from the transaction data is generated. 
The balance data is updated on every sychronization cycle.

It consists for 4 separate Docker containers:
* the OLTP database (MySQL)
* the OLAP database (MySQL)
* a service which inserts transactions into the OLTP database
* a service which synchronizes transactions between OLTP and OLAP database and updates the balance table
 
## Usage
Start the OLTP database container and the service which inserts new transactions:

    docker-compose up --build mysql-oltp row_inserter_service

This will create a fresh MySQL database with an empty transactions 
table. The data is not stored in a persistent volume and is lost 
if the MySQL container is deleted.

The service which inserts new transactions is started automatically
once the MySQL database is ready and accepts connections. It will 
insert a rows with random transaction data in an endless loop and 
wait for a random period of up to 3 seconds between inserts.

Once the MySQL database is ready and the transaction inserter 
service has started (this takes about 30 to 60 seconds), the OLAP 
synchronization service can be started:

    docker-compose up --build mysql-olap database_sync_service

The database sync service initially fetches all existing transactions 
in the OLTP database and copies them to the OLAP database in batches
of 1000 rows. Once this process is complete, it will check the OLTP
database for new rows once per minute, synchronize them to the OLAP
database and updates the balance table accordingly.