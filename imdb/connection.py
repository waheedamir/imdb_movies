from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import session
from sqlalchemy import MetaData

credentials = {
    'user': 'waheed',
    'password': 'any problem',
    'host': 'localhost',
    'port': '3306',
    'database': 'imdb'
}
engine = create_engine(
    f"mysql+pymysql://{credentials['user']}:{credentials['password']}@{credentials['host']}:{credentials['port']}/{credentials['database']}",
                                       encoding='utf-8', pool_size=20, pool_recycle=60)

db_session = scoped_session(session.sessionmaker(bind=engine, expire_on_commit=False))
META = MetaData(engine)

