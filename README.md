# SQLAlchemy data manager

Import SQLAlchemy models from json/csv or export db data to json/csv.

## Examples

```python
# models.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, unique=True, primary_key=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)


# settings.py

import os

from .models import User

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(BASE_PATH, "test_data")

USERS_JSON = os.path.join(TEST_DATA_PATH, "users.json")
USERS_CSV = os.path.join(TEST_DATA_PATH, "users.csv")

MODEL_FILE_JSON_MAPPING = {
    User: USERS_JSON,
}

MODEL_FILE_CSV_MAPPING = {User: USERS_CSV}

# Run
from sqlalchemy_data_manager import CSVDataManager, JsonDataManager

json_manager = JsonDataManager()
json_manager.import_data() # Import data from json
json_manager.export_data() # Export data to json

csv_manager = CSVDataManager()
csv_manager.import_data() # Import data from csv
csv_manager.export_data() # Export data to csv
```

## Required

- python >=3.11, <4.0
- SQLAlchemy >=1.4.36, <2.1.0

## Installation
```pip install sqlalchemy-data-manager```

## Contributing

Before contributing please read our [contributing guidelines](CONTRIBUTING.md).
