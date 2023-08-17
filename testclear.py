from db.db_service import DbService
from db.models import *

db: DbService = DbService()

# clear all forecasts
db.clear_table(Forecast)
