# ss_weather

List input variables

List output variables

## Strategy Database Transactions

### Installation

Install an SQL database. If you aren't sure which way to do this, I can recommend using XAMPP on all Platforms.

Then prepare your python installation by installing the pip packages saved in `requirements.txt`:

```py
pip install -r requirements.txt
```

### Creating a Database

Create a new database for the strategy team in XAMPP or whatever you are using. Here is an example for how to create a new user and a database with the same name.

!['Example Config'](docs/dbconfig.png)

Make sure to copy file `db/env.example` and rename the file to `db/.env` so that your password is not in version control. Then exchange the dummy values in `db/.env` to the values you previously chose

### Adding entries

The database interactions are abstracted behind the DBService class.

You can create new entries to the database by executing the following code:

```py
# current file: any in root level directory
from db.db_service import DbService
from db.models import *

# your API response in JSON / python dict
api_data: dict = {"gk": 83.3, "gh_max": 110.63228810314124, "tt": 26.5, "ff": 11}

forecast: Forecast = Forecast(
    api_data["gk"], api_data["gh_max"], api_data["tt"], api_data["ff"]
)

db: DbService = DbService()
db.add_entry(forecast)
```

### Reading entries

The DBService class provides two methods for fetching data in python. `

```py
from db.db_service import DbService
from db.models import *

db: DbService = DbService()

# get latest 100 entries
db.query(Forecast, 100)

# get latest forecast
db.latest(Forecast)
```

### Clearing a table

This code snippet allows you to clear all the values inside of a table without deleting the table itself.

```py
from db.db_service import DbService
from db.models import *

db: DbService = DbService()

# clear all forecasts
db.clear_table(Forecast)
```


### Chaging ORM models

To interact with the database, we use a library called SQLAlchemy and their object relational models. The models are saved in `/db/models.py`. There you specify what your table looks like (columns, data type). Here is find the nitty-gritty details on the specification: [https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models](https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models)

For most use-cases you can just directly copy-paste a line and then change the name and type of an entry. There isn't much more to it. Or if you want another table, just copy paste a class and rename the variables