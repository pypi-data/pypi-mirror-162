from dispositor.db.db import DispositorDB
from dispositor import space as spaceClass
import pandas as pd
from dispositor.experiments.degree_of_displacement.degree_of_displacement import DegreeOfDisplacement
from planet import Sun

if __name__ == '__main__':
    db = DispositorDB({
        'host': 'localhost',
        'user': 'user',
        'password': 'password',
        'database': 'people',
        'prefix': 'wwwtest_'
    })

    #  Пример заполнения таблицы "дни"
    # space = spaceClass.Space(spaceClass.septenerSegmentData(), None, db)
    #
    # start_date = '1900-01-01'
    # end_date = '1901-01-01'
    #
    # daterange = pd.date_range(start_date, end_date)
    #
    # for single_date in daterange:
    #     date = single_date.strftime("%Y/%m/%d")
    #     space.setDate(date)
    #     space.save()
    #     print(date)


    # Пример заполенния таблицы Центры по дням
    # space = spaceClass.Space(spaceClass.septenerSegmentData(), None, db)
    # planet = space.planets[0]
    # segment = space.segments[0]
    # degree_of_displacement = DegreeOfDisplacement(
    #     space=space,  # Пространство
    #     row_count=10000,  # Количество человек по условию
    #     conditions={'planetId': planet.id, 'segmentId': segment.id},  # Условие
    #     summary_people_threshold=50,  # Порог количества людей одной деятельности по условию
    # )
    # degree_of_displacement.fillingCenterTable()

    #  Пример создания эксперимента "По степени смещения"
    # space = spaceClass.Space(spaceClass.septenerSegmentData(), None, db)
    # planet = space.planets[0]
    # segment = space.segments[0]
    # degree_of_displacement = DegreeOfDisplacement(
    #     space=space,  # Пространство
    #     row_count=10000,  # Количество человек по условию
    #     conditions={'planetId': planet.id, 'segmentId': segment.id},  # Условие/ можно передать center_planet_id
    #     summary_people_threshold=50,  # Порог количества людей одной деятельности по условию
    # )
    # degree_of_displacement = degree_of_displacement.fillingDegreeOfDisplacement(planet, segment)
    # print(degree_of_displacement)