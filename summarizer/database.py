import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, DateTime, ARRAY

from env import DATABASE_URL

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    echo=True,
)

BaseModel = declarative_base()


class Paper(BaseModel):
    __tablename__ = "papers"

    id = Column(String, primary_key=True)
    # if paper is published in arXiv, the id is the arXiv id

    title = Column(String, nullable=False)
    abstract = Column(Text, nullable=False)

    authors = Column(ARRAY(String), nullable=False)
    organizations = Column(ARRAY(String), nullable=False)

    url = Column(String, nullable=False)  # URL to the paper publishment page
    pdf = Column(String, nullable=False)  # URL to the PDF of the paper

    journal = Column(String, nullable=True)
    doi = Column(String, nullable=True)

    summary = Column(Text, nullable=True)

    published_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


BaseModel.metadata.create_all(engine)

connection = engine.connect()
Session = sessionmaker(bind=engine)
