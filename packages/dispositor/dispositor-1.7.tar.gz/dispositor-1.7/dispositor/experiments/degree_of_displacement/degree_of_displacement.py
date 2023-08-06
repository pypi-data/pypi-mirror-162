from dispositor.experiments.degree_of_displacement.degree_of_displacement_db import DegreeOfDisplacementDB

class DegreeOfDisplacement:
    def __init__(self, space, row_count, conditions,
                 summary_people_threshold):
        self.space = space
        self.row_count = row_count  # Количество записей в таблице
        self.conditions = conditions  # Астрономические условия
        self.summary_people_threshold = summary_people_threshold  # суммарное количества людей в одном роде деятельности

    def fillingDegreeOfDisplacement(self, planet, segment):
        degree_of_displacement_db = DegreeOfDisplacementDB(self.space)
        degree_of_displacement_db.init()
        # Заполнение таблицы экспериментов по параметрам
        degree_of_displacement_db.fillingDegreeOfDisplacementTable([
            {'id': 1, 'type_id': 1},
            {'id': 2, 'type_id': 1},
            {'id': 3, 'type_id': 2},
            {'id': 4, 'type_id': 2},
            {'id': 5, 'type_id': 2},
            {'id': 6, 'type_id': 2},
            {'id': 7, 'type_id': 2},
            {'id': 8, 'type_id': 2},
            {'id': 9, 'type_id': 2},
        ])
        # Заполнение таблицы людей (деление на части при том, чтобы люди не повторялись)
        degree_of_displacement_db.fillingDegreeOfDisplacementPeopleTable(self.row_count)
        # Заполнение таблицы значений
        degree_of_displacement_db.fillingDegreeOfDisplacementValuesTable({'planet_id':  planet.id,
                                                                          'segment_id': segment.id,
                                                                          'center_planet_id': None},
                                                                         self.summary_people_threshold)
        # Обрезка значение, чтобы во всех таблицах были одинаковые
        degree_of_displacement_db.pruningDegreeOfDisplacementValuesTables()

        # Построение случайных выборок
        degree_of_displacement_db.fillingRandDegreeOfDisplacementValuesTable()

        # Сравнение
        return degree_of_displacement_db.showContrast()

    def fillingCenterTable(self):
        degree_of_displacement_db = DegreeOfDisplacementDB(self.space)
        degree_of_displacement_db.fillingCenterDaysTable()
