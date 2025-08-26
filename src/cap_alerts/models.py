from datetime import datetime
from enum import Enum
from itertools import chain
from typing import Self

import sqlalchemy
from geoalchemy2 import Geography, WKBElement
from lxml.etree import _Element
from shapely import Point, Polygon
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cap_alerts.db import Base
from cap_alerts.util import (
    IPAWSAlertsError,
    extract_quoted,
    findall,
    findalltext,
    findint,
    findtext,
)


class AlertScope(Enum):
    PUBLIC = "Public"
    RESTRICTED = "Restricted"
    PRIVATE = "Private"


class AlertStatus(Enum):
    ACTUAL = "Actual"
    EXERCISE = "Exercise"
    SYSTEM = "System"
    TEST = "Test"
    DRAFT = "Draft"


class AlertType(Enum):
    ALERT = "Alert"
    UPDATE = "Update"
    CANCEL = "Cancel"
    ACK = "Ack"
    ERROR = "Error"


class AlertCategoryCode(Enum):
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


class AlertCertainty(Enum):
    OBSERVED = "Observed"
    VERY = "Very Likely"
    LIKELY = "Likely"
    POSSIBLE = "Possible"
    UNLIKELY = "Unlikely"
    UNKNOWN = "Unknown"


class AlertResponseTypeCode(Enum):
    SHELTER = "Shelter"
    EVACUATE = "Evacuate"
    PREPARE = "Prepare"
    EXECUTE = "Execute"
    AVOID = "Avoid"
    MONITOR = "Monitor"
    ASSESS = "Assess"
    ALLCLEAR = "AllClear"
    NONE = "None"


class AlertSeverity(Enum):
    EXTREME = "Extreme"
    SEVERE = "Severe"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


class AlertUrgency(Enum):
    IMMEDIATE = "Immediate"
    EXPECTED = "Expected"
    FUTURE = "Future"
    PAST = "Past"
    UNKNOWN = "Unknown"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    identifier: Mapped[str]
    sender: Mapped[str]
    sent: Mapped[datetime]
    status: Mapped[str]
    msgtype: Mapped[str]
    source: Mapped[str | None]
    scope: Mapped[str]
    restriction: Mapped[str | None]
    note: Mapped[str | None]

    addresses: Mapped[list["AlertAddress"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan"
    )
    codes: Mapped[list["AlertCode"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan"
    )
    references: Mapped[list["AlertReference"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan"
    )
    incidents: Mapped[list["AlertIncident"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan"
    )
    alert_info: Mapped[list["AlertInfo"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan"
    )

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        if sent_str := findtext(elem, "cap:sent"):
            sent = datetime.fromisoformat(sent_str)
        else:
            sent = None

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
            identifier=findtext(elem, "cap:identifier"),
            sender=findtext(elem, "cap:sender"),
            sent=sent,
            status=findtext(elem, "cap:status"),
            msgtype=findtext(elem, "cap:msgType"),
            source=findtext(elem, "cap:source"),
            scope=findtext(elem, "cap:scope"),
            restriction=findtext(elem, "cap:restriction"),
            note=findtext(elem, "cap:note"),
            addresses=addresses,
            codes=codes,
            references=references,
            incidents=incidents,
            alert_info=alert_info,
        )


class AlertAddress(Base):
    __tablename__ = "alert_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"))
    address: Mapped[str]

    alert: Mapped[list["Alert"]] = relationship(back_populates="addresses")


class AlertCode(Base):
    __tablename__ = "alert_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"))
    code: Mapped[str]

    alert: Mapped[list["Alert"]] = relationship(back_populates="codes")


class AlertIncident(Base):
    __tablename__ = "alert_incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"))
    incident: Mapped[str]

    alert: Mapped[list["Alert"]] = relationship(back_populates="incidents")


class AlertReference(Base):
    __tablename__ = "alert_references"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"))
    sender: Mapped[str | None]
    identifier: Mapped[str]
    sent: Mapped[datetime | None]

    alert: Mapped[list["Alert"]] = relationship(back_populates="references")

    @classmethod
    def from_text(cls, text: str) -> Self:
        try:
            sender, identifier, sent_str = text.split(",")
            sent = datetime.fromisoformat(sent_str)
        except ValueError:
            identifier = text
            sender = None
            sent = None

        return cls(sender=sender, identifier=identifier, sent=sent)


