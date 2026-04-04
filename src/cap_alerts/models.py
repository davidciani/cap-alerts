"""models.py - Data models for cap_alerts."""

from datetime import datetime
from enum import Enum
from itertools import chain
from typing import TYPE_CHECKING, Any, Self

from geoalchemy2 import Geography
from geoalchemy2.shape import from_shape
from shapely import Point, Polygon
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel

from cap_alerts.db import Base
from cap_alerts.util import (
    MalformedPolygonError,
    extract_quoted,
    find_date,
    find_text,
    findall,
    findalltext,
    get_date,
    get_int,
    get_text,
)

if TYPE_CHECKING:
    from lxml.etree import _Element


class AlertScope(str, Enum):
    """Scope of alert disemination."""

    PUBLIC = "Public"
    RESTRICTED = "Restricted"
    PRIVATE = "Private"


class AlertStatus(str, Enum):
    """Status of an alert."""

    ACTUAL = "Actual"
    EXERCISE = "Exercise"
    SYSTEM = "System"
    TEST = "Test"
    DRAFT = "Draft"


class AlertType(str, Enum):
    """Type of alert."""

    ALERT = "Alert"
    UPDATE = "Update"
    CANCEL = "Cancel"
    ACK = "Ack"
    ERROR = "Error"


class AlertCategoryCode(str, Enum):
    """The type of event described by an alert."""

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


class AlertCertainty(str, Enum):
    """Certainty of event."""

    OBSERVED = "Observed"
    VERY = "Very Likely"
    LIKELY = "Likely"
    POSSIBLE = "Possible"
    UNLIKELY = "Unlikely"
    UNKNOWN = "Unknown"


class AlertResponseTypeCode(str, Enum):
    """How one should respond to the alert."""

    SHELTER = "Shelter"
    EVACUATE = "Evacuate"
    PREPARE = "Prepare"
    EXECUTE = "Execute"
    AVOID = "Avoid"
    MONITOR = "Monitor"
    ASSESS = "Assess"
    ALLCLEAR = "AllClear"
    NONE = "None"


class AlertSeverity(str, Enum):
    """The severity of the potential event."""

    EXTREME = "Extreme"
    SEVERE = "Severe"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


class AlertUrgency(str, Enum):
    """An alert's urgency."""

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
    sent: datetime
    status: str
    msgtype: str
    source: str | None
    scope: str
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

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        """Instantiate _cls_ from xml element.

        Args:
            elem (_Element): XML element representing _cls_.

        Returns:
            Self: Instantiated _cls_.
        """
        addresses = [
            AlertAddress(address=x) for x in extract_quoted(elem, "cap:addresses")
        ]
        codes = [AlertCode(code=x) for x in findalltext(elem, "cap:code")]
        references = [
            AlertReference.from_text(x) for x in extract_quoted(elem, "cap:references")
        ]
        incidents = [
            AlertIncident(incident=x) for x in extract_quoted(elem, "cap:incidents")
        ]
        alert_info = [AlertInfo.from_element(x) for x in findall(elem, "cap:info")]
        return cls(
            identifier=find_text(elem, "cap:identifier"),
            sender=find_text(elem, "cap:sender"),
            sent=find_date(elem, "cap:sent"),
            status=find_text(elem, "cap:status"),
            msgtype=find_text(elem, "cap:msgType"),
            source=find_text(elem, "cap:source"),
            scope=find_text(elem, "cap:scope"),
            restriction=get_text(elem, "cap:restriction"),
            note=get_text(elem, "cap:note"),
            addresses=addresses,
            codes=codes,
            references=references,
            incidents=incidents,
            alert_info=alert_info,
        )


class AlertAddress(SQLModel, table=True):
    """Address associated with an Alert."""

    __tablename__: str = "alert_addresses"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int = Field(foreign_key="alerts.id")
    address: str

    alert: Alert = Relationship(back_populates="addresses")


class AlertCode(SQLModel, table=True):
    """Code associated with an Alert."""

    __tablename__: str = "alert_codes"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int = Field(foreign_key="alerts.id")
    code: str

    alert: Alert = Relationship(back_populates="codes")


class AlertIncident(SQLModel, table=True):
    """Incidents associated with an alert."""

    __tablename__: str = "alert_incidents"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int = Field(foreign_key="alerts.id")
    incident: str

    alert: Alert = Relationship(back_populates="incidents")


