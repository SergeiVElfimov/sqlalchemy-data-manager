import csv
import json
import logging
from abc import ABC, abstractmethod
from contextlib import suppress

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("sqlalchemy-data-manager")


class BaseDataManager(ABC):
    """Base class for data management."""

    def __init__(self, connecting_settings: dict, mappings: dict, batch_size: int = 1000, encoding: str = "utf8"):
        self.session = next(self.get_session(connecting_settings=connecting_settings))
        self.mapping = mappings
        self.batch_size = batch_size
        self.encoding = encoding

    @classmethod
    def get_session(cls, connecting_settings: dict):
        """Create a session object.

        :param connecting_settings: Connection settings.
        :yield: SQLAlchemy session object.
        """
        Session = sessionmaker(create_engine(**connecting_settings))
        session = Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    @classmethod
    def instance_as_dict(cls, instance):
        """Instance to a dictionary."""
        return {c.key: getattr(instance, c.key) for c in inspect(instance).mapper.column_attrs}

    def bulk_create(self, instances):
        """Mass create instances model."""
        for i in range(0, len(instances), self.batch_size):
            batch = instances[i : i + self.batch_size]
            self.session.add_all(batch)
            self.session.commit()

    @abstractmethod
    def import_data(self): ...

    @abstractmethod
    def export_data(self): ...


class JsonDataManager(BaseDataManager):
    """Import sqlalchemy models from json or export db data to json."""

    def import_data(self) -> None:
        """Import data from json if db table is empty."""
        for model, file_path in self.mapping.items():
            logger.info(f"Populating {model}...")

            if self.session.query(select(model).exists()).scalar():
                logger.info(f"Table {model.__tablename__} not empty, skipping")
                continue
            with open(file_path, encoding=self.encoding) as _file:
                instances = [model(**item) for item in json.load(_file)]
                self.bulk_create(instances=instances)
            logger.info("Done")

    def export_data(self) -> None:
        """Export data to json."""
        for model, file_path in self.mapping.items():
            instances = self.session.query(model).all()
            instances_as_dicts = [self.instance_as_dict(instance) for instance in instances]
            with open(file_path, "w", encoding=self.encoding) as _file:
                json.dump(instances_as_dicts, _file)


class CSVDataManager(BaseDataManager):
    """Import sqlalchemy models from csv or export db data to csv."""

    default_bool_mapping = {"true": True, "false": False}

    def __init__(
        self,
        connecting_settings,
        mappings,
        batch_size=1000,
        encoding="utf8",
        bool_mapping: dict[str, bool] | None = None,
    ):
        super().__init__(connecting_settings, mappings, batch_size, encoding)
        self.bool_mapping = self.default_bool_mapping if bool_mapping is None else bool_mapping
        self.reversed_bool_mapping = {v: k for k, v in self.bool_mapping.items()}

    def import_data(self) -> None:
        """Import data from csv if db table is empty."""
        for model, file_path in self.mapping.items():
            logger.info(f"Populating {model}...")
            if self.session.query(select(model).exists()).scalar():
                logger.info(f"Table {model.__tablename__} not empty, skipping")
                continue
            with open(file_path, encoding=self.encoding, newline="") as _file:
                csv_reader = csv.DictReader(_file, dialect="excel")
                self.bulk_create(
                    instances=[
                        model(**self._pre_process_import_data_row(csv_reader.fieldnames, row)) for row in csv_reader
                    ]
                )
            logger.info("Done")

    def _pre_process_import_data_row(self, fieldnames, row) -> dict:
        """Pre-process before import.

        :param fieldnames: Field names.
        :param row: Row from csv.
        :return: Dictionary  with result.
        """
        forbidden_values = {"", None}
        data = {}
        for header in fieldnames:
            value = row[header]
            if value not in forbidden_values:
                with suppress(ValueError, TypeError):
                    value = int(value)
                bool_value = self.bool_mapping.get(value)
                if isinstance(bool_value, bool):
                    value = bool_value
                data[header] = value
        return data

    def export_data(self):
        """Export data to csv."""
        for model, file_path in self.mapping.items():
            field_names = model.__table__.columns.keys()
            instances = self.session.query(model).all()
            data = []
            for instance in instances:
                converted_data = {}
                for field_name in field_names:
                    value = getattr(instance, field_name)
                    if isinstance(value, bool):
                        bool_value = self.reversed_bool_mapping.get(value)
                        if bool_value is not None:
                            value = bool_value
                    converted_data[field_name] = value
                data.append(converted_data)

            with open(file_path, mode="w", encoding=self.encoding, newline="") as _file:
                csv_writer = csv.DictWriter(_file, fieldnames=field_names, dialect="excel")
                csv_writer.writeheader()
                csv_writer.writerows(data)