class AlertInfo(Base):
    __tablename__ = "alert_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"))
    language: Mapped[str] = mapped_column(default="en-US")
    event: Mapped[str]
    urgency: Mapped[AlertUrgency] = mapped_column(
        sqlalchemy.Enum(
            AlertUrgency, values_callable=lambda t: [str(item.value) for item in t]
        )
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        sqlalchemy.Enum(
            AlertSeverity, values_callable=lambda t: [str(item.value) for item in t]
        )
    )
    certainty: Mapped[AlertCertainty] = mapped_column(
        sqlalchemy.Enum(
            AlertCertainty, values_callable=lambda t: [str(item.value) for item in t]
        )
    )
    audience: Mapped[str | None]
    effective: Mapped[datetime | None]
    onset: Mapped[datetime | None]
    expires: Mapped[datetime | None]
    sender_name: Mapped[str | None]
    headline: Mapped[str | None]
    description: Mapped[str | None]
    instruction: Mapped[str | None]
    web: Mapped[str | None]
    contact: Mapped[str | None]

    categories: Mapped[list["AlertInfoCategory"]] = relationship(
        back_populates="alert_info", cascade="all, delete-orphan"
    )
    response_types: Mapped[list["AlertInfoResponseType"]] = relationship(
        back_populates="alert_info", cascade="all, delete-orphan"
    )
    event_codes: Mapped[list["AlertInfoEventCode"]] = relationship(
        back_populates="alert_info", cascade="all, delete-orphan"
    )
    parameters: Mapped[list["AlertInfoParameter"]] = relationship(
        back_populates="alert_info", cascade="all, delete-orphan"
    )
    resources: Mapped[list["AlertInfoResource"]] = relationship(
        back_populates="alert_info", cascade="all, delete-orphan"
    )
    areas: Mapped[list["Area"]] = relationship(
        back_populates="alert_info", cascade="all, delete-orphan"
    )

    alert: Mapped["Alert"] = relationship(back_populates="alert_info")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
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

        if sent_str := findtext(elem, "cap:effective"):
            effective = datetime.fromisoformat(sent_str)
        else:
            effective = None

        if onset_str := findtext(elem, "cap:onset"):
            onset = datetime.fromisoformat(onset_str)
        else:
            onset = None

        if expires_str := findtext(elem, "cap:expires"):
            expires = datetime.fromisoformat(expires_str)
        else:
            expires = None

        return cls(
            language=findtext(elem, "cap:language"),
            event=findtext(elem, "cap:event"),
            urgency=findtext(elem, "cap:urgency"),
            severity=findtext(elem, "cap:severity"),
            certainty=findtext(elem, "cap:certainty"),
            audience=findtext(elem, "cap:audience"),
            effective=effective,
            onset=onset,
            expires=expires,
            sender_name=findtext(elem, "cap:senderName"),
            headline=findtext(elem, "cap:headline"),
            description=findtext(elem, "cap:description"),
            instruction=findtext(elem, "cap:instruction"),
            web=findtext(elem, "cap:web"),
            contact=findtext(elem, "cap:contact"),
            response_types=response_types,
            categories=categories,
            event_codes=event_codes,
            parameters=parameters,
            resources=resources,
            areas=areas,
        )


class AlertInfoCategory(Base):
    __tablename__ = "alert_info_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    alertinfo_id: Mapped[int] = mapped_column(ForeignKey("alert_info.id"))
    category: Mapped[AlertCategoryCode] = mapped_column(
        sqlalchemy.Enum(
            AlertCategoryCode, values_callable=lambda t: [str(item.value) for item in t]
        )
    )

    alert_info: Mapped["AlertInfo"] = relationship(back_populates="categories")


class AlertInfoResponseType(Base):
    __tablename__ = "alert_info_response_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    alertinfo_id: Mapped[int] = mapped_column(ForeignKey("alert_info.id"))
    responsetype: Mapped[AlertResponseTypeCode]

    alert_info: Mapped["AlertInfo"] = relationship(back_populates="response_types")


