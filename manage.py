import sys, subprocess, uvicorn
from tortoise import run_async

from src.config import MIGRATION_LOCATION, DEPLOYMENT_DETAILS
from scripts import upload_csvs

if __name__ == "__main__":
    if sys.argv == ["manage.py", "init", "migration"]:
        subprocess.run(["aerich", "init", "-t", "src.main.db_config", "--location", MIGRATION_LOCATION])
        subprocess.run(["aerich", "init-db"])
    
    if sys.argv == ["manage.py", "migrate"]:
        print("Please give migration a name.")
        migration_name = input()
        commands = [["aerich", "migrate", "--name", migration_name], ["aerich", "upgrade"]]
        for cmd in commands:
            subprocess.run(cmd)

    if sys.argv == ["manage.py", "runserver"]:
        uvicorn.run("src.main:app", port = DEPLOYMENT_DETAILS["PORT"], host=DEPLOYMENT_DETAILS["HOST"], lifespan="on")

    if sys.argv == ["manage.py", "upload"]:
        run_async(upload_csvs.upload())