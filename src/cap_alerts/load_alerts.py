"""load_alerts.py -- extract alerts from jsonl and load to database."""

import logging
import lzma
from concurrent.futures import Future
from pathlib import Path
from typing import TYPE_CHECKING, Any

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
    from multiprocessing.managers import DictProxy

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
_progress: DictProxy[Any, Any]


def print_result(future: Future) -> None:
    """If the task resulted in an exception, print it.

    Args:
        future (Future): task result
    """
    if e := future.exception():
        console.log(e)


def init_worker(progress: DictProxy[Any, Any]) -> None:
    """Initalize worker process.

    Args:
        progress (dict): handle for progress bar to update
    """
    global session, _progress
    engine = create_engine(DATABASE_URL, echo=True)

    session = Session(engine)

    _progress = progress


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


def process_file(task_id: int, file_path: Path) -> None:
    """Process a jsonl file, extract alert xml, and insert into database.

    Args:
        task_id (int): task id for progress bar
        file_path (Path): jsonl file with alert records
    """
    with lzma.open(file_path, "rt") as f_in:
        lines = f_in.read().splitlines()
    len_of_task = len(lines)

    decoder = msgspec.json.Decoder()
    for n, line in enumerate(lines):
        raw_xml: str = decoder.decode(line)["originalMessage"]
        root = etree.fromstring(raw_xml.encode())
        alert = extract_alert(root)

        # skip the non-CMAS alerts from NWS
        if alert.sender == "w-nws.webmaster@noaa.gov" and not has_cmas(alert):
            _progress[task_id] = {"progress": n + 1, "total": len_of_task}
            continue

        session.add(alert)

        _progress[task_id] = {"progress": n + 1, "total": len_of_task}


def main() -> None:
    """Kick off multi-process ETL job."""
    console.log("START")

    engine = create_engine(DATABASE_URL, echo=False)

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
            with lzma.open(file_path, "rt") as f_in:
                lines = f_in.read().splitlines()

            task_id = progress.add_task(f"Loading {file_path.name}…", total=len(lines))

            decoder = msgspec.json.Decoder()
            for line in lines:
                raw_xml: str = decoder.decode(line)["originalMessage"]
                root = etree.fromstring(raw_xml.encode())
                alert = extract_alert(root)

                # skip the non-CMAS alerts from NWS
                if alert.sender == "w-nws.webmaster@noaa.gov" and not has_cmas(alert):
                    progress.update(task_id, advance=1)
                    continue

                session.add(alert)

                progress.update(task_id, advance=1)

            session.commit()
            progress.update(task_id, visible=False)
            progress.update(overall_progress_task, advance=1)

    console.log("END")


if __name__ == "__main__":
    main()
