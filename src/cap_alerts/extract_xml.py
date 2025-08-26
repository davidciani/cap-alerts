import lzma
import re
from itertools import groupby
from pathlib import Path

import msgspec.json
from rich.console import Console

console = Console()


def file_year(file_path: Path) -> str:
    if m := re.search(r"\d{4}", str(file_path.name)):
        year = m.group(0)
        return year
    else:
        raise ValueError("File path doesn't contain a year.")


def main():
    console.log("START")

    files = list(Path("data/").glob("IpawsArchivedAlerts_*.jsonl.xz"))

    files = sorted(files, key=file_year)

    decoder = msgspec.json.Decoder()
    for k, g in groupby(files, file_year):
        console.log(f"Processing {k}")

        lines = []
        for segment_path in g:
            with lzma.open(segment_path, "rb") as f_in:
                lines.extend(f_in.read().splitlines())

        with lzma.open(Path(f"data/IpawsArchivedAlerts_{k}.xml.xz"), "wt") as f_out:
            f_out.write("<alerts>\n")
            for n, line in enumerate(lines):
                raw_xml: str = decoder.decode(line)["originalMessage"]
                f_out.write(raw_xml + "\n")
            f_out.write("</alerts>\n")

    console.log("END")


if __name__ == "__main__":
    main()
