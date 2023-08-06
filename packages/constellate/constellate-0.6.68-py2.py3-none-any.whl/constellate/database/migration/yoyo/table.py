from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Tables MUST be subclassed as follow to be extended:
# class _YoyoLogR(YoyoLogR):
#     __tablename__ = YoyoLogR.__tablename__


class YoyoLogR(Base):

    __abstract__ = True
    __tablename__ = "_yoyo_log"
    id = Column(String, primary_key=True)
    migration_id = Column(String)


class YoyoMigrationR(Base):
    __abstract__ = True
    __tablename__ = "_yoyo_migration"
    migration_hash = Column(String, primary_key=True)
    migration_id = Column(String)


class YoyoVersionR(Base):
    __abstract__ = True
    __tablename__ = "_yoyo_version"
    version = Column(Integer, primary_key=True)
