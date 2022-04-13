# coding: utf-8

"""
Все релевантные вакансии по выбранному ВУЗу.
"""

import copy
from requests import get
from sqlalchemy import and_
from time import time

from configs.facultetus import api_config
from misc.helpers import exit_on_fail, session, transform_list_to_str
from misc.log import logger
from misc.tables import FacultetusEmployerSphere, FacultetusSphere, \
    FacultetusVac, FacultetusVacSphere


@exit_on_fail("vacs.py")
def main():
    print("Update spheres...")
    response = get(
        url=f"https://facultetus.ru/api/{api_config['CLIENT_SECRET']}/getlib",
        headers={
            "Content-Type": "application/json; charset=UTF-8",
        },
        params={"lib": "spheres"}
    )

    if not response.json().get("spheres"):
        return

    for sp in response.json()['spheres']:
        if (
            not session.query(FacultetusSphere)
            .filter(FacultetusSphere.name == sp)
            .one_or_none()
        ):
            session.add(FacultetusSphere(name=sp))
    session.commit()

    spheres_list = [sphere.__dict__ for sphere in session.query(FacultetusSphere).all()]
    spheres_dict = {sphere['name']: sphere['id'] for sphere in spheres_list}
    current_offset = 0
    print("Update vacs...")
    while True:
        print(f"> Page {int(current_offset / api_config['OFFSET'])}...")
        response = get(
            url=f"https://facultetus.ru/api/{api_config['CLIENT_ID']}/getPositions",
            headers={
                "Content-Type": "application/json; charset=UTF-8",
            },
            params={
                "university_id": api_config["UNIVERSITY_ID"],
                "offset": current_offset,
            },
        )

        if response.json()["response"] == []:
            break

        for vac in response.json()["response"]:
            vac["spheres"] = (
                transform_list_to_str(vac["spheres"])
                if vac.get("spheres")
                else None
            )

            if (
                not session.query(FacultetusVac)
                .filter(FacultetusVac.position_id == vac["position_id"])
                .one_or_none()
            ):
                vac["langs"] = (
                    transform_list_to_str(vac["langs"]) if vac.get("langs") else None
                )
                vac["skills"] = (
                    transform_list_to_str(vac["skills"]) if vac.get("skills") else None
                )
                vac["tests"] = (
                    transform_list_to_str(vac["tests"]) if vac.get("tests") else None
                )
                vac["professions"] = (
                    transform_list_to_str(vac["professions"])
                    if vac.get("professions")
                    else None
                )
                vac["cash_from"] = int(vac["cash_from"]) if vac["cash_from"] else None
                vac["cash_to"] = int(vac["cash_to"]) if vac["cash_to"] else None
                session.add(FacultetusVac(**vac)) 
            else:
                vac_copy = copy.deepcopy(vac)
                del vac_copy["position_id"]
                session.query(FacultetusVac) \
                    .filter(FacultetusVac.position_id == vac["position_id"]) \
                    .update(vac_copy)
            session.commit()

            spheres = vac["spheres"] or ''
            for sphere in spheres.split(";"):
                sphere_clean = sphere.strip()
                if sphere_clean:
                    if (
                        not session.query(
                            FacultetusEmployerSphere
                        ).filter(
                            and_(
                                FacultetusEmployerSphere.employer_id == vac["employer_id"],
                                FacultetusEmployerSphere.sphere_id == spheres_dict.get(sphere_clean, '')
                            )
                        ).one_or_none()
                    ):
                        session.add(
                            FacultetusEmployerSphere(
                                employer_id=vac["employer_id"],
                                sphere_id=spheres_dict.get(sphere_clean, '')
                            )
                        )
                        session.commit()

                    if (
                        not session.query(
                            FacultetusVacSphere
                        ).filter(
                            and_(
                                FacultetusVacSphere.position_id == vac["position_id"],
                                FacultetusVacSphere.sphere_id == spheres_dict.get(sphere_clean, '')
                            )
                        ).one_or_none()
                    ):
                        session.add(
                            FacultetusVacSphere(
                                position_id=vac["position_id"],
                                sphere_id=spheres_dict.get(sphere_clean, '')
                            )
                        )
                        session.commit()

        current_offset += api_config["OFFSET"]

    print("Update employers...\n")
    session.execute("""
        BEGIN
            DBMS_SNAPSHOT.REFRESH('apiuser.mv_facultetus_employer');
        END;
    """)


if __name__ == "__main__":
    start = time()
    main()
    end = time()
    time_spent = f"Total time spent: {end - start} sec"
    logger.getLogger("vacs.py").info(time_spent)
    print(f">> {time_spent}")
