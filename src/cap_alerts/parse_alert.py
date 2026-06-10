from datetime import datetime
from typing import TYPE_CHECKING

from geoalchemy2.shape import from_shape
from shapely.geometry import Point, Polygon

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

from cap_alerts.models import (
    Alert,
    AlertAddress,
    AlertCategoryCode,
    AlertCertainty,
    AlertCode,
    AlertIncident,
    AlertInfo,
    AlertInfoCategory,
    AlertInfoEventCode,
    AlertInfoParameter,
    AlertInfoResource,
    AlertInfoResponseType,
    AlertReference,
    AlertResponseTypeCode,
    AlertScope,
    AlertSeverity,
    AlertStatus,
    AlertType,
    AlertUrgency,
    Area,
    AreaGeoCode,
    AreaPolygon,
)


def extract_alert(elem: _Element) -> Alert:
    alert = Alert(
        identifier=find_text(elem, "cap:identifier"),
        sender=find_text(elem, "cap:sender"),
        sent=find_date(elem, "cap:sent"),
        status=AlertStatus(find_text(elem, "cap:status")),
        msgtype=AlertType(find_text(elem, "cap:msgType")),
        source=find_text(elem, "cap:source", optional=True),
        scope=AlertScope(find_text(elem, "cap:scope")),
        restriction=get_text(elem, "cap:restriction"),
        note=get_text(elem, "cap:note"),
    )

    # Extract addresses
    alert.addresses = [
        AlertAddress(address=x, alert=alert)
        for x in extract_quoted(elem, "cap:addresses")
    ]

    # Extract incidents
    alert.incidents = [
        AlertIncident(incident=x, alert=alert)
        for x in extract_quoted(elem, "cap:incidents")
    ]

    # Extract codes
    alert.codes = [
        AlertCode(code=x, alert=alert) for x in findalltext(elem, "cap:code")
    ]

    # Extract references
    for reference_str in extract_quoted(elem, "cap:references"):
        try:
            sender, identifier, sent_str = reference_str.split(",")
            sent = datetime.fromisoformat(sent_str)
        except ValueError:
            identifier = reference_str
            sender = None
            sent = None

        alert.references.append(
            AlertReference(sender=sender, identifier=identifier, sent=sent, alert=alert)
        )

    # Extract alert infos
    for alert_info_elem in findall(elem, "cap:info"):
        alert_info = AlertInfo(
            alert=alert,
            language=find_text(alert_info_elem, "cap:language", optional=True)
            or "en-US",
            event=find_text(alert_info_elem, "cap:event"),
            urgency=AlertUrgency(find_text(alert_info_elem, "cap:urgency")),
            severity=AlertSeverity(find_text(alert_info_elem, "cap:severity")),
            certainty=AlertCertainty(find_text(alert_info_elem, "cap:certainty")),
            audience=get_text(alert_info_elem, "cap:audience"),
            effective=get_date(alert_info_elem, "cap:effective"),
            onset=get_date(alert_info_elem, "cap:onset"),
            expires=get_date(alert_info_elem, "cap:expires"),
            sender_name=get_text(alert_info_elem, "cap:senderName"),
            headline=get_text(alert_info_elem, "cap:headline"),
            description=get_text(alert_info_elem, "cap:description"),
            instruction=get_text(alert_info_elem, "cap:instruction"),
            web=get_text(alert_info_elem, "cap:web"),
            contact=get_text(alert_info_elem, "cap:contact"),
        )

        # Extract response types
        alert_info.response_types = [
            AlertInfoResponseType(responsetype=AlertResponseTypeCode(x))
            for x in findalltext(alert_info_elem, "cap:responseType")
        ]

        # Extract categories
        alert_info.categories = [
            AlertInfoCategory(category=AlertCategoryCode(x))
            for x in findalltext(alert_info_elem, "cap:category")
        ]

        # Extract event codes
        alert_info.event_codes = [
            AlertInfoEventCode(
                value_name=find_text(event_code_elem, "cap:valueName"),
                value=find_text(event_code_elem, "cap:value"),
            )
            for event_code_elem in findall(alert_info_elem, "cap:eventCode")
        ]

        # Extract parameters
        alert_info.parameters = [
            AlertInfoParameter(
                value_name=find_text(parameter_elem, "cap:valueName"),
                value=find_text(parameter_elem, "cap:value"),
            )
            for parameter_elem in findall(alert_info_elem, "cap:parameter")
        ]

        # Extract resources
        alert_info.resources = [
            AlertInfoResource(
                resource_description=find_text(resource_elem, "cap:resourceDesc"),
                mime_type=find_text(resource_elem, "cap:mimeType"),
                size=get_int(resource_elem, "cap:size"),
                uri=get_text(resource_elem, "cap:uri"),
                deref_uri=get_text(resource_elem, "cap:derefUri"),
                digest=get_text(resource_elem, "cap:digest"),
            )
            for resource_elem in findall(alert_info_elem, "cap:resource")
        ]

        # Extract areas
        for area_elem in findall(alert_info_elem, "cap:area"):
            area = Area(
                area_description=find_text(area_elem, "cap:areaDesc"),
                altitude=get_int(area_elem, "cap:altitude"),
                ceiling=get_int(area_elem, "cap:ceiling"),
            )

            # Extract true polygons
            for polygon_str in findalltext(area_elem, "cap:polygon"):
                try:
                    points = []
                    for point in polygon_str.split():
                        latitude, longitude = point.split(",")
                        points.append(Point(float(longitude), float(latitude)))
                    area.polygons.append(
                        AreaPolygon(geom=from_shape(Polygon(points), srid=4326))
                    )

                except ValueError as e:
                    msg = "Malformed AreaPolygon[polygon]"
                    raise MalformedPolygonError(msg, polygon_str) from e

            # Extract circles
            for circle_str in findalltext(area_elem, "cap:circle"):
                try:
                    coords, radius = circle_str.split()
                    latitude, longitude = coords.split(",")

                    circle: Point = Point(float(latitude), float(longitude)).buffer(
                        float(radius) * 1000
                    )
                    area.polygons.append(
                        AreaPolygon(geom=from_shape(circle, srid=4326))
                    )

                except ValueError as e:
                    msg = "Malformed AreaPolygon[circle]"
                    raise MalformedPolygonError(msg, circle_str) from e

            # Extract geo codes
            for geocode_elem in findall(area_elem, "cap:geocode"):
                area.geocodes.append(
                    AreaGeoCode(
                        value_name=find_text(geocode_elem, "cap:valueName"),
                        value=find_text(geocode_elem, "cap:value"),
                    )
                )

            alert_info.areas.append(area)

        alert.alert_info.append(alert_info)

    return alert
