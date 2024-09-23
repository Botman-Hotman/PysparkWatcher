# Pyspark Watcher

## Introduction
To test and implement a spark pipeline this system uses docker to spin up an instance of apache spark, postgres and a directory watcher through watchdog. 
The database management is handled through SQL alchemy which will generate the target schemas through ORM. New files are processed when added to the '**imports**' directory in the root of the project to simulate the handover of a flat file from another service. 

The docker-compose file creates the following spark services:
* Master 
* Worker
* History




## Setup
The project requires pipenv as means to manage dependencies. 
A folder for **logs** and **imports** / **exports** is needed as well. 
Not included in the push as it would be bad dev practice as it could contain secrets!.

$ `
git clone git@github.com:Botman-Hotman/PysparkWatcher.git &&  
cd DataProcessor && 
mkdir logs imports exports &&  
touch .env
`

# Environment Vars
Add the following settings into the .env file created in the command above.
The following vars are designed to work for the docker container, adjust if you wish to use a local instance of postgres.
If **dev** is true it will drop and recreate all the tables within the database on every startup.

*  dev = True
*  debug_logs = False
*  db_string = 'postgresql//dev-user:password@postgres:5432/dev_db'
*  db_string_async = "postgresql+asyncpg://dev-user:password@postgres:5432/dev_db"
*  echo_sql = False
*  init_db = True
*  staging_schema = 'staging'
*  dw_schema = 'datawarehouse'
* SPARK_NO_DAEMONIZE=true
* app_name='PysparkWatcher'
* master='spark://spark-master:7077'


# Start Up
Spin up a docker instance of postgres and the directory watcher. 
There is an option to use volumes to persist the data. Check the commented lines within the docker-compose.yamml. 
If this services is to interact with other docker containers they must all use the network created there too.

$ `docker-compose up -d`

### check that the images are up
$ `docker ps`

We make the assumption that a job will push the flat file into the import folder. The below command simulates a new file entering the directory.
Put the target file in the root of the project and run below. The container is named **'app'** as defined in the docker-compose file.

$ `docker cp  example_data/* app:app/imports`