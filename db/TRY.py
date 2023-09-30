# current file: any in root level directory
from db_service import DbService
from models import *

# your API response in JSON / python dict
api_data: dict = {"gk": 83.3, "gh_max": 110.63228810314124, "tt": 26.5, "ff": 11}

forecast: Forecast = Forecast(
    api_data["gk"], api_data["gh_max"], api_data["tt"], api_data["ff"]
)

db: DbService = DbService()
db.add_entry(forecast)