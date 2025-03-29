import datetime

import sqlalchemy
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, ARRAY


from env import DATABASE_URL

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    echo=True,
)


class Base(DeclarativeBase):
    pass


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    title: Mapped[str] = mapped_column(String, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)

    authors: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    organizations: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    url: Mapped[str] = mapped_column(
        String, nullable=False
    )  # URL to the paper publishment page
    pdf: Mapped[str] = mapped_column(
        String, nullable=False
    )  # URL to the PDF of the paper

    journal: Mapped[str] = mapped_column(String, nullable=True)
    doi: Mapped[str] = mapped_column(String, nullable=True)

    topics: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=True
    )  # List of topics extracted from the paper
    summary: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # Summary generated by the llm

    published_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)


Base.metadata.create_all(engine)

connection = engine.connect()
Session = sessionmaker(bind=engine)