class AlertReference(SQLModel, table=True):
    """Reference to another alert associated with an Alert."""

    __tablename__: str = "alert_references"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int = Field(foreign_key="alerts.id")
    sender: str | None
    identifier: str
    sent: datetime | None

    alert: Alert = Relationship(back_populates="references")

    @classmethod
    def from_text(cls, text: str) -> Self:
        """Instantiate AlertReference from text.

        Args:
            text (str): reference text

        Returns:
            Self: Instantiated AlertReference.
        """
        try:
            sender, identifier, sent_str = text.split(",")
            sent = datetime.fromisoformat(sent_str)
        except ValueError:
            identifier = text
            sender = None
            sent = None

        return cls(sender=sender, identifier=identifier, sent=sent)


class AlertInfo(Base):
    """A set of information being communicated about an alert."""

    __tablename__: str = "alert_info"

    id: int | None = Field(default=None, primary_key=True)
    alert_id: int = Field(foreign_key="alerts.id")
    language: str = Field(default="en-US")
    event: str
    urgency: AlertUrgency
    severity: AlertSeverity
    certainty: AlertCertainty
    audience: str | None
    effective: datetime
    onset: datetime
    expires: datetime
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

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        """Instantiate AlertInfo from xml element.

        Args:
            elem (_Element): XML element representing AlertInfo.

        Returns:
            Self: Instantiated AlertInfo.
        """
        response_types = [
            AlertInfoResponseType(responsetype=AlertResponseTypeCode(x))
            for x in findalltext(elem, "cap:responseType")
        ]
        event_codes = [
            AlertInfoEventCode.from_element(x) for x in findall(elem, "cap:eventCode")
        ]
        categories = [
            AlertInfoCategory(category=AlertCategoryCode(x))
            for x in findalltext(elem, "cap:category")
        ]
        parameters = [
            AlertInfoParameter.from_element(x) for x in findall(elem, "cap:parameter")
        ]
        resources = [
            AlertInfoResource.from_element(x) for x in findall(elem, "cap:resource")
        ]
        areas = [Area.from_element(x) for x in findall(elem, "cap:area")]

        return cls(
            language=find_text(elem, "cap:language"),
            event=find_text(elem, "cap:event"),
            urgency=AlertUrgency(find_text(elem, "cap:urgency")),
            severity=AlertSeverity(find_text(elem, "cap:severity")),
            certainty=AlertCertainty(find_text(elem, "cap:certainty")),
            audience=get_text(elem, "cap:audience"),
            effective=get_date(elem, "cap:effective"),
            onset=get_date(elem, "cap:onset"),
            expires=get_date(elem, "cap:expires"),
            sender_name=get_text(elem, "cap:senderName"),
            headline=get_text(elem, "cap:headline"),
            description=get_text(elem, "cap:description"),
            instruction=get_text(elem, "cap:instruction"),
            web=get_text(elem, "cap:web"),
            contact=get_text(elem, "cap:contact"),
            response_types=response_types,
            categories=categories,
            event_codes=event_codes,
            parameters=parameters,
            resources=resources,
            areas=areas,
        )


class AlertInfoCategory(SQLModel, table=True):
    """A category associated with an AlertInfo."""

    __tablename__: str = "alert_info_categories"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int = Field(foreign_key="alert_info.id")
    category: AlertCategoryCode

    alert_info: AlertInfo = Relationship(back_populates="categories")


class AlertInfoResponseType(SQLModel, table=True):
    """Response type associated with an AlertInfo."""

    __tablename__: str = "alert_info_response_types"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int = Field(foreign_key="alert_info.id")
    responsetype: AlertResponseTypeCode

    alert_info: AlertInfo = Relationship(back_populates="response_types")


class AlertInfoEventCode(SQLModel, table=True):
    """Event code associated with an AlertInfo."""

    __tablename__: str = "alert_info_event_codes"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int = Field(foreign_key="alert_info.id")
    value_name: str
    value: str

    alert_info: AlertInfo = Relationship(back_populates="event_codes")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        """Instantiate AlertInfoEventCode from xml element.

        Args:
            elem (_Element): XML element representing AlertInfoEventCode.

        Returns:
            Self: Instantiated AlertInfoEventCode.
        """
        return cls(
            value_name=find_text(elem, "cap:valueName"),
            value=find_text(elem, "cap:value"),
        )


class AlertInfoParameter(Base):
    """Parameter associated with an AlertInfo."""

    __tablename__: str = "alert_info_parameters"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int = Field(foreign_key="alert_info.id")
    value_name: str
    value: str

    alert_info: AlertInfo = Relationship(back_populates="parameters")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        """Instantiate AlertInfoParameter from xml element.

        Args:
            elem (_Element): XML element representing AlertInfoParameter.

        Returns:
            Self: Instantiated AlertInfoParameter.
        """
        return cls(
            value_name=find_text(elem, "cap:valueName"),
            value=find_text(elem, "cap:value"),
        )


