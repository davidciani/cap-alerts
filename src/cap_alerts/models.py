"""models.py - Data models for cap_alerts."""

from datetime import datetime  # noqa: TC003
from enum import StrEnum
from typing import Any

from geoalchemy2 import Geography
from sqlalchemy import Column
from sqlmodel import DateTime, Field, Relationship, SQLModel


class AlertScope(StrEnum):
    """Enumeration of scope of alert disemination."""

    PUBLIC = "Public"
    RESTRICTED = "Restricted"
    PRIVATE = "Private"


class AlertStatus(StrEnum):
    """Enumeration of status of an alert."""

    ACTUAL = "Actual"
    EXERCISE = "Exercise"
    SYSTEM = "System"
    TEST = "Test"
    DRAFT = "Draft"


class AlertType(StrEnum):
    """Enumeration of type of alert."""

    ALERT = "Alert"
    UPDATE = "Update"
    CANCEL = "Cancel"
    ACK = "Ack"
    ERROR = "Error"


class AlertCategoryCode(StrEnum):
    """Enumeration of type of event described by an alert."""

    GEO = "Geo"
    MET = "Met"
    SAFETY = "Safety"
    SECURITY = "Security"
    RESCUE = "Rescue"
    FIRE = "Fire"
    HEALTH = "Health"
    ENV = "Env"
    TRANSPORT = "Transport"
    INFRA = "Infra"
    CBRNE = "CBRNE"
    OTHER = "Other"


class AlertCertainty(StrEnum):
    """Enumeration of certainty of event."""

    OBSERVED = "Observed"
    VERY = "Very Likely"
    LIKELY = "Likely"
    POSSIBLE = "Possible"
    UNLIKELY = "Unlikely"
    UNKNOWN = "Unknown"


class AlertResponseTypeCode(StrEnum):
    """Enumeration of how one should respond to the alert."""

    SHELTER = "Shelter"
    EVACUATE = "Evacuate"
    PREPARE = "Prepare"
    EXECUTE = "Execute"
    AVOID = "Avoid"
    MONITOR = "Monitor"
    ASSESS = "Assess"
    ALLCLEAR = "AllClear"
    NONE = "None"


class AlertSeverity(StrEnum):
    """Enumeration of severity of the potential event."""

    EXTREME = "Extreme"
    SEVERE = "Severe"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


class AlertUrgency(StrEnum):
    """Enumeration of alert's urgency."""

    IMMEDIATE = "Immediate"
    EXPECTED = "Expected"
    FUTURE = "Future"
    PAST = "Past"
    UNKNOWN = "Unknown"


class Alert(SQLModel, table=True):
    """An alert."""

    __tablename__: str = "alerts"

    id: int | None = Field(default=None, primary_key=True)
    identifier: str
    sender: str
    sent: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    status: AlertStatus
    msgtype: AlertType
    source: str | None
    scope: AlertScope
    restriction: str | None
    note: str | None

    addresses: list[AlertAddress] = Relationship(
        back_populates="alert", cascade_delete=True
    )
    codes: list[AlertCode] = Relationship(back_populates="alert", cascade_delete=True)
    references: list[AlertReference] = Relationship(
        back_populates="alert", cascade_delete=True
    )
    incidents: list[AlertIncident] = Relationship(
        back_populates="alert", cascade_delete=True
    )
    alert_info: list[AlertInfo] = Relationship(
        back_populates="alert", cascade_delete=True
    )


class AlertAddress(SQLModel, table=True):
    """Address associated with an Alert."""

    __tablename__: str = "alert_addresses"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int | None = Field(default=None, foreign_key="alerts.id")
    address: str

    alert: Alert = Relationship(back_populates="addresses")


class AlertCode(SQLModel, table=True):
    """Code associated with an Alert."""

    __tablename__: str = "alert_codes"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int | None = Field(default=None, foreign_key="alerts.id")
    code: str

    alert: Alert = Relationship(back_populates="codes")


class AlertIncident(SQLModel, table=True):
    """Incidents associated with an alert."""

    __tablename__: str = "alert_incidents"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int | None = Field(default=None, foreign_key="alerts.id")
    incident: str

    alert: Alert = Relationship(back_populates="incidents")


class AlertReference(SQLModel, table=True):
    """Reference to another alert associated with an Alert."""

    __tablename__: str = "alert_references"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int | None = Field(default=None, foreign_key="alerts.id")
    sender: str | None
    identifier: str
    sent: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))

    alert: Alert = Relationship(back_populates="references")


