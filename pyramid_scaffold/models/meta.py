from sqlalchemy.schema import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy import create_engine

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: https://alembic.sqlalchemy.org/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
engine = create_engine('mysql+mysqlconnector://root:@localhost/shopify')
DBSession = scoped_session(sessionmaker(bind=engine))
Base = declarative_base(metadata=metadata)
