"""load_alerts.py -- extract alerts from jsonl and load to database."""

import logging
import lzma
from pathlib import Path
from typing import TYPE_CHECKING

import msgspec.json
from lxml import etree
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
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


IN_DIR = Path("data/ipaws_alerts/json")
FILES = list(IN_DIR.glob("IpawsArchivedAlerts_*.jsonl.xz"))

DATABASE_URL = "postgresql+psycopg://cap_alerts_app@localhost/cap_alerts_dev"
# DATABASE_URL = "sqlite:///:memory:"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

console = Console()

progress_columns = [
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    MofNCompleteColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
]


session: Session


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


engine = create_engine(DATABASE_URL, echo=False)


def main() -> None:
    console.log("START")

    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(engine)

    session = Session(engine)

    with Progress(*progress_columns, console=console) as progress:
        files = sorted(FILES, reverse=True)
        overall_progress_task = progress.add_task(
            "Loading files…",
            total=len(files),
        )

        for file_path in sorted(files):
            load_from_file(file_path, progress=progress)
            progress.update(overall_progress_task, advance=1)

    console.log("END")


if __name__ == "__main__":
    main()
