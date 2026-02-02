# coding: utf-8
"""
Все релевантные вакансии по выбранному ВУЗу. Independent version.
"""
import os
import sys
import copy
import logging
from datetime import datetime, timedelta
from time import time
from requests import get
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, ForeignKey, Integer, TIMESTAMP, VARCHAR, text, DateTime, and_, or_
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load configuration from .env
load_dotenv()

# --- Configuration ---
UNIVERSITY_ID = os.getenv("UNIVERSITY_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
OFFSET = int(os.getenv("FACULTETUS_OFFSET", "20"))

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

    logger = logging.getLogger("vacs_single.py")
    logger.setLevel(logging.INFO)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    return logger

logger = setup_logging()

# --- Database Models ---
Base = declarative_base()

class FacultetusVac(Base):
    __tablename__ = "facultetus_vac"
    __table_args__ = {"schema": "apiuser"}
    position_id = Column(Integer, primary_key=True)
    employer_id = Column(Integer)
    employer_title = Column(VARCHAR(250))
    employer_slogan = Column(VARCHAR(200))
    employer_logo = Column(VARCHAR(150))
    employer_type = Column(VARCHAR(300))
    title = Column(VARCHAR(300))
    type = Column(VARCHAR(20))
    lookingfor = Column(VARCHAR(200))
    region = Column(VARCHAR(50))
    city = Column(VARCHAR(30))
    address = Column(VARCHAR(200))
    background_pic = Column(VARCHAR(150))
    description = Column(VARCHAR(500))
    requirements = Column(VARCHAR(300))
    cond = Column(VARCHAR(200))
    edu_trial_accept = Column(VARCHAR(1))
    tempjob = Column(VARCHAR(1))
    forinternationals = Column(VARCHAR(1))
    fornewbies = Column(VARCHAR(1))
    fordisabled = Column(VARCHAR(1))
    remoted = Column(VARCHAR(1))
    edu_combo_friendly = Column(VARCHAR(1))
    first_year_friendly = Column(VARCHAR(1))
    for_graduates = Column(VARCHAR(1))
    instant_paid = Column(VARCHAR(1))
    cash_from = Column(Integer)
    cash_to = Column(Integer)
    is_actual = Column(VARCHAR(1))
    position_link = Column(VARCHAR(150))
    spheres = Column(VARCHAR(200))
    langs = Column(VARCHAR(200))
    skills = Column(VARCHAR(200))
    tests = Column(VARCHAR(300))
    professions = Column(VARCHAR(300))
    date_added = Column(TIMESTAMP, server_default=text("sysdate"))
    date_updated = Column(TIMESTAMP)
    date_deleted = Column(TIMESTAMP)

class FacultetusSphere(Base):
    __tablename__ = "facultetus_sphere"
    __table_args__ = {"schema": "apiuser"}
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(150), nullable=False)
    date_added = Column(TIMESTAMP, nullable=False, server_default=text("sysdate "))

class FacultetusEmployerSphere(Base):
    __tablename__ = "facultetus_employer_sphere"
    __table_args__ = {"schema": "apiuser"}
    id = Column(Integer, primary_key=True)
    employer_id = Column(Integer)
    sphere_id = Column(ForeignKey("apiuser.facultetus_sphere.id"))
    date_added = Column(TIMESTAMP, nullable=False, server_default=text("sysdate "))
    sphere = relationship("FacultetusSphere")

class FacultetusVacSphere(Base):
    __tablename__ = "facultetus_vac_sphere"
    __table_args__ = {"schema": "apiuser"}
    id = Column(Integer, primary_key=True)
    position_id = Column(VARCHAR(100))
    sphere_id = Column(ForeignKey("apiuser.facultetus_sphere.id"))
    date_added = Column(TIMESTAMP, nullable=False, server_default=text("sysdate "))

class FacultetusVacLog(Base):
    __tablename__ = "facultetus_vac_log"
    __table_args__ = {"schema": "apiuser"}
    id = Column(Integer, primary_key=True)
    added = Column(Integer)
    updated = Column(Integer)
    deleted = Column(Integer)
    successfully = Column(Integer)
    date_added = Column(TIMESTAMP, nullable=False, server_default=text("sysdate "))

# --- Database Connection ---
try:
    engine = create_engine(DB_URL, echo=False)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
except Exception as e:
    logger.error(f"Failed to initialize database session: {e}")
    sys.exit(1)

# --- Helper Functions ---
def transform_list_to_str(elems: list, delimeter: str = ";") -> str:
    return delimeter.join([elem["data"] for elem in elems])

