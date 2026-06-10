"""load_alerts.py -- extract alerts from jsonl and load to database."""

import logging
import lzma
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import msgspec.json
from lxml import etree
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from sqlmodel import Session, SQLModel, create_engine

from cap_alerts.parse_alert import extract_alert

if TYPE_CHECKING:
    from cap_alerts import models

logger = logging.getLogger(__name__)


MODE = "api"  # api or files

# paths for files mode
IN_DIR = Path("data/ipaws_alerts/json")
PATTERN = "IpawsArchivedAlerts_*.jsonl.xz"

# url for api mode
FEMA_API_URL = "https://www.fema.gov/api/open/v1/IpawsArchivedAlerts"


DATABASE_URL = "postgresql+psycopg://cap_alerts_app@localhost/cap_alerts"
# DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, echo=False)

console = Console()

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(console=console)]
)


progress_columns: list[ProgressColumn] = [
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    MofNCompleteColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
]


def has_cmas(alert: models.Alert) -> bool:
    """Detect if alert was distributed by CMAS.

    Args:
        alert (models.Alert): alert to check

    Returns:
        bool: False if alert has parameter BLOCKCHANNEL = CMAS, else True.
    """
    for info in alert.alert_info:
        for param in info.parameters:
            if param.value_name == "BLOCKCHANNEL" and param.value == "CMAS":
                return False
    return True


def load_from_file(file_path: Path, progress: Progress | None = None):
    with Session(engine) as session, lzma.open(file_path, "rt") as f_in:
        lines = f_in.read().splitlines()

        if progress:
            task_id = progress.add_task(description=f"Loading {file_path.name}…")
            lines = progress.track(lines, task_id=task_id)

        decoder = msgspec.json.Decoder()

        for line in lines:
            raw_xml: str = decoder.decode(line)["originalMessage"]
            root = etree.fromstring(raw_xml.encode())
            alert = extract_alert(root)

            # skip the non-CMAS alerts from NWS
            if alert.sender == "w-nws.webmaster@noaa.gov" and not has_cmas(alert):
                pass
            else:
                session.add(alert)

        session.commit()

        if progress:
            progress.update(task_id, visible=False)


def load_from_files(directory: Path, pattern: str, progress: Progress | None):
    files_sorted = sorted(directory.glob(pattern), reverse=True)

    if progress:
        task_id = progress.add_task("Loading files…")
        files_sorted = progress.track(files_sorted, task_id=task_id)

    for file_path in files_sorted:
        load_from_file(file_path, progress=progress)


def load_from_api(progress: Progress | None = None):

    with Session(engine) as session, httpx.Client(timeout=None) as client:
        if progress:
            task_id = progress.add_task("Loading records…")
            need_count = True
        else:
            need_count = False

        # Iterate until no more pages of results
        skip = 0
        while True:
            # Get page of results from API
            try:
                resp = client.get(
                    FEMA_API_URL,
                    params={"$skip": str(skip), "$top": 10_000, "$count": need_count},
                )
                resp.raise_for_status()

            except httpx.HTTPStatusError as e:
                console.log(f"ERROR {e.response.status_code}: {e.response.url}")
                raise

            # Decode json
            json_data = resp.json()

            if progress and need_count:
                progress.update(task_id, total=int(json_data["metadata"]["count"]))
                need_count = False

            # If no results were returned, we're done.
            if len(json_data["IpawsArchivedAlerts"]) == 0:
                break

            for alert_data in json_data["IpawsArchivedAlerts"]:
                raw_xml: str = alert_data["originalMessage"]
                root = etree.fromstring(raw_xml.encode())
                alert = extract_alert(root)

                # skip the non-CMAS alerts from NWS
                if alert.sender == "w-nws.webmaster@noaa.gov" and not has_cmas(alert):
                    pass
                else:
                    session.add(alert)

                if progress:
                    progress.update(task_id, advance=1)

            session.commit()


def main() -> None:
    console.log("START")

    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(engine)

    with Progress(*progress_columns, console=console) as progress:
        match MODE:
            case "files":
                load_from_files(IN_DIR, PATTERN, progress=progress)
            case "api":
                load_from_api(progress=progress)

    console.log("END")


if __name__ == "__main__":
    main()
