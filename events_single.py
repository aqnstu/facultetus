# coding: utf-8
"""
Все мероприятия из выбранных ВУЗов. Independent version.
"""
import os
import sys
import logging
from datetime import datetime
from functools import wraps
from time import time
from requests import get
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, ForeignKey, Integer, TIMESTAMP, VARCHAR, text, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load configuration from .env
load_dotenv()

# --- Configuration ---
CLIENT_ID = os.getenv("CLIENT_ID")
LIMIT = int(os.getenv("FACULTETUS_LIMIT", 80))
OFFSET = int(os.getenv("FACULTETUS_OFFSET", 20))

DB_URL = "{DB_TYPE}+{DB_DRIVER}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}".format(
    DB_TYPE=os.getenv("DB_TYPE"),
    DB_DRIVER=os.getenv("DB_DRIVER"),
    DB_USERNAME=os.getenv("DB_USERNAME"),
    DB_PASSWORD=os.getenv("DB_PASSWORD"),
    DB_HOST=os.getenv("DB_HOST"),
    DB_PORT=os.getenv("DB_PORT"),
    DB_NAME=os.getenv("DB_NAME")
)

# --- Logging Setup ---
class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.ERROR

def setup_logging():
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s -- %(name)s.%(funcName)s, %(lineno)d: %(message)s",
        datefmt="%Y-%m-%d, %H:%M:%S"
    )

    # Stdout handler (INFO and below ERROR)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(InfoFilter())

    # Stderr handler (ERROR and above)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    stderr_handler.setLevel(logging.ERROR)

    logger = logging.getLogger("events_single.py")
    logger.setLevel(logging.INFO)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    return logger

logger = setup_logging()

# --- Database Models ---
Base = declarative_base()

class FacultetusActivityType(Base):
    __tablename__ = "facultetus_activity_type"
    __table_args__ = {"schema": "apiuser"}
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(100))
    date_added = Column(TIMESTAMP, server_default=text("sysdate"))
    name_ru = Column(VARCHAR(100))

class FacultetusActivity(Base):
    __tablename__ = "facultetus_activity"
    __table_args__ = {"schema": "apiuser"}
    id = Column(VARCHAR(10), primary_key=True)
    created = Column(TIMESTAMP)
    cprofile_id = Column(VARCHAR(10))
    type = Column(VARCHAR(30))
    type_text = Column(VARCHAR(30))
    published = Column(VARCHAR(1))
    students_moderation = Column(VARCHAR(1))
    students_reg = Column(VARCHAR(1))
    cprofiles_moderation = Column(VARCHAR(1))
    leader_event_id = Column(VARCHAR(10))
    timepad_event_id = Column(VARCHAR(10))
    university_id = Column(VARCHAR(10))
    fair_id = Column(VARCHAR(10))
    title = Column(VARCHAR(500))
    slogan = Column(VARCHAR(350))
    description = Column(VARCHAR(4000))
    background_pic = Column(VARCHAR(150))
    date_start = Column(DateTime)
    time_start = Column(TIMESTAMP)
    date_end = Column(DateTime)
    time_end = Column(TIMESTAMP)
    timezone = Column(VARCHAR(10))
    require_leader_auth = Column(VARCHAR(1))
    require_rsv_auth = Column(VARCHAR(1))
    region = Column(VARCHAR(150))
    city = Column(VARCHAR(100))
    address = Column(VARCHAR(250))
    online = Column(VARCHAR(1), name="online", quote=True)
    external_link = Column(VARCHAR(500))
    author_title = Column(VARCHAR(100))
    author_logo = Column(VARCHAR(150))
    date_added = Column(TIMESTAMP, server_default=text("sysdate"))
    participants_limitation = Column(VARCHAR(1000))
    vc_event_id = Column(VARCHAR(10))
    poll_id = Column(Integer)
    youtube_id = Column(Integer)
    my_rater = Column(VARCHAR(1))
    activity_link = Column(VARCHAR(500))
    local_datetime = Column(TIMESTAMP)
    local_datetime_end = Column(TIMESTAMP)
    students_q = Column(Integer)
    link_token = Column(VARCHAR(250))
    is_public = Column(VARCHAR(1))
    skip_auth = Column(VARCHAR(1))
    group_id = Column(VARCHAR(10))
    photo_payload = Column(VARCHAR(1000))
    type_id = Column(ForeignKey("apiuser.facultetus_activity_type.id"))
    date_sorter = Column(TIMESTAMP)
    one_day_priority = Column(Integer)
    type1 = relationship("FacultetusActivityType")

