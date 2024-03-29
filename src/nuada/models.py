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
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default='In Progress')
    commentary: Mapped[Optional[str]] = mapped_column(String(100))

    __table_args__ = (UniqueConstraint('year', 'month', name='_uc_year_month'),)

    def __repr__(self) -> str:
        return f'''(control_id: {self.control_id}, 
                    timestamp: {self.timestamp}, 
                    year: {self.year}, 
                    month: {self.month},
                    status: {self.status}, 
                    commentary: {self.commentary})'''

class Term(Base):
    '''
    Represents the terms (and their as sociated frequencies) sourced from the relevant outlet in `Source`
    '''
    __tablename__ = 'term'

    term_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    term: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey('source.source_id'))
    control_id: Mapped[int] = mapped_column(ForeignKey('control.control_id'))
    frequency: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('term', 'source_id', 'control_id', name='_uc_term_source_control'),)

    def __repr__(self) -> str:
        return f'''(term_id: {self.term_id}, 
                    term: {self.term}, 
                    source_id: {self.source_id}, 
                    control_id: {self.control_id}, 
                    frequency: {self.frequency})'''

class Source(Base):
    '''
    Represents data on the 'source' (e.g. the 'New York Times')
    '''
    __tablename__ = 'source'

    source_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alias: Mapped[str] = mapped_column(String(30), nullable=False)

    __table_args__ = (UniqueConstraint('alias', name='_uc_alias'),)

    def __repr__(self) -> str:
        return f'(source_id: {self.source_id}, alias: {self.alias})'

if __name__ == '__main__':
    pass