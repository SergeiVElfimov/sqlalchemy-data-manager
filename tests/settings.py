import os

from .models import User

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(BASE_PATH, "test_data")

USERS_JSON = os.path.join(TEST_DATA_PATH, "users.json")
USERS_CSV = os.path.join(TEST_DATA_PATH, "users.csv")

MODEL_FILE_JSON_MAPPING = {
    User: USERS_JSON,
}

MODEL_FILE_CSV_MAPPING = {
    User: USERS_JSON,
}
