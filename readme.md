# Pyspark Watcher

## Introduction
To test and implement a spark pipeline this system uses docker to spin up an instance of apache spark, postgres and a directory watcher through watchdog (this would emulate a trigger of an azure blob storage trigger). 
The database management is handled through SQL alchemy which will generate the target schemas through ORM. New files are processed when added to the '**imports**' directory in the root of the project to simulate the handover of a flat file from another service, a cron job that hits an api to download a csv file for example.

We make the assumption that the files are saved with the name of the target table they need to be ingested into too. 
My approach to the unknowns would be to parse the csv general schema, understand data types, and create the data in a staging area dynamically for review.
Although not implemented at the end of the new file event trigger a zip and back up service could be created, but in this instance it just deletes the file for simplicity. 

### Code layout

#### Core
* **config.py** - Contains all settings for env variables, validated with pydantic
* **db.py** - singleton patterns for database engines and sessions sync / async
* **spark.py** - singleton pattern for a spark session that can be used project wide, also drivers for the JDCB connectors are loaded into jars here. 
* **drivers** - jar jdcb drivers for spark

#### Models
This contains the ORM models of the database, using the Base declaration found in core/db to init the general schema and relationships. 
* **transactions**
* **users**

#### Pipeline
Contains all files that are running the spark jobs and general processes.

#### Services
* **directory_watcher.py** - entry point and logic for the watchdog module.
* **schema_init.py** - design pattern for inserting dimensions and creating scaffolding for a database.
___

## Setup
The project requires pipenv as means to manage dependencies. 
A folder for **logs** and **imports** / **exports** is needed as well. 
Not included in the push as it would be bad dev practice as it could contain secrets!.

You will need to connect to the database through a explorer of your choice, I like DBeaver. The details are in the ENV variables below are the same as those in the docker-compose file. 
A note that the database will be on localhost, the name below is the docker friendly name.

$ `
git clone git@github.com:Botman-Hotman/PysparkWatcher.git &&  
cd PysparkWatcher && 
mkdir logs imports exports &&  
touch .env
`

# Environment Vars
Add the following settings into the .env file created in the command above.
The following vars are designed to work for the docker container, adjust if you wish to use a local instance of postgres/spark as these are hunting for the docker network name and not the usual localhost/ip.
If **dev** is true it will drop and recreate all the tables within the database on every startup.

*  dev = True
*  debug_logs = False
*  db_string = 'postgresql//dev-user:password@postgres:5432/dev_db'
*  db_string_async = "postgresql+asyncpg://dev-user:password@postgres:5432/dev_db"
*  echo_sql = False
*  init_db = True
*  staging_schema = 'staging'
*  dw_schema = 'datawarehouse'
*  SPARK_NO_DAEMONIZE=true
*  app_name='PysparkWatcher'
*  master='spark://spark-master:7077'
*  spark_log_level = 'WARN'
*  db_url = "postgres:5432/dev_db"
*  db_name = 'dev_db'
*  db_user = 'dev-user'
*  db_password = 'password'
*  jdbc_database = "jdbc:postgresql://"
*  driver_type= 'org.postgresql.Driver'


# Start Up
The command below will collect, install start all the services and dependencies needed. For the first run this will take sometime to download all the services and dependencies, up to 10 minutes from testing. I did not include methods to deploy this to the cloud, however pushing docker containers to a cloud platform of your choice is well documented.

$ `docker-compose up`

If you wish to change the resources assigned to the spark server, see the docker-compose.yaml and adjusted the following values on the worker and master
![Alt text](img/spark_settings.png?raw=true "spark settings")


if init_db is True you should also see the following tables have been created in the database:
![Alt text](img/tables.png?raw=true "database tables")



### check that the containers are up
$ `docker ps`

### check the logs of the start up, you should see the image below 

$ `docker-compose logs`


![Alt text](img/watcher.png?raw=true "expected start")

We make the assumption that a job will push the flat files into the import folder. 
The below command simulates a new file entering the directory.
The container is named **'app'** as defined in the docker-compose file.

The target files are in example_data. There are two directories to test the pipeline:

* **insert**: This contains fresh data to push into the database
* **updates**: This contains 200 changes to the users.csv and 100 changes to transaction.csv to simulate CDC. 

Run the commands in order to do the initial insert, naturally we need users to be inserted first to satisfy any foreign key constraints in the transaction table

$ `docker cp example_data/inserts/users.csv app:app/imports`

![Alt text](img/new_file.png?raw=true "expected start")


On the new data entering into the pipeline, the usual duplication and null value checks are performed. A hash of the email address is taken and converted into a UUID as the user_id as a more reliable and anonymous key to pass between systems. 
The scripts will check if there are any existing records in the database, naturally on the first run there will not so it will create the relevant dimensions and insert the data. 

Once the command at the top is complete, check the database and you will see the tables populated. 

$ `docker cp example_data/updates/users.csv app:app/imports`


The commands above simulate new data coming into the database, we fetch the existing data from the database, merge on the email address as its a natural business key for users and will be the only thing that should not change. 
We then perform basic comparison operations to see what data has changed and what needs to be updated, inserted and deactivated as the current dimension. 
The file located in the updates folder of the example data directory should produce the following output:
![Alt text](img/example_updates.png?raw=true "expected start")

In order to check the general job status you can go to the following link:
[localhost:8080]()


After the jobs are completed, the files are deleted from imports for housekeeping.

# Challenges Faced
The biggest issue I found with this was getting all the micro services to talk to each other with permissions and shared volumes. 
The JDBC connector dosnt provide a native upsert function that postgres has through the SQL alchemy code.

I dont use the native pyspark api for ETL often, 
I much prefer to use native SQL and if needed inject information through formated strings via python, once I learnt the general design patterns of the dataframe API it became easier but this vs SQL queries in a platform like bigquery is not something I would personally choose for like this. 

Also using the correct base image version of Java is important to align with the target version of spark, thank god for LLM's to parse error messages.