class AlertInfoResource(SQLModel, table=True):
    """External resource attached to an AlertInfo."""

    __tablename__: str = "alert_info_resources"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int = Field(foreign_key="alert_info.id")
    resource_description: str
    mime_type: str
    size: int | None
    uri: str | None
    deref_uri: str | None
    digest: str | None

    alert_info: AlertInfo = Relationship(back_populates="resources")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        """Instantiate AlertInfoResource from xml element.

        Args:
            elem (_Element): XML element representing AlertInfoResource.

        Returns:
            Self: Instantiated AlertInfoResource.
        """
        return cls(
            resource_description=find_text(elem, "cap:resourceDesc"),
            mime_type=find_text(elem, "cap:mimeType"),
            size=get_int(elem, "cap:size"),
            uri=get_text(elem, "cap:uri"),
            deref_uri=get_text(elem, "cap:derefUri"),
            digest=get_text(elem, "cap:digest"),
        )


class Area(SQLModel, table=True):
    """A geographic area that an alert applies to."""

    __tablename__: str = "areas"

    id: int | None = Field(default=None, primary_key=True)
    alertinfo_id: int = Field(foreign_key="alert_info.id")
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

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        """Instantiate Area from xml element.

        Args:
            elem (_Element): XML element representing Area.

        Returns:
            Self: Instantiated Area.
        """
        polygons = list(
            chain(
                [
                    AreaPolygon.from_polygon_text(x)
                    for x in findalltext(elem, "cap:polygon")
                ],
                [
                    AreaPolygon.from_circle_text(x)
                    for x in findalltext(elem, "cap:circle")
                ],
            ),
        )

        geocodes = [AreaGeoCode.from_element(x) for x in findall(elem, "cap:geocode")]

        return cls(
            area_description=find_text(elem, "cap:areaDesc"),
            altitude=get_int(elem, "cap:altitude"),
            ceiling=get_int(elem, "cap:ceiling"),
            polygons=polygons,
            geocodes=geocodes,
        )


class AreaGeoCode(SQLModel, table=True):
    """Geocode-based description for an area."""

    __tablename__: str = "area_geocodes"

    id: int | None = Field(default=None, primary_key=True)
    area_id: int = Field(foreign_key="areas.id")
    value_name: str
    value: str

    area: Area = Relationship(back_populates="geocodes")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        """Instantiate AreaGeoCode from xml element.

        Args:
            elem (_Element): XML element representing AreaGeoCode.

        Returns:
            Self: Instantiated AreaGeoCode.
        """
        return cls(
            value_name=find_text(elem, "cap:valueName"),
            value=find_text(elem, "cap:value"),
        )


class AreaPolygon(SQLModel, table=True):
    """Polygon-based description for an area."""

    __tablename__: str = "area_polygons"

    id: int | None = Field(default=None, primary_key=True)
    area_id: int = Field(foreign_key="areas.id")
    geom: Any = Field(sa_column=Column(Geography("POLYGON", srid=4326)))

    area: Area = Relationship(back_populates="polygons")

    @classmethod
    def from_circle_text(cls, text: str) -> Self:
        """Instantiate Polygon from text description of circle.

        Args:
            text (str): text description of circle.

        Returns:
            Self: Polygon representing the circle.
        """
        try:
            coords, radius = text.split()
            latitude, longitude = coords.split(",")
        except ValueError as e:
            msg = "Malformed AreaPolygon[circle]"
            raise MalformedPolygonError(msg, text) from e

        circle = Point(float(latitude), float(longitude)).buffer(float(radius) * 1000)
        return cls(geom=from_shape(circle, srid=4326))

    @classmethod
    def from_polygon_text(cls, text: str) -> Self:
        """Instantiate Polygon from text description of polygon.

        Args:s
            text (str): text description of polygon.

        Returns:
            Self: Instantiated Polygon.
        """
        points = []

        try:
            for point in text.split():
                latitude, longitude = point.split(",")
                points.append(Point(float(longitude), float(latitude)))
        except ValueError as e:
            msg = "Malformed AreaPolygon[polygon]"
            raise MalformedPolygonError(msg, text) from e

        polygon = Polygon(points)

        return cls(geom=from_shape(polygon, srid=4326))