# --- Main Logic ---
def main():
    logger.info("Update spheres...")
    response = get(
        url=f"https://facultetus.ru/api/{CLIENT_SECRET}/getlib",
        headers={"Content-Type": "application/json; charset=UTF-8"},
        params={"lib": "spheres"}
    )

    resp_json = response.json()
    if not resp_json.get("spheres"):
        logger.info("No spheres found in response")
    else:
        for sp in resp_json['spheres']:
            if not session.query(FacultetusSphere).filter(FacultetusSphere.name == sp).one_or_none():
                session.add(FacultetusSphere(name=sp))
        session.commit()

    spheres_list = [sphere.__dict__ for sphere in session.query(FacultetusSphere).all()]
    spheres_dict = {sphere['name']: sphere['id'] for sphere in spheres_list}
    
    current_offset = 0
    vacs_added, vacs_updated, vacs_droped = 0, 0, 0
    date_updated = datetime.now()
    
    logger.info("Update vacs...")
    while True:
        logger.info(f"> Page {int(current_offset / OFFSET)}...")
        response = get(
            url=f"https://facultetus.ru/api/{CLIENT_ID}/getPositions",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            params={
                "university_id": UNIVERSITY_ID,
                "offset": current_offset
            },
        )

        resp_json = response.json()
        if not resp_json.get("response"):
            break

        for vac in resp_json["response"]:
            for field in ("spheres", "langs", "skills", "tests", "professions"):
                vac[field] = transform_list_to_str(vac[field]) if vac.get(field) else None

            for field in ("cash_from", "cash_to"):
                vac[field] = int(vac[field]) if vac.get(field) else None

            for field in ("description", "requirements", "cond"):
                if isinstance(vac.get(field), str):
                    if len(vac[field]) > 4000:
                        vac[field] = vac[field][:3997] + '...'

            allowed_keys = FacultetusVac.__table__.columns.keys()
            vac_data = {k: v for k, v in vac.items() if k in allowed_keys}

            if not session.query(FacultetusVac).filter(FacultetusVac.position_id == vac["position_id"]).one_or_none():
                vacs_added += 1
                session.add(FacultetusVac(**vac_data))
            else:
                vac_copy = copy.deepcopy(vac_data)
                del vac_copy["position_id"]
                vac_copy["date_updated"] = date_updated
                session.query(FacultetusVac).filter(FacultetusVac.position_id == vac["position_id"]).update(vac_copy)
                vacs_updated += 1
            session.commit()

            spheres = vac.get("spheres") or ''
            for sphere in spheres.split(";"):
                sphere_clean = sphere.strip()
                if sphere_clean:
                    s_id = spheres_dict.get(sphere_clean)
                    if s_id:
                        if not session.query(FacultetusEmployerSphere).filter(
                            and_(FacultetusEmployerSphere.employer_id == vac["employer_id"], FacultetusEmployerSphere.sphere_id == s_id)
                        ).one_or_none():
                            session.add(FacultetusEmployerSphere(employer_id=vac["employer_id"], sphere_id=s_id))
                            session.commit()

                        if not session.query(FacultetusVacSphere).filter(
                            and_(FacultetusVacSphere.position_id == vac["position_id"], FacultetusVacSphere.sphere_id == s_id)
                        ).one_or_none():
                            session.add(FacultetusVacSphere(position_id=vac["position_id"], sphere_id=s_id))
                            session.commit()

        current_offset += OFFSET

    logger.info("Update employers (refreshing materialized view)...")
    try:
        session.execute(text("BEGIN DBMS_SNAPSHOT.REFRESH('apiuser.mv_facultetus_employer'); END;"))
        session.commit()
    except Exception as e:
        logger.warning(f"Failed to refresh materialized view: {e}")

    vac_hours_delta = 2
    logger.info("Mark actual and outdated vacancies...")
    session.query(FacultetusVac).filter(
        and_(FacultetusVac.date_added.isnot(None), FacultetusVac.date_updated > datetime.now() - timedelta(hours=vac_hours_delta))
    ).update({"date_deleted": None})
    session.commit()

    vacs_droped = session.query(FacultetusVac).filter(
        or_(
            and_(FacultetusVac.date_added <= datetime.now() - timedelta(hours=vac_hours_delta), FacultetusVac.date_updated.is_(None)),
            and_(FacultetusVac.date_added.isnot(None), FacultetusVac.date_updated <= datetime.now() - timedelta(hours=vac_hours_delta))
        )
    ).update({"date_deleted": datetime.now()})
    session.commit()

    logger.info("Log upload completion...")
    session.add(FacultetusVacLog(added=vacs_added, updated=vacs_updated, deleted=vacs_droped, successfully=1))
    session.commit()

if __name__ == "__main__":
    start_time = time()
    try:
        main()
    except Exception as e:
        session.rollback()
        logger.error("Exception occurred", exc_info=True)
        session.add(FacultetusVacLog(successfully=0))
        session.commit()
    finally:
        time_spent = f"Total time spent: {time() - start_time:.2f} sec"
        logger.info(time_spent)
