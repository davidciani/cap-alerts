import lzma
from datetime import date, datetime
from pathlib import Path

import httpx
from dateutil.relativedelta import relativedelta
from dateutil.rrule import YEARLY, rrule

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_DIR = Path("data")

SIZE = 10_000
SKIP = 0

LIMIT = None

FROM_DATE = date(2016, 1, 1)
TO_DATE = date(2025, 12, 31)

# 2017-03-01 to 2017-04-30
# 2022-10-01

BASE_URL = "https://www.fema.gov/api/open/v1/IpawsArchivedAlerts?"


def get_alerts(client: httpx.Client, url: str, out_path: Path) -> None:
    try:
        resp = client.get(url)
        resp.raise_for_status()

    except httpx.HTTPStatusError as e:
        print(f"ERROR {e.response.status_code}: {e.response.url}")
        print(e.response.text)
        raise e

    outpath_xz = out_path.with_suffix(out_path.suffix + ".xz")
    with lzma.open(outpath_xz, "wb") as out_file:
        out_file.write(resp.text.encode("utf-8"))


def get_alert_count(
    client: httpx.Client, base_url: str, date_from: date, date_to: date
) -> int:
    url = (
        base_url
        + f"$filter=sent ge '{date_from.isoformat()}' and sent le '{date_to.isoformat()}'"
    )

    try:
        resp = client.get(url + "&$count=true&$select=id&$top=1")
        resp.raise_for_status()

    except httpx.HTTPStatusError as e:
        print(f"ERROR {e.response.status_code}: {e.response.url}")
        print(e.response.text)
        raise e

    json_data = resp.json()
    return int(json_data["metadata"]["count"])


def main():
    print(f"START {str(datetime.now())}")

    with httpx.Client(timeout=None) as client:
        for date_from in rrule(
            freq=YEARLY,
            dtstart=FROM_DATE,
            byyearday=1,
            until=TO_DATE,
        ):
            date_to = date_from + relativedelta(
                month=12, day=31, hour=23, minute=59, second=59
            )

            print(f"BATCH {str(date_from)} -- {str(date_to)}")
            record_count = get_alert_count(
                client,
                BASE_URL,
                date_from,
                date_to,
            )

            print(f"      RECORD COUNT: {record_count:,}")

            skip = 0
            i = 1
            while record_count > 0:
                to_request = min(100000, record_count)

                params = (
                    f"$filter=sent ge '{date_from.isoformat()}' and sent le '{date_to.isoformat()}'"
                    + f"&$metadata=off&$format=jsonl&$skip={str(skip)}&$top={str(to_request)}"
                )

                url = BASE_URL + params

                out_path = Path(
                    OUT_DIR,
                    f"IpawsArchivedAlerts_{date_from:%Y}_{i:03d}.jsonl",
                )

                get_alerts(client, url, out_path)

                print(
                    f"      {i:03d} "
                    + f"REQUEST {to_request:,} "
                    + f"SKIP {skip:,} "
                    + f"REMAINING {record_count - to_request:,} "
                    + f"OUT {out_path.name}\n"
                    + f"      {params}"
                )

                record_count = record_count - to_request
                skip = skip + to_request
                i = i + 1

            print()

    print(f"END {str(datetime.now())}")


if __name__ == "__main__":
    main()

# 4850417
