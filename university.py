# coding: utf-8

"""
Все университеты.
"""

from requests import get
from time import time

from configs.facultetus import api_config
from misc.helpers import exit_on_fail, session
from misc.log import logger
from misc.tables import FacultetusUniversity


@exit_on_fail("university.py")
def main():
    current_offset = 0
    while True:
        print(f"> Page {int(current_offset / (api_config['OFFSET'] + 30))}...")
        response = get(
            url=f"https://facultetus.ru/api/{api_config['CLIENT_SECRET']}/getUniversities",
            headers={
                "Content-Type": "application/json; charset=UTF-8",
            },
            params={"offset": current_offset},
        )

        if not response.json().get("response"):
            break

        for university in response.json()["response"]:
            if (
                not session.query(FacultetusUniversity)
                .filter(
                    FacultetusUniversity.university_id == university["university_id"]
                )
                .one_or_none()
            ):
                session.add(FacultetusUniversity(**university))
        session.commit()

        # limit игнорируется, возвращается по 50 универов
        current_offset += api_config["OFFSET"] + 30


if __name__ == "__main__":
    start = time()
    main()
    end = time()
    time_spent = f"Total time spent: {end - start} sec"
    logger.getLogger("university.py").info(time_spent)
    print(f">> {time_spent} sec")
