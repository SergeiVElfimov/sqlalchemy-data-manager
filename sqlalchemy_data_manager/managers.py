import json
import logging
from abc import ABC, abstractmethod

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("sqlalchemy-data-manager")


class BaseDataManager(ABC):
    """Base class for data management."""

    def __init__(self, connecting_settings: dict, mappings: dict, batch_size: int = 1000):
        self.session = next(self.get_session(connecting_settings=connecting_settings))
        self.mapping = mappings
        self.batch_size = batch_size

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
            with open(file_path, encoding="utf8") as _file:
                instances = [model(**item) for item in json.load(_file)]
                for i in range(0, len(instances), self.batch_size):
                    batch = instances[i : i + self.batch_size]
                    self.session.add_all(batch)
                    self.session.commit()
            logger.info("Done")

    def export_data(self) -> None:
        """Export data to json."""
        for model, file_path in self.mapping.items():
            instances = self.session.query(model).all()
            instances_as_dicts = [self.instance_as_dict(instance) for instance in instances]
            with open(file_path, "w", encoding="utf8") as _file:
                json.dump(instances_as_dicts, _file)


class CSVDataManager(BaseDataManager):
    """Import sqlalchemy models from csv or export db data to csv."""

    bool_mapping = {"true": True, "false": False}

    def import_data(self) -> None:
        """Import data from csv."""
