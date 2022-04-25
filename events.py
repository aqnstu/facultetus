# coding: utf-8

"""
Все мероприятия из выбранныз ВУЗов.
"""

from requests import get
from time import time

from configs.facultetus import api_config
from misc.helpers import exit_on_fail, session, str_to_datetaime
from misc.log import logger
from misc.tables import FacultetusActivity, FacultetusActivityType, FacultetusUniversity

university_ids_raw = session.query(FacultetusUniversity.university_id).all()
university_ids = [elem for tup in university_ids_raw for elem in tup]


@exit_on_fail("events.py")
def main():
    types_list = [type.__dict__ for type in session.query(FacultetusActivityType).all()]
    types_dict = {sphere['name']: sphere['id'] for sphere in types_list}
    print(types_dict)

    for university_id in university_ids:
        print(f"> University ID: {university_id}...")
        current_offset = 0
        while True:
            response = get(
                url=f"https://facultetus.ru/api/{api_config['CLIENT_ID']}/getActivities",
                headers={
                    "Content-Type": "application/json; charset=UTF-8",
                },
                params={
                    "university_id": university_id,
                    "offset": current_offset,
                    "limit": api_config["LIMIT"],
                },
            )

            if not response.json().get("response"):
                print("No data found")
                break
            else:
                print(f">> Page {int(current_offset / api_config['OFFSET'])}...")

            for event in response.json()["response"]:
                if (
                    not session.query(FacultetusActivity)
                    .filter(FacultetusActivity.id == event["id"])
                    .one_or_none()
                ):
                    event["created"] = str_to_datetaime(
                        event.get("created"), ["%Y-%m-%d %H:%M:%S"]
                    )
                    event["date_start"] = str_to_datetaime(
                        event.get("date_start"), ["%Y-%m-%d"]
                    )
                    event["time_start"] = str_to_datetaime(
                        event.get("time_start"), ["%H:%M:%S"]
                    )
                    event["date_end"] = str_to_datetaime(
                        event.get("date_end"), ["%Y-%m-%d"]
                    )
                    event["time_end"] = str_to_datetaime(
                        event.get("time_end"), ["%H:%M:%S"]
                    )
                    event["local_datetime"] = str_to_datetaime(
                        event.get("local_datetime"), ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
                    )
                    event["local_datetime_end"] = str_to_datetaime(
                        event.get("local_datetime_end"), "%Y-%m-%d %H:%M:%S"
                    )
                    event["photo_payload"] = ",".join(event.get("photo_payload") or []) \
                        if not event.get("photo_payload") else None
                    event["date_sorter"] = str_to_datetaime(
                        event.get("date_sorter"), "%Y-%m-%d %H:%M:%S"
                    )

                    if (
                        not session.query(FacultetusActivityType)
                        .filter(FacultetusActivityType.name == event["type"])
                        .one_or_none()
                    ):
                        types_dict[event["type"]] = max(types_dict.values()) + 1
                        session.add(FacultetusActivityType(name=event["type"]))

                    event["type_id"] = types_dict.get(event["type"])

                    session.add(FacultetusActivity(**event))
            session.commit()

            current_offset += api_config["OFFSET"]


if __name__ == "__main__":
    start = time()
    main()
    end = time()
    time_spent = f"Total time spent: {end - start} sec"
    logger.getLogger("events.py").info(time_spent)
    print(f">>> {time_spent} sec")
