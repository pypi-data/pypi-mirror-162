from sqlalchemy import (
    Integer,
    Column,
    Boolean,
    DateTime,
    ForeignKey
)
from datetime import datetime
from ...database import Base


class NCTCompanyScientificLinkModel(Base):
    __tablename__ = "nct_company_scientific_links"

    id = Column(Integer, primary_key=True)
    nct_study_id = Column(
        Integer,
        ForeignKey('nct_study.id'),
        nullable=False,
    )
    company_scientific_link_id = Column(
        Integer,
        ForeignKey('company_scientific_links.id'),
        nullable=False,
    )
    is_deleted = Column(
        Boolean,
        nullable=True
    )
    date = Column(DateTime, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
