import logging
import lzma
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

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
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from cap_alerts import models  # noqa: F401
from cap_alerts.db import Base
from cap_alerts.util import formatTime

logger = logging.getLogger(__name__)


IN_DIR = Path("data/json")
FILES = list(IN_DIR.glob("IpawsArchivedAlerts_*.jsonl.xz"))

logging.Formatter.formatTime = formatTime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
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


session: sessionmaker[Session]


def insert_alert(raw_xml: str):
    try:
        root = etree.fromstring(raw_xml.encode())
        alert = models.Alert.from_element(root)
    except ValueError as e:
        raise e

    with session() as s:
        with s.begin():
            s.add(alert)


def print_result(future):
    pass
    if e := future.exception():
        console.log(e)


def init_worker(progress):
    global session, _progress
    engine = create_engine(
        "postgresql+psycopg://cap_alerts_app@localhost/cap_alerts", echo=False
    )

    session = sessionmaker(engine)
    _progress = progress


def process_file(task_id: int, file_path: Path):
    with lzma.open(file_path,"rt") as f_in:
        lines = f_in.read().splitlines()
    len_of_task = len(lines)

    decoder = msgspec.json.Decoder()
    for n, line in enumerate(lines):
        raw_xml: str = decoder.decode(line)["originalMessage"]
        insert_alert(raw_xml)
        _progress[task_id] = {"progress": n + 1, "total": len_of_task}


def main():
    console.log("START")

    engine = create_engine(
        "postgresql+psycopg://cap_alerts_app@localhost/cap_alerts", echo=False
    )

    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Progress(*progress_columns, console=console) as progress:
        futures = []
        with multiprocessing.Manager() as manager:
            _progress = manager.dict()

            files = FILES
            overall_progress_task = progress.add_task(
                "Loading files…", total=len(files)
            )

            with ProcessPoolExecutor(
                initializer=init_worker, initargs=(_progress,)
            ) as executor:
                for file_path in list(sorted(files)):
                    task_id = progress.add_task(
                        f"Loading {file_path.name}…", visible=False
                    )
                    future = executor.submit(process_file, task_id, file_path)
                    future.add_done_callback(print_result)
                    futures.append(future)

                while (n_finished := sum([future.done() for future in futures])) < len(
                    futures
                ):
                    progress.update(
                        overall_progress_task, completed=n_finished, total=len(futures)
                    )
                    for task_id, update_data in _progress.items():
                        latest = update_data["progress"]
                        total = update_data["total"]
                        # update the progress bar for this task:
                        progress.update(
                            task_id,
                            completed=latest,
                            total=total,
                            visible=latest < total,
                        )

                # raise any errors:
                for future in futures:
                    future.result()

    console.log("END")


if __name__ == "__main__":
    main()

# 4850417
