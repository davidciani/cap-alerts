from sqlmodel import Session, create_engine, select

from cap_alerts.models import Alert

DATABASE_URL = "postgresql+psycopg://cap_alerts_app@localhost/cap_alerts_dev"
engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"options": "-c timezone=utc"}
)


def select_alert():
    with Session(engine) as session:
        statement = select(Alert)
        results = session.exec(statement)

        alerts = results.fetchmany(10)

        for alert in alerts:
            print(alert)
            # print(alert.model_dump_json(indent=2))


def main():
    select_alert()


if __name__ == "__main__":
    main()
