# Restaurant-Time-Management

This project contains APIs for creating reports of total uptime and downtime of some store or restaurants in lastweek based on the given data. This project uses FastAPI to provide APIs and Tortoise-ORM to interact with database wich is postgres in this case.

## WorkFlow

`/trigger_report` API triggers the report creation and returns a `report_id` which can be used to check the status of the report whether it has been created or not using `/get_report`. The report creation occurs in background and uses `multiprocessing` to speed things up as it is a CPU bound task.

# Commands

Following commands can be used for the different purposes:

### Migration

For migrating first time, use:

```
python manage.py init migration
```

For later migrations, use:

```
python manage.py migrate
```

### Run Server

To Run Server use:

```
python manage.py runserver
```

### Populate

To populate data, give the csv files to scripts/upload_csvs.py and use:

```
python manage.py upload
```
