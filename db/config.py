from sqlalchemy import create_engine

sql_postgres = 'postgresql://postgres:1@localhost/auth'
connect_args = {"check_same_thread": False}
engine = create_engine(sql_postgres)

