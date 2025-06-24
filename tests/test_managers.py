import csv
import json
from contextlib import suppress

from sqlalchemy_data_manager import CSVDataManager, JsonDataManager

from .models import User
from .settings import MODEL_FILE_CSV_MAPPING, MODEL_FILE_JSON_MAPPING, USERS_CSV, USERS_JSON


class TestDataManagers:
    @classmethod
    def check_users_from_json(cls, users_with_id: dict[int, User]):
        with open(USERS_JSON, encoding="utf8") as _file:
            for item in json.load(_file):
                user = users_with_id.get(item["id"])
                for field_name, value in item.items():
                    assert getattr(user, field_name) == value

    def test_export_json_manager(self, database_url, users):
        manager = JsonDataManager(connecting_settings={"url": database_url}, mappings=MODEL_FILE_JSON_MAPPING)
        manager.export_data()

        self.check_users_from_json(users_with_id={user.id: user for user in users})

    def test_import_json_manager(self, database_url, db_session):
        assert db_session.query(User).count() == 0
        manager = JsonDataManager(connecting_settings={"url": database_url}, mappings=MODEL_FILE_JSON_MAPPING)
        manager.import_data()
        assert db_session.query(User).count() == 3

        self.check_users_from_json(users_with_id={user.id: user for user in db_session.query(User).all()})

    def check_users_from_csv(self, users_with_id: dict[int, User]):
        with open(USERS_CSV, encoding="utf8", newline="") as _file:
            csv_reader = csv.DictReader(_file, dialect="excel")
            for row in csv_reader:
                user = users_with_id[int(row["id"])]
                for field_name, value in row.items():
                    with suppress(ValueError, TypeError):
                        value = int(value)
                    assert getattr(user, field_name) == value

    def test_export_csv_manager(self, database_url, users):
        manager = CSVDataManager(connecting_settings={"url": database_url}, mappings=MODEL_FILE_CSV_MAPPING)
        manager.export_data()
        self.check_users_from_csv(users_with_id={user.id: user for user in users})

    def test_import_csv_manager(self, database_url, db_session):
        assert db_session.query(User).count() == 0
        manager = CSVDataManager(connecting_settings={"url": database_url}, mappings=MODEL_FILE_CSV_MAPPING)
        manager.import_data()
        assert db_session.query(User).count() == 3

        self.check_users_from_json(users_with_id={user.id: user for user in db_session.query(User).all()})
