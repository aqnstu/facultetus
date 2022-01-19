# coding: utf-8

from sqlalchemy import Column, Integer, TIMESTAMP, VARCHAR, text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class FacultetusActivity(Base):
    __tablename__ = "facultetus_activity"
    __table_args__ = {"schema": "apiuser"}

    id = Column(VARCHAR(10), primary_key=True, comment='ID события')
    created = Column(TIMESTAMP, comment="Дата создания")
    cprofile_id = Column(VARCHAR(10), comment='ID создателя')
    type = Column(VARCHAR(30), comment="Тип события")
    type_text = Column(VARCHAR(30), comment="Тип события")
    published = Column(VARCHAR(1), comment="Статус публикации")
    students_moderation = Column(VARCHAR(1), comment="Модерация участников")
    students_reg = Column(VARCHAR(1), comment="Регистрация участников")
    cprofiles_moderation = Column(VARCHAR(1), comment="Модерация организаций")
    leader_event_id = Column(VARCHAR(10), comment="ID события на Leader-id")
    timepad_event_id = Column(VARCHAR(10), comment="ID события на Timepad")
    university_id = Column(VARCHAR(10), comment="ID университета")
    fair_id = Column(VARCHAR(10), comment='ID ярмарки вакансий')
    title = Column(VARCHAR(200), comment="Название события")
    slogan = Column(VARCHAR(350), comment="Краткое описание события")
    description = Column(VARCHAR(4000), comment="Описание события")
    background_pic = Column(VARCHAR(150), comment="Заставка события")
    date_start = Column(DateTime, comment="Дата начала")
    time_start = Column(TIMESTAMP, comment="Время начала")
    date_end = Column(DateTime, comment="Дата окончания")
    time_end = Column(TIMESTAMP, comment="Время окончания")
    timezone = Column(VARCHAR(10))
    require_leader_auth = Column(VARCHAR(1))
    require_rsv_auth = Column(VARCHAR(1))
    region = Column(VARCHAR(50), comment="Регион")
    city = Column(VARCHAR(50), comment="Город")
    address = Column(VARCHAR(250), comment="Адрес")
    online = Column(
        VARCHAR(1), comment="Предусмотрено онлайн-участие", name="online", quote=True
    )
    external_link = Column(VARCHAR(500), comment="Внешняя ссылка")
    author_title = Column(VARCHAR(100), comment="Название автора события")
    author_logo = Column(VARCHAR(150), comment="Логотип автора события")
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


class FacultetusUniversity(Base):
    __tablename__ = "facultetus_university"
    __table_args__ = {"schema": "apiuser"}

    university_id = Column(Integer, primary_key=True, comment="Идентификатор образовательного учреждения")
    title = Column(VARCHAR(200), comment="Короткое название ОУ")
    title_full = Column(VARCHAR(500), comment="Длинное название ОУ")
    logo = Column(VARCHAR(150), comment="Логотип университета")
    region = Column(VARCHAR(100), comment="Регион")
    city = Column(VARCHAR(100), comment="Город")
    type = Column(VARCHAR(100), comment="Тип ОУ: 1 - университет, 2 - колледж")
    link = Column(VARCHAR(150), comment="Ссылка на цифровую карьерную среду университета")
    instant_subscription = Column(
        VARCHAR(1),
        comment="Формат подписки для работодателей: 1 - без модерации университетом, 0 - с модерацией университетом",
    )
    instant_student_access = Column(
        VARCHAR(1),
        comment="Доступ к резюме студентов после подписки:"
        "1 - автоматически, без модерации университетом, 0 - после ручной модерации завки университетом",
    )


class FacultetusVac(Base):
    __tablename__ = "facultetus_vac"
    __table_args__ = {"schema": "apiuser"}

    position_id = Column(Integer, primary_key=True, comment="Идентификатор вакансии")
    employer_id = Column(Integer, comment="Идентификатор организации")
    employer_title = Column(VARCHAR(250), comment="Название организации")
    employer_slogan = Column(VARCHAR(200), comment="Название организации")
    employer_logo = Column(VARCHAR(150), comment="Логотип организации (ссылка)")
    employer_type = Column(VARCHAR(300), comment="Тип организации")
    title = Column(VARCHAR(300), comment="Название вакансии")
    type = Column(VARCHAR(20), comment="Тип вакансии")
    lookingfor = Column(VARCHAR(200), comment="Идеальный кандидат")
    region = Column(VARCHAR(50), comment="Регион")
    city = Column(VARCHAR(30), comment="Город")
    address = Column(VARCHAR(200), comment="Адрес")
    background_pic = Column(VARCHAR(150), comment="Фон вакансии (ссылка на картинку)")
    description = Column(VARCHAR(500), comment="Описание вакансии")
    requirements = Column(VARCHAR(300), comment="Требования вакансии")
    cond = Column(VARCHAR(200), comment="Условия вакансии")
    edu_trial_accept = Column(VARCHAR(1), comment="Подходит для практики")
    tempjob = Column(VARCHAR(1), comment="Подходит для подработки")
    forinternationals = Column(VARCHAR(1), comment="Подходит для иностранцев")
    fornewbies = Column(VARCHAR(1), comment="Подходит для новичков (без опыта)")
    fordisabled = Column(VARCHAR(1), comment="Подходит для лиц с ОВЗ")
    remoted = Column(VARCHAR(1), comment="Удалённая работа")
    edu_combo_friendly = Column(VARCHAR(1), comment="Совместимо с учёбой")
    first_year_friendly = Column(VARCHAR(1), comment="Подходит для первых курсов")
    for_graduates = Column(VARCHAR(1), comment="Подходит для выпускников")
    instant_paid = Column(VARCHAR(1), comment="Оплачивается")
    cash_from = Column(Integer, comment="Оклад от")
    cash_to = Column(Integer, comment="Оклад до")
    is_actual = Column(VARCHAR(1), comment="Считается актуальной")
    position_link = Column(VARCHAR(150), comment="Ссылка на вакансию")
    spheres = Column(VARCHAR(200), comment="Сферы вакансии")
    langs = Column(VARCHAR(200), comment="Требования по языкам")
    skills = Column(VARCHAR(200), comment="Требования по навыкам")
    tests = Column(VARCHAR(300), comment="Привязанные к вакансии тестирования")
    professions = Column(VARCHAR(300), comment="Профессии, релевантные вакансии")
    date_added = Column(TIMESTAMP, server_default=text("sysdate"))
