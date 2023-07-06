from typing import Any, cast

from pydantic.dataclasses import dataclass
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Float, Integer, String
from fastapi import HTTPException, status

from tnsquery.db.base import Base


@dataclass
class Transient:
    """Model for transient data without a link to the database."""

    name: str
    redshift: float
    ra: float
    dec: float
    ebv: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Transient":
        return cls(
            name=data["objname"],
            redshift=data["redshift"],
            ra=data["ra"],
            dec=data["dec"],
            ebv=data["ebv"],
        )


class ATModel(Base):
    """Model to hold AT/SN data."""

    __tablename__ = "transients"

    id = Column(
        "id", Integer, primary_key=True, autoincrement=True
    )  # Local (cached) ID
    name = Column(
        "name", String(100), nullable=False, unique=True
    )  # noqa: WPS432  # IAU name
    redshift = Column("redshift", Float)
    ra = Column("ra", Float)  # Right ascension (J2000) in degrees
    dec = Column("dec", Float)  # Declination (J2000) in degrees
    ebv = Column("ebv", Float)  # E(B-V) from SFD(2011) dust map from IRSA.

    @classmethod
    def from_transient(cls, transient: Transient) -> "ATModel":
        return cls(
            name=transient.name,
            redshift=transient.redshift,
            ra=transient.ra,
            dec=transient.dec,
            ebv=transient.ebv,
        )

    def as_transient(self) -> Transient:
        return Transient(
            name=cast(str, self.name),
            redshift=cast(float, self.redshift),
            ra=cast(float, self.ra),
            dec=cast(float, self.dec),
            ebv=cast(float, self.ebv),
        )


def verify_transient_name(name: str) -> str:
    name = name.strip()

    if name.lower().startswith("sn") or name.lower().startswith("at"):
        name = name[2:]

    if not name[0:2].isnumeric():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Name should be of form <year><identifier> but was: {name}",
        )

    return name
