# coding: utf-8

"""
Все сферы.
"""

from requests import get
from time import time

from configs.facultetus import api_config
from misc.helpers import exit_on_fail, session
from misc.log import logger
from misc.tables import FacultetusSphere


@exit_on_fail("spheres.py")
def main():
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


if __name__ == "__main__":
    start = time()
    main()
    end = time()
    time_spent = f"Total time spent: {end - start} sec"
    logger.getLogger("spheres.py").info(time_spent)
    print(f">> {time_spent} sec")
