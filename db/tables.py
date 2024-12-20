import sqlalchemy as db

engine = db.create_engine("sqlite:///test.db")

con = engine.connect()
metadata = db.MetaData()

tasks = db.Table('tasks', metadata,
                 db.Column('id', db.Integer, primary_key=True),
                 db.Column("tgid", db.Integer, db.ForeignKey('users.tgid')),
                 db.Column("title", db.String),
                 db.Column("description", db.String),
                 db.Column("date_started", db.DateTime),
                 db.Column("date_finished", db.DateTime),
                 db.Column("status", db.Boolean, default=False)
                 )

users = db.Table("users", metadata,
                 db.Column('tgid', db.Integer, primary_key=True),
                 db.Column("name", db.String),
                 db.Column("surname", db.String),
                 db.Column('age', db.Integer),
                 db.Column('email', db.String))



metadata.create_all(engine)
