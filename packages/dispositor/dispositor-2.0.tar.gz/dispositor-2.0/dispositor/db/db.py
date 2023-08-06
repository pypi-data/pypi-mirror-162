from dispositor.db.connection import Connection


class DispositorDB(Connection):
    def __init__(self, settings):
        self.settings = settings
        Connection.__init__(self, settings['host'], settings['user'], settings['password'], settings['database'])

    def init(self, planets, segments):
        if self.isExistTable('planets') is not True:
            self.createPlanetTable()
        if self.isExistTable('segments') is not True:
            self.createSegmentTable()
        if self.isExistTable('days') is not True:
            self.createDayTable()
        self.fillingPlanetTable(planets)
        self.fillingSegmentTable(segments)
        return self

    def isExistTable(self, base_name):
        table_name = self.getTableName(base_name)
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES LIKE '%s'" % table_name)
        return True if cursor.fetchone() else False

    def getTableName(self, base_name):
        return self.settings['prefix'] + base_name if self.settings['prefix'] is not None else base_name

    def createPlanetTable(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE `%s` ("
                       "`id` int(11) NOT NULL AUTO_INCREMENT,"
                       "`name` varchar(100) NOT NULL,"
                       "PRIMARY KEY (`id`)"
                       ") ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;" % self.getTableName('planets'))

    def createSegmentTable(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE `%s` ("
                       "`id` int(11) NOT NULL AUTO_INCREMENT,"
                       "`name` varchar(100) NOT NULL,"
                       "`planet_id` int(11) NOT NULL,"
                       "PRIMARY KEY (`id`),"
                       "KEY `segments_FK` (`planet_id`)"
                       ") ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;" % self.getTableName('segments'))

    def createDayTable(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE `%s` ("
                       "`id` int(11) NOT NULL AUTO_INCREMENT,"
                       "`planet_id` int(11) NOT NULL,"
                       "`segment_id` int(11) NOT NULL,"
                       "`date` date NOT NULL,"
                       "PRIMARY KEY (`id`),"
                       "UNIQUE KEY `days_UN` (`planet_id`,`date`)"
                       ") ENGINE=InnoDB AUTO_INCREMENT=383517 DEFAULT CHARSET=latin1;" % self.getTableName('days'))

    def truncateTable(self, tableName):
        cursor = self.connection.cursor()
        cursor.execute("TRUNCATE TABLE %s;" % self.getTableName(tableName))

    def fillingPlanetTable(self, planets):
        for planet in planets:
            create_planet_query = "INSERT IGNORE INTO people.%s (id, name) VALUES (%s, '%s');" % (
                self.getTableName('planets'), planet.id, planet.name)
            with self.connection.cursor() as cursor:
                cursor.execute(create_planet_query)
                self.connection.commit()

    def fillingSegmentTable(self, segments):
        for segment in segments:
            create_segment_query = "INSERT IGNORE INTO people.%s (id, name, planet_id) VALUES (%s, '%s', %s);" % (
                self.getTableName('segments'), segment.id, segment.name, segment.owner_planet.id)
            with self.connection.cursor() as cursor:
                cursor.execute(create_segment_query)
                self.connection.commit()

    def fillingDayTable(self, planets, date):
        for planet in planets:
            create_day_query = "INSERT IGNORE INTO people.%s " \
                               "(planet_id, segment_id, date) " \
                               "VALUES (%s, '%s', '%s');" \
                               % (self.getTableName('days'), planet.id, planet.getSegment().id, date)
            with self.connection.cursor() as cursor:
                cursor.execute(create_day_query)
                self.connection.commit()

