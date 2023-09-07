# current file: any in root level directory
from db.db_service import DbService
from db.models import *

# your API response in JSON / python dict
api_data: dict = {"id": 1, "gk": 83.3, "gh_max": 110.63228810314124, "tt": 26.5, "ff": 11}

forecast: Forecast = Forecast(
    api_data["gk"], api_data["gh_max"], api_data["tt"], api_data["ff"]
)

db: DbService = DbService()
db.add_entry(forecast)

    # id: Mapped[int] = mapped_column(primary_key=True) # numbers
    # gk: Mapped[float] = mapped_column(Float())
    # gh_max: Mapped[float] = mapped_column(Float())
    # tt: Mapped[float] = mapped_column(Float())
    # ff: Mapped[float] = mapped_column(Float())