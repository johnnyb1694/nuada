from sqlalchemy import String, Integer, DateTime, UniqueConstraint, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
    pass

class Control(Base):
    '''
    Used to capture metadata on the specific run being performed (i.e. what time the run was performed and its corresponding identifier)
    '''
    __tablename__ = 'control'

    control_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default='Initialised')
    commentary: Mapped[Optional[str]] = mapped_column(String(100), default='N/A')

    def __repr__(self) -> str:
        return f'Control(control_id={self.control_id}, timestamp={self.timestamp}, status={self.status}, commentary={self.commentary})'

class Article(Base):
    '''
    Represents article metadata. This principally consists of the article publication date, headline and abstract
    '''
    __tablename__ = 'article'

    article_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    publication_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey('source.source_id'))
    control_id: Mapped[int] = mapped_column(ForeignKey('control.control_id'))

    def __repr__(self) -> str:
        return f'Article(article_id={self.article_id}, publication_date={self.publication_date}, headline={self.headline}, abstract={self.abstract})'

class Source(Base):
    '''
    Represents data on a specific news 'source' (e.g. the 'New York Times')
    '''
    __tablename__ = 'source'

    source_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_alias: Mapped[str] = mapped_column(String(30), nullable=False)

    __table_args__ = (UniqueConstraint('source_alias', name='_uc_source_alias'),)

    def __repr__(self) -> str:
        return f'Source(source_id={self.source_id}, source_alias={self.source_alias})'

if __name__ == '__main__':
    pass