import json

from sqlalchemy_data_manager import JsonDataManager

from .models import User
from .settings import MODEL_FILE_JSON_MAPPING, USERS_JSON


class TestDataManagers:
    @classmethod
    def check_users(cls, users_with_id: dict[int, User]):
        with open(USERS_JSON, encoding="utf8") as _file:
            for item in json.load(_file):
                user = users_with_id.get(item["id"])
                for field_name, value in item.items():
                    assert getattr(user, field_name) == value

    def test_export_json_manager(self, database_url, users):
        manager = JsonDataManager(connecting_settings={"url": database_url}, mappings=MODEL_FILE_JSON_MAPPING)
        manager.export_data()

        self.check_users(users_with_id={user.id: user for user in users})

    def test_import_json_manager(self, database_url, db_session):
        assert db_session.query(User).count() == 0
        manager = JsonDataManager(connecting_settings={"url": database_url}, mappings=MODEL_FILE_JSON_MAPPING)
        manager.import_data()
        assert db_session.query(User).count() == 3

        self.check_users(users_with_id={user.id: user for user in db_session.query(User).all()})
