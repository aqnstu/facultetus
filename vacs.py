# coding: utf-8

"""
Все релевантные вакансии по выбранному ВУЗу.
"""

from requests import get
from time import time

from configs.facultetus import api_config
from misc.helpers import exit_on_fail, session, transform_list_to_str
from misc.log import logger
from misc.tables import FacultetusVac


@exit_on_fail("vacs.py")
def main():
    current_offset = 0
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
            if (
                not session.query(FacultetusVac)
                .filter(FacultetusVac.position_id == vac["position_id"])
                .one_or_none()
            ):
                vac["spheres"] = (
                    transform_list_to_str(vac["spheres"])
                    if vac.get("spheres")
                    else None
                )
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
        session.commit()

        current_offset += api_config["OFFSET"]


if __name__ == "__main__":
    start = time()
    main()
    end = time()
    time_spent = f"Total time spent: {end - start} sec"
    logger.getLogger("vacs.py").info(time_spent)
    print(f">> {time_spent}")
