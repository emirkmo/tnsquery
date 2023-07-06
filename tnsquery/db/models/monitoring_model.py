from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String, Text

from tnsquery.db.base import Base


# class MonitoringModel(Base):
#     """Model for tns log monitoring purposes."""

#     __tablename__ = "tns_log"

#     id = Column(Integer(), primary_key=True, autoincrement=True)
#     query = Column(Text())  # noqa: WPS432
#     response = Column(Text())
#     code = Column(Integer())


class TransientLogModel(Base):
    """Model for transient log monitoring purposes."""

    __tablename__ = "tnsquery_log"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(100))
    query = Column(Text())  # noqa: WPS432
    response = Column(Text())
    code = Column(Integer())
