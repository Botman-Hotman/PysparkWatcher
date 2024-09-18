# Pyspark Watcher

## Introduction
To test and implement a spark pipeline this system uses docker to spin up an instance of apache spark, postgres and a directory watcher through watchdog. 
The database management is handled through SQL alchemy which will generate the target schemas through ORM principles. New files are processed when added to the imports directory in the root of the project to simulate the handover of a flat file from another service. 

The docker-compose file creates three spark services:
* Master 
* Worker
* History

The master and worker services have access to the book data and spark apps directories that we map into the containers using the volumes setting.
The history server uses only the spark-logs volume that is defined at the bottom of the docker compose file. 
The directory for the spark logs is the same that is defined in the spark default configuration file.