class AlertInfo(SQLModel, table=True):
    """A set of information being communicated about an alert."""

    __tablename__: str = "alert_info"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int | None = Field(default=None, foreign_key="alerts.id")
    language: str = Field(default="en-US")
    event: str
    urgency: AlertUrgency
    severity: AlertSeverity
    certainty: AlertCertainty
    audience: str | None
    effective: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))
    onset: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))
    expires: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))
    sender_name: str | None
    headline: str | None
    description: str | None
    instruction: str | None
    web: str | None
    contact: str | None

    categories: list[AlertInfoCategory] = Relationship(
        back_populates="alert_info", cascade_delete=True
    )
    response_types: list[AlertInfoResponseType] = Relationship(
        back_populates="alert_info", cascade_delete=True
    )
    event_codes: list[AlertInfoEventCode] = Relationship(
        back_populates="alert_info", cascade_delete=True
    )
    parameters: list[AlertInfoParameter] = Relationship(
        back_populates="alert_info", cascade_delete=True
    )
    resources: list[AlertInfoResource] = Relationship(
        back_populates="alert_info", cascade_delete=True
    )
    areas: list[Area] = Relationship(back_populates="alert_info", cascade_delete=True)

    alert: Alert = Relationship(back_populates="alert_info")


class AlertInfoCategory(SQLModel, table=True):
    """A category associated with an AlertInfo."""

    __tablename__: str = "alert_info_categories"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int | None = Field(default=None, foreign_key="alert_info.id")
    category: AlertCategoryCode

    alert_info: AlertInfo = Relationship(back_populates="categories")


class AlertInfoResponseType(SQLModel, table=True):
    """Response type associated with an AlertInfo."""

    __tablename__: str = "alert_info_response_types"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int | None = Field(default=None, foreign_key="alert_info.id")
    responsetype: AlertResponseTypeCode

    alert_info: AlertInfo = Relationship(back_populates="response_types")


class AlertInfoEventCode(SQLModel, table=True):
    """Event code associated with an AlertInfo."""

    __tablename__: str = "alert_info_event_codes"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int | None = Field(default=None, foreign_key="alert_info.id")
    value_name: str
    value: str

    alert_info: AlertInfo = Relationship(back_populates="event_codes")


class AlertInfoParameter(SQLModel, table=True):
    """Parameter associated with an AlertInfo."""

    __tablename__: str = "alert_info_parameters"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int | None = Field(default=None, foreign_key="alert_info.id")
    value_name: str
    value: str

    alert_info: AlertInfo = Relationship(back_populates="parameters")


class AlertInfoResource(SQLModel, table=True):
    """External resource attached to an AlertInfo."""

    __tablename__: str = "alert_info_resources"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int | None = Field(default=None, foreign_key="alert_info.id")
    resource_description: str
    mime_type: str
    size: int | None
    uri: str | None
    deref_uri: str | None
    digest: str | None

    alert_info: AlertInfo = Relationship(back_populates="resources")


class Area(SQLModel, table=True):
    """A geographic area that an alert applies to."""

    __tablename__: str = "areas"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int | None = Field(default=None, foreign_key="alert_info.id")
    area_description: str
    altitude: int | None
    ceiling: int | None

    polygons: list[AreaPolygon] = Relationship(
        back_populates="area", cascade_delete=True
    )
    geocodes: list[AreaGeoCode] = Relationship(
        back_populates="area", cascade_delete=True
    )

    alert_info: AlertInfo = Relationship(back_populates="areas")


class AreaGeoCode(SQLModel, table=True):
    """Geocode-based description for an area."""

    __tablename__: str = "area_geocodes"

    id: int | None = Field(default=None, primary_key=True)
    area_id: int | None = Field(default=None, foreign_key="areas.id")
    value_name: str
    value: str

    area: Area = Relationship(back_populates="geocodes")


class AreaPolygon(SQLModel, table=True):
    """Polygon-based description for an area."""

    __tablename__: str = "area_polygons"

    id: int | None = Field(default=None, primary_key=True)
    area_id: int | None = Field(default=None, foreign_key="areas.id")
    geom: Any = Field(sa_column=Column(Geography("POLYGON", srid=4326)))

    area: Area = Relationship(back_populates="polygons")
