# coding: utf-8

"""
Все мероприятия из выбранныз ВУЗов.
"""

from requests import get
from time import time

from configs.facultetus import api_config
from misc.helpers import exit_on_fail, session, str_to_datetaime
from misc.log import logger
from misc.tables import FacultetusActivity

university_ids = [6, 13, 119]


@exit_on_fail('events.py')
def main():
    for university_id in university_ids:
        print(f'> University ID: {university_id}...')
        current_offset = 0
        while True:
            print(f">> Page {int(current_offset / api_config['OFFSET'])}...")
            response = get(
                url=f"https://facultetus.ru/api/{api_config['CLIENT_ID']}/getActivities",
                headers={
                    "Content-Type": "application/json; charset=UTF-8",
                },
                params={
                    'university_id': university_id,
                    'offset': current_offset,
                    'limit': api_config['LIMIT']
                }
            )

            if not response.json().get('response'):
                break

            for event in response.json()['response']:
                if not session.query(FacultetusActivity).filter(
                    FacultetusActivity.id == event['id']
                ).one_or_none():
                    event['created'] = str_to_datetaime(event.get('created'), '%Y-%m-%d %H:%M:%S')
                    event['date_start'] = str_to_datetaime(event.get('date_start'), '%Y-%m-%d')
                    event['time_start'] = str_to_datetaime(event.get('time_start'), '%H:%M:%S')
                    event['date_end'] = str_to_datetaime(event.get('date_end'), '%Y-%m-%d')
                    event['time_end'] = str_to_datetaime(event.get('time_end'), '%H:%M:%S')
                    event['local_datetime'] = str_to_datetaime(event.get('local_datetime'), '%Y-%m-%d %H:%M:%S')
                    event['local_datetime_end'] = str_to_datetaime(event.get('local_datetime_end'), '%Y-%m-%d %H:%M:%S')
                    session.add(FacultetusActivity(**event))
            session.commit()

            current_offset += api_config['OFFSET']


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    time_spent = f"Total time spent: {end - start} sec"
    logger.getLogger('events.py').info(time_spent)
    print(f">>> {time_spent} sec")