class AlertInfoEventCode(Base):
    __tablename__ = "alert_info_event_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    alertinfo_id: Mapped[int] = mapped_column(ForeignKey("alert_info.id"))
    value_name: Mapped[str]
    value: Mapped[str]

    alert_info: Mapped["AlertInfo"] = relationship(back_populates="event_codes")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        return cls(
            value_name=findtext(elem, "cap:valueName"),
            value=findtext(elem, "cap:value"),
        )


class AlertInfoParameter(Base):
    __tablename__ = "alert_info_parameters"

    id: Mapped[int] = mapped_column(primary_key=True)
    alertinfo_id: Mapped[int] = mapped_column(ForeignKey("alert_info.id"))
    value_name: Mapped[str]
    value: Mapped[str]

    alert_info: Mapped["AlertInfo"] = relationship(back_populates="parameters")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        return cls(
            value_name=findtext(elem, "cap:valueName"),
            value=findtext(elem, "cap:value"),
        )


class AlertInfoResource(Base):
    __tablename__ = "alert_info_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    alertinfo_id: Mapped[int] = mapped_column(ForeignKey("alert_info.id"))
    resource_description: Mapped[str]
    mime_type: Mapped[str]
    size: Mapped[int | None]
    uri: Mapped[str | None]
    deref_uri: Mapped[str | None]
    digest: Mapped[str | None]

    alert_info: Mapped["AlertInfo"] = relationship(back_populates="resources")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        return cls(
            resource_description=findtext(elem, "cap:resourceDesc"),
            mime_type=findtext(elem, "cap:mimeType"),
            size=findint(elem, "cap:size"),
            uri=findtext(elem, "cap:uri"),
            deref_uri=findtext(elem, "cap:derefUri"),
            digest=findtext(elem, "cap:digest"),
        )


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(primary_key=True)
    alertinfo_id: Mapped[int] = mapped_column(ForeignKey("alert_info.id"))
    area_description: Mapped[str]
    altitude: Mapped[int | None]
    ceiling: Mapped[int | None]

    polygons: Mapped[list["AreaPolygon"]] = relationship(
        back_populates="area", cascade="all, delete-orphan"
    )
    geocodes: Mapped[list["AreaGeoCode"]] = relationship(
        back_populates="area", cascade="all, delete-orphan"
    )

    alert_info: Mapped["AlertInfo"] = relationship(back_populates="areas")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
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
            )
        )

        geocodes = [AreaGeoCode.from_element(x) for x in findall(elem, "cap:geocode")]

        return cls(
            area_description=findtext(elem, "cap:areaDesc"),
            altitude=findint(elem, "cap:altitude"),
            ceiling=findint(elem, "cap:ceiling"),
            polygons=polygons,
            geocodes=geocodes,
        )


class AreaGeoCode(Base):
    __tablename__ = "area_geocodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"))
    value_name: Mapped[str]
    value: Mapped[str]

    area: Mapped["Area"] = relationship(back_populates="geocodes")

    @classmethod
    def from_element(cls, elem: _Element) -> Self:
        return cls(
            value_name=findtext(elem, "cap:valueName"),
            value=findtext(elem, "cap:value"),
        )


class AreaPolygon(Base):
    __tablename__ = "area_polygons"

    id: Mapped[int] = mapped_column(primary_key=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"))
    geom: Mapped[WKBElement] = mapped_column(
        Geography(geometry_type="POLYGON", srid=4326)
    )

    area: Mapped["Area"] = relationship(back_populates="polygons")

    @classmethod
    def from_circle_text(cls, text: str) -> Self:
        try:
            coords, radius = text.split()
            latitude, longitude = coords.split(",")
        except ValueError as e:
            raise IPAWSAlertsError("Malformed AreaPolygon[circle]", text) from e

        circle = Point(float(latitude), float(longitude)).buffer(float(radius) * 1000)
        return cls(geom=f"srid=4326;{circle.wkt}")

    @classmethod
    def from_polygon_text(cls, text: str) -> Self:
        points = []

        try:
            for point in text.split():
                latitude, longitude = point.split(",")
                points.append(Point(float(longitude), float(latitude)))
        except ValueError as e:
            raise IPAWSAlertsError("Malformed AreaPolygon[polygon]", text) from e

        polygon = Polygon(points)
        return cls(geom=f"srid=4326;{polygon.wkt}")
