from sqlalchemy import Integer, Float
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from typing import Tuple

Base = declarative_base()

# docs: https://docs.sqlalchemy.org/en/20/orm/examples.html


# can adapt the entries by adding or removing lines
class Forecast(Base):
    __tablename__ = "forecasts"
    id: Mapped[int] = mapped_column(primary_key=True)
    gk: Mapped[float] = mapped_column(Float())
    gh_max: Mapped[float] = mapped_column(Float())
    tt: Mapped[float] = mapped_column(Float())
    ff: Mapped[float] = mapped_column(Float())

    def __init__(self, gk, gh_max, tt, ff):
        self.gk = float(gk)
        self.gh_max = float(gh_max)
        self.tt = float(tt)
        self.ff = float(ff)

    def __repr__(self) -> str:
        return "%s(id=%s), (%s, %s, %s, %s, %s)" % (
            "forecasts",
            self.id,
            self.gk,
            self.gh_max,
            self.tt,
            self.ff,
        )


class CarParams(Base):
    __tablename__ = "car_params"
    time: Mapped[int] = mapped_column(primary_key=True)
    cd: Mapped[float] = mapped_column(Float())
    cr: Mapped[float] = mapped_column(Float())

    def __init__(self, cd, cr):
        self.cd = cd
        self.cr = cr

    def __repr__(self) -> str:
        return "%s(id=%s), (%s, %s, %s)" % (
            "forecasts",
            self.time,
            self.cd,
            self.cr,
        )