class FacultetusUniversity(Base):
    __tablename__ = "facultetus_university"
    __table_args__ = {"schema": "apiuser"}
    university_id = Column(Integer, primary_key=True)
    title = Column(VARCHAR(200))

# --- Database Connection ---
try:
    engine = create_engine(DB_URL, echo=False)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
except Exception as e:
    logger.error(f"Failed to initialize database session: {e}")
    sys.exit(1)

# --- Helper Functions ---
def exit_on_fail(log_module: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                session.rollback()
                error_text = "Exception occurred in " + log_module
                logger.error(error_text, exc_info=True)
                sys.exit(1)
        return wrapper
    return decorator

def str_to_datetaime(s: str, formats):
    if not s:
        return None
    if isinstance(formats, str):
        formats = [formats]
    dt = None
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
        except Exception:
            pass
        if dt:
            break
    return dt

# --- Main Logic ---
@exit_on_fail("events_single.py")
def main():
    university_ids_raw = session.query(FacultetusUniversity.university_id).all()
    university_ids = [elem for tup in university_ids_raw for elem in tup]

    types_list = [type.__dict__ for type in session.query(FacultetusActivityType).all()]
    types_dict = {sphere['name']: sphere['id'] for sphere in types_list}
    logger.info(f"Existing activity types: {types_dict}")

    for university_id in university_ids:
        logger.info(f"> University ID: {university_id}...")
        current_offset = 0
        while True:
            response = get(
                url=f"https://facultetus.ru/api/{CLIENT_ID}/getActivities",
                headers={"Content-Type": "application/json; charset=UTF-8"},
                params={
                    "university_id": university_id,
                    "offset": current_offset,
                    "limit": LIMIT,
                },
            )

            resp_json = response.json()
            if not resp_json.get("response"):
                logger.info("No data found")
                break
            else:
                logger.info(f">> Page {int(current_offset / OFFSET)}...")

            for event in resp_json["response"]:
                if (
                    not session.query(FacultetusActivity)
                    .filter(FacultetusActivity.id == event["id"])
                    .one_or_none()
                ):
                    event["created"] = str_to_datetaime(event.get("created"), ["%Y-%m-%d %H:%M:%S"])
                    event["date_start"] = str_to_datetaime(event.get("date_start"), ["%Y-%m-%d"])
                    event["time_start"] = str_to_datetaime(event.get("time_start"), ["%H:%M:%S"])
                    event["date_end"] = str_to_datetaime(event.get("date_end"), ["%Y-%m-%d"])
                    event["time_end"] = str_to_datetaime(event.get("time_end"), ["%H:%M:%S"])
                    event["local_datetime"] = str_to_datetaime(
                        event.get("local_datetime"), ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
                    )
                    event["local_datetime_end"] = str_to_datetaime(
                        event.get("local_datetime_end"), "%Y-%m-%d %H:%M:%S"
                    )
                    event["photo_payload"] = ",".join(event.get("photo_payload") or []) \
                        if event.get("photo_payload") else None
                    event["date_sorter"] = str_to_datetaime(
                        event.get("date_sorter"), "%Y-%m-%d %H:%M:%S"
                    )

                    if (
                        not session.query(FacultetusActivityType)
                        .filter(FacultetusActivityType.name == event["type"])
                        .one_or_none()
                    ):
                        new_id = (max(types_dict.values()) + 1) if types_dict else 1
                        types_dict[event["type"]] = new_id
                        session.add(FacultetusActivityType(name=event["type"]))
                        session.flush()

                    event["type_id"] = types_dict.get(event["type"])

                    allowed_keys = FacultetusActivity.__table__.columns.keys()
                    event_data = {k: v for k, v in event.items() if k in allowed_keys}
                    session.add(FacultetusActivity(**event_data))
            session.commit()
            current_offset += OFFSET

if __name__ == "__main__":
    start_time = time()
    main()
    time_spent = f"Total time spent: {time() - start_time:.2f} sec"
    logger.info(time_spent)
