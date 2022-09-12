from typing import Tuple, Any
from tnsquery.db.meta import meta
from sqlalchemy.orm import declarative_base, as_declarative
from sqlalchemy.orm.decl_api import DeclarativeMeta

# # @overload
# # class Base(metaclass=DeclarativeMeta):
# #     __abstract__ = True
# Base = declarative_base()

# @overload
# def declarative_base() -> type[Base]:
#     ...
    
# @overload
# def declarative_base() -> type[Base]:
#     ...
    

# def declarative_base():
#     from sqlalchemy.orm import declarative_base
#     return declarative_base()
    
    
#Base = declarative_base()


from sqlalchemy import Table
@as_declarative(metadata=meta)
class Base:
    
    """
    Base for all models.

    It has some type definitions to
    enhance autocompletion.
    """
    __abstract__ = True
    __tablename__: str
    __table__: Table
    __table_args__: Tuple[Any, ...]
    __table_kwargs__: Any
    
    def __init__(self, **kwargs: Any) -> None:
        ...

# mapper_registry = registry()
# Base = mapper_registry.generate_base()