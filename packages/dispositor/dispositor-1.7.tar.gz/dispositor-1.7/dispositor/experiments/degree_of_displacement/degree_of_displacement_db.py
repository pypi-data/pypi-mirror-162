import random
from decimal import *
from dispositor.chain import Chain


class DegreeOfDisplacementDB:
    def __init__(self, space):
        self.space = space

    def init(self):
        # Создание таблиц
        if self.space.db.isExistTable('degree_of_displacements') is not True:
            self.createDegreeOfDisplacementTable()
        if self.space.db.isExistTable('degree_of_displacement_types') is not True:
            self.createDegreeOfDisplacementTypesTable()
        if self.space.db.isExistTable('degree_of_displacement_values') is not True:
            self.createDegreeOfDisplacementValuesTable()
        if self.space.db.isExistTable('degree_of_displacement_people') is not True:
            self.createDegreeOfDisplacementPeopleTable()
        if self.space.db.isExistTable('center_days') is not True:
            self.createCenterDaysTable()
        # Заполнение таблицы типов
        self.fillingDegreeOfDisplacementTypesTable([
            {'id': 1, 'name': 'Связанный'},
            {'id': 2, 'name': 'Случайный'},
        ])
        return self

    def createDegreeOfDisplacementTable(self):
        cursor = self.space.db.connection.cursor()
        cursor.execute("CREATE TABLE `%s` ("
                       "`id` int(11) NOT NULL AUTO_INCREMENT,"
                       "`degree_of_displacement_type_id` int(11) NOT NULL,"
                       "PRIMARY KEY (`id`),"
                       "KEY `degree_of_displacements_degree_of_displacement_type_id_IDX`"
                       " (`degree_of_displacement_type_id`) USING BTREE"
                       ") ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;"
                       % self.space.db.getTableName('degree_of_displacements'))

    def createDegreeOfDisplacementTypesTable(self):
        cursor = self.space.db.connection.cursor()
        cursor.execute("CREATE TABLE `%s` ("
                       "`id` int(11) NOT NULL AUTO_INCREMENT,"
                       "`name` varchar(100) NOT NULL,"
                       "PRIMARY KEY (`id`)"
                       ") ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;"
                       % self.space.db.getTableName('degree_of_displacement_types'))

    def createDegreeOfDisplacementValuesTable(self):
        cursor = self.space.db.connection.cursor()
        cursor.execute("CREATE TABLE `%s` ("
                       "`id` int(11) NOT NULL AUTO_INCREMENT,"
                       "`value_id` int(11) NOT NULL,"
                       "`degree_of_displacement_id` int(11) NOT NULL,"
                       "`percent` decimal(10,9) NOT NULL DEFAULT '0',"
                       "`idx` int(11) NOT NULL DEFAULT '0',"
                       "PRIMARY KEY (`id`),"
                       "UNIQUE KEY `degree_of_displacement_values_value_id_IDX` "
                       "(`value_id`,`degree_of_displacement_id`) USING BTREE"
                       ") ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;"
                       % self.space.db.getTableName('degree_of_displacement_values'))

    def createDegreeOfDisplacementPeopleTable(self):
        cursor = self.space.db.connection.cursor()
        cursor.execute("CREATE TABLE `%s` ("
                       "`id` int(11) NOT NULL AUTO_INCREMENT,"
                       "`people_id` int(11) NOT NULL,"
                       "`degree_of_displacement_id` int(11) NOT NULL,"
                       "PRIMARY KEY (`id`),"
                       "UNIQUE KEY `degree_of_displacement_people_people_id_IDX` (`people_id`) USING BTREE"
                       ") ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;"
                       % self.space.db.getTableName('degree_of_displacement_people'))

    def createCenterDaysTable(self):
        cursor = self.space.db.connection.cursor()
        cursor.execute("CREATE TABLE `%s` ("
                       "`id` int(11) NOT NULL AUTO_INCREMENT,"
                       "`date` date NOT NULL,"
                       "`center_planet_ids` varchar(100) NOT NULL,"
                       "PRIMARY KEY (`id`),"
                       "UNIQUE KEY `center_days_date_IDX` (`date`) USING BTREE"
                       ") ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;"
                       % self.space.db.getTableName('center_days'))

    def fillingDegreeOfDisplacementTypesTable(self, types):
        for type in types:
            create_type_query = "INSERT IGNORE INTO people.%s (id, name) VALUES (%s, '%s');" % (
                self.space.db.getTableName('degree_of_displacement_types'), type['id'], type['name'])
            with self.space.db.connection.cursor() as cursor:
                cursor.execute(create_type_query)
                self.space.db.connection.commit()

    def fillingDegreeOfDisplacementTable(self, degree_of_displacements):
        self.space.db.truncateTable('degree_of_displacements')
        for degree_of_displacement in degree_of_displacements:
            create_degree_of_displacements_query = "INSERT IGNORE INTO people.%s " \
                                                   "(id, degree_of_displacement_type_id) VALUES (%s, '%s');" % (
                                                       self.space.db.getTableName('degree_of_displacements'),
                                                       degree_of_displacement['id'],
                                                       degree_of_displacement['type_id'])
            with self.space.db.connection.cursor() as cursor:
                cursor.execute(create_degree_of_displacements_query)
                self.space.db.connection.commit()

    def fillingDegreeOfDisplacementPeopleTable(self, row_count):
        cursor = self.space.db.connection.cursor()
        cursor.execute("SELECT * FROM %s WHERE degree_of_displacement_type_id = 1"
                       % self.space.db.getTableName('degree_of_displacements'))

        degree_of_displacements = cursor.fetchall()
        self.space.db.truncateTable('degree_of_displacement_people')
        for degree_of_displacement in degree_of_displacements:
            create_dod_people_query = "INSERT IGNORE INTO %s (people_id, degree_of_displacement_id)" \
                                      " SELECT id, %s FROM peopels" \
                                      " WHERE id NOT IN (SELECT people_id FROM %s)" \
                                      " AND birthday_date IS NOT NULL " \
                                      " AND birthday_date > '1900-01-01' " \
                                      " AND id IN  " \
                                      " (SELECT people_id FROM people_properties  " \
                                      " WHERE people_properties.property = 'P106')  " \
                                      " ORDER BY RAND(%s) LIMIT %s;" % (
                                          self.space.db.getTableName('degree_of_displacement_people'),
                                          degree_of_displacement[0],
                                          self.space.db.getTableName('degree_of_displacement_people'),
                                          random.randint(1, 34716624),
                                          row_count)
            with self.space.db.connection.cursor() as cursor:
                cursor.execute(create_dod_people_query)
                self.space.db.connection.commit()

    def fillingDegreeOfDisplacementValuesTable(self, conditions, summary_people_threshold):
        self.space.db.truncateTable('degree_of_displacement_values')

        cursor = self.space.db.connection.cursor()
        cursor.execute("SELECT * FROM %s WHERE degree_of_displacement_type_id = 1"
                       % self.space.db.getTableName('degree_of_displacements'))

        degree_of_displacements = cursor.fetchall()

        if conditions['center_planet_id'] is not None:
            astroCondition = "SELECT date  FROM %s d WHERE center_planet_ids LIKE '%%%s%%' " % (
                self.space.db.getTableName('center_days'),
                conditions['center_planet_id'],
            )
        else:
            astroCondition = "SELECT date  FROM %s d WHERE planet_id = %s and segment_id = %s" % (
                self.space.db.getTableName('days'),
                conditions['planet_id'],
                conditions['segment_id'],
            )

        for degree_of_displacement in degree_of_displacements:
            cursor = self.space.db.connection.cursor()
            cursor.execute(
                """
            SELECT 
            all_rows.value_id, 
            all_rows.count as all_count, 
            IFNULL(condition_rows.count, 0) as condition_count, 
            (IFNULL(condition_rows.count, 0) / all_rows.count ) as percent
            FROM (
                SELECT value_id, COUNT(*) as count FROM (
                SELECT 
                    pp.value_id
                FROM peopels p
                JOIN people_properties pp ON p.id = pp.people_id 
                WHERE birthday_date IS NOT NULL 
                AND birthday_date > '1900-01-01'
                AND pp.property = 'P106' 
                AND p.id IN (
                    SELECT people_id 
                    FROM %s wdodp
                    WHERE degree_of_displacement_id = %s
                    )
                ) as group_all_rows
                GROUP BY value_id
            ) as all_rows
            LEFT JOIN (
            SELECT value_id, COUNT(*) as count FROM (
                SELECT 
                    pp.value_id
                FROM peopels p
                JOIN people_properties pp ON p.id = pp.people_id 
                WHERE birthday_date IS NOT NULL
                AND birthday_date > '1900-01-01' 
                AND pp.property = 'P106' 
                AND p.id IN (
                    SELECT people_id 
                    FROM %s wdodp
                    WHERE degree_of_displacement_id = %s)
                    AND birthday_date IN (
                        %s
                    )
            ) as group_condition_rows
            GROUP BY value_id)
            as condition_rows ON all_rows.value_id = condition_rows.value_id 
            WHERE all_rows.count > %s ORDER BY percent DESC;
                """
                % (
                    self.space.db.getTableName('degree_of_displacement_people'),
                    degree_of_displacement[0],
                    self.space.db.getTableName('degree_of_displacement_people'),
                    degree_of_displacement[0],
                    astroCondition,
                    summary_people_threshold,
                ))

            degree_of_displacement_values = cursor.fetchall()
            for idx, degree_of_displacement_value in enumerate(degree_of_displacement_values):
                create_degree_of_displacement_value_query = "INSERT IGNORE INTO people.%s " \
                                                            "(value_id, degree_of_displacement_id, idx, percent) " \
                                                            " VALUES (%s, '%s', '%s', '%s');" % (
                                                                self.space.db.getTableName(
                                                                    'degree_of_displacement_values'),
                                                                degree_of_displacement_value[0],
                                                                degree_of_displacement[0],
                                                                idx,
                                                                Decimal(degree_of_displacement_value[3])
                                                            )
                with self.space.db.connection.cursor() as cursor:
                    cursor.execute(create_degree_of_displacement_value_query)
                    self.space.db.connection.commit()

    def fillingCenterDaysTable(self):
        cursor = self.space.db.connection.cursor()
        cursor.execute("SELECT date FROM %s GROUP BY `date`;" % self.space.db.getTableName('days'))

        chain = Chain(self.space)
        days = cursor.fetchall()
        for day in days:
            self.space.setDate(day[0])
            chain.setSpace(self.space)
            center_planet_ids = ''.join([str(planet.id) for planet in chain.getCenterPlanets()])
            create_center_day_query = "INSERT IGNORE INTO people.%s (date, center_planet_ids) VALUES ('%s', '%s');" % (
                self.space.db.getTableName('center_days'), day[0].strftime("%Y-%m-%d"), center_planet_ids)
            with self.space.db.connection.cursor() as cursor:
                cursor.execute(create_center_day_query)
                self.space.db.connection.commit()
            print(day[0].strftime("%Y-%m-%d"))

    def pruningDegreeOfDisplacementValuesTables(self):
        delete_degree_of_displacement_value_query = "DELETE FROM %s " \
                                                    "WHERE  value_id NOT IN ( " \
                                                    "SELECT value_alies.value_id " \
                                                    "FROM ( " \
                                                    "SELECT wdodv.value_id " \
                                                    "FROM %s wdodv " \
                                                    "JOIN %s wdodv2 " \
                                                    " ON wdodv.value_id = wdodv2.value_id " \
                                                    " AND wdodv.degree_of_displacement_id != wdodv2.degree_of_displacement_id) as value_alies);" \
                                                    % (
                                                        self.space.db.getTableName('degree_of_displacement_values'),
                                                        self.space.db.getTableName('degree_of_displacement_values'),
                                                        self.space.db.getTableName('degree_of_displacement_values'),
                                                    )
        with self.space.db.connection.cursor() as cursor:
            cursor.execute(delete_degree_of_displacement_value_query)
            self.space.db.connection.commit()

    def fillingRandDegreeOfDisplacementValuesTable(self):
        cursor = self.space.db.connection.cursor()
        cursor.execute("SELECT * FROM %s WHERE degree_of_displacement_type_id = 2"
                       % self.space.db.getTableName('degree_of_displacements'))

        degree_of_displacements = cursor.fetchall()
        for degree_of_displacement in degree_of_displacements:
            cursor = self.space.db.connection.cursor()
            cursor.execute("SELECT value_id FROM %s WHERE degree_of_displacement_id = 1 ORDER BY RAND(%s)"
                           % (
                               self.space.db.getTableName('degree_of_displacement_values'),
                               random.randint(1, 64236784),
                           ))
            degree_of_displacement_values = cursor.fetchall()
            for idx, degree_of_displacement_value in enumerate(degree_of_displacement_values):
                create_rand_dod_values_query = "INSERT IGNORE INTO %s (value_id, degree_of_displacement_id, idx, percent)" \
                                               " VALUES (%s, '%s', '%s', '%s');" % (
                                                   self.space.db.getTableName('degree_of_displacement_values'),
                                                   degree_of_displacement_value[0],
                                                   degree_of_displacement[0],
                                                   idx,
                                                   0)
                with self.space.db.connection.cursor() as cursor:
                    cursor.execute(create_rand_dod_values_query)
                    self.space.db.connection.commit()

    def getContrast(self, first_degree_of_displacement_id, second_degree_of_displacement_id):
        cursor = self.space.db.connection.cursor()
        cursor.execute("SELECT SUM(ABS(sel_1.idx - sel_2.idx)) as sum "
                       " FROM (SELECT value_id, idx FROM %s wdodv "
                       " WHERE wdodv.degree_of_displacement_id =%s) as sel_1 "
                       "LEFT JOIN "
                       "(SELECT value_id, idx "
                       "FROM %s wdodv "
                       "WHERE wdodv.degree_of_displacement_id =%s) sel_2 ON sel_1.value_id = sel_2.value_id;"
                       % (
                           self.space.db.getTableName('degree_of_displacement_values'),
                           first_degree_of_displacement_id,
                           self.space.db.getTableName('degree_of_displacement_values'),
                           second_degree_of_displacement_id,
                       ))
        return cursor.fetchall()[0][0]

    def showContrast(self):
        cursor = self.space.db.connection.cursor()
        cursor.execute("SELECT id FROM %s"
                       % self.space.db.getTableName('degree_of_displacements'))
        degree_of_displacements = cursor.fetchall()
        result = {}
        for first_degree_of_displacement in degree_of_displacements:
            for second_degree_of_displacement in degree_of_displacements:
                contrast = self.getContrast(first_degree_of_displacement[0], second_degree_of_displacement[0])
                if contrast == 0: continue
                result[second_degree_of_displacement[0]] = int(self.getContrast(first_degree_of_displacement[0],
                                                                           second_degree_of_displacement[0]))
            break
        result = list(dict(sorted(result.items(), key=lambda item: item[1])).keys())
        return result.index(2)
