import os

DB_CONFIG = {
    "USER": "postgres",
    "DBNAME": "restaurent-managemet-db",
    "PASSWORD": "postgres",
    "PORT": 5432,
    "HOST": "localhost"
}
DBURL = "postgres://"+DB_CONFIG["USER"]+":"+DB_CONFIG["PASSWORD"]+"@"+DB_CONFIG["HOST"]+":"+str(DB_CONFIG["PORT"])+"/"+DB_CONFIG["DBNAME"]
MIGRATION_LOCATION = "./local_migrations"

DEFAULT_TIMEZONE = "America/Chicago"

DEPLOYMENT_DETAILS = {
    "HOST": "localhost",
    "PORT": 8000
}

REPORT_DIR = "./reports"
REPORT_LINK = "/reports"

if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

BASEURL = "http://localhost:8000"