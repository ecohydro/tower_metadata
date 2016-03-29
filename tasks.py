"""Celery application code."""
import os
if os.path.exists('.env'):
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from config import config
from celery import Celery
import datetime
from app.models import Metadata, DropboxFiles
from mongoengine import connect

# Make the database connection:
# Set the config settings to whatever the app is using.
this_config = config[os.getenv('FLASK_CONFIG') or 'default']
# Make the database connection:
connect(host=this_config().mongo_url())
find_files = DropboxFiles.find_files

celery = Celery('mpala_tower')
celery.config_from_object("celery_settings")


def doy(date=None):
    """Return a DOY from a datetime object."""
    if not date:
        date = datetime.datetime.now()
    this_ordinal = date.toordinal()
    year_ordinal = datetime.datetime(date.year, 1, 1).toordinal()
    return this_ordinal - year_ordinal + 1


@celery.task
def add(x, y):
    """Add two numbers."""
    return x + y


@celery.task(bind=True)
def create_metadata_task(self, year, doy):
    """Celery task to create metadata."""
    # Import the ORM for the metadata
    self.update_state(state='PROGESS')
    Metadata(
        year=year,
        doy=doy,
        files=find_files(year=year, doy=doy)
    ).generate_metadata()
