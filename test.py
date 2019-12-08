import unittest
from final import *
import final as final

class TestDatabase(unittest.TestCase):

    def test_site_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT SiteName FROM HeritageSites'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Asmara',), result_list)
        self.assertEqual(len(result_list), 145)

        sql = '''
            SELECT SiteName, Criteria, [Year]
            FROM HeritageSites
            WHERE Criteria="Cultural"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 91)
        self.assertEqual(result_list[3][2], 1980)

        conn.close()

    def test_country_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT COUNT(*)
            FROM Countries
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 44)

        conn.close()

#     def test_joins(self):
#         conn = sqlite3.connect(DBNAME)
#         cur = conn.cursor()
#
#         sql = '''
#             SELECT SiteName, c.CountryName, c.Region, [Year]
# FROM HeritageSites JOIN Countries as c ON HeritageSites.CountryId = c.Id
# WHERE Criteria="Cultural"
#         '''
#         results = cur.execute(sql)
#         result_list = results.fetchall()
#         self.assertIn(('Aapravasi Ghat',), result_list)
#         conn.close()

class TestCriteriaSearch(unittest.TestCase):

    def test_site_search(self):
        results = process_command('CountryName=Egypt')
        self.assertEqual(results[0][0], 'Abu Mena')

        results = process_command('CountryName=Kenya Criteria=Natural')
        self.assertEqual(results[1][0], 'Lake Turkana National Parks',)

        results = process_command('CountryName=Tunisia Year')
        self.assertEqual(results[2][0], 'Medina of Tunis')

        results = process_command('Criteria=Natural Year')
        self.assertEqual(results[6][0], 'Mount Nimba Strict Nature Reserve')

        results = process_command('SiteName=Abu_Mena')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'Abu Mena')

class TestWorldHeritage(unittest.TestCase):

    def testConstructor(self):
        s1 = final.WorldHeritage(('Abu Mena', 'Egypt', 'Africa', 'Cultural', 29.663117, 30.84098, '182 (450)', 1979, 'The ruins of the former Christian holy city contain a church, a baptistery, basilicas, public buildings, streets, monasteries, houses, and workshops, and were built over the tomb of Menas of Alexandria.[28] The World Heritage Committee designated Abu Mena as an endangered site in 2001, due to cave-ins in the area caused by the clay at the surface, which becomes semi-liquid when met with "excess water".[29]'))
        self.assertEqual(s1.sitename, "Abu Mena")
        self.assertEqual(s1.country, "Egypt")
        self.assertEqual(s1.region, "Africa")
        self.assertEqual(s1.criteria, "Cultural")
        self.assertEqual(s1.longtitude, 29.663117)
        self.assertEqual(s1.latitude, 30.84098)
        self.assertEqual(s1.area,'182 (450)')
        self.assertEqual(s1.year, 1979)
        self.assertEqual(s1.description,'The ruins of the former Christian holy city contain a church, a baptistery, basilicas, public buildings, streets, monasteries, houses, and workshops, and were built over the tomb of Menas of Alexandria.[28] The World Heritage Committee designated Abu Mena as an endangered site in 2001, due to cave-ins in the area caused by the clay at the surface, which becomes semi-liquid when met with "excess water".[29]')

    def testStr(self):
        s1 = final.WorldHeritage(('Abu Mena', 'Egypt', 'Africa', 'Cultural', 29.663117, 30.84098, '182 (450)', 1979, 'The ruins of the former Christian holy city contain a church, a baptistery, basilicas, public buildings, streets, monasteries, houses, and workshops, and were built over the tomb of Menas of Alexandria.[28] The World Heritage Committee designated Abu Mena as an endangered site in 2001, due to cave-ins in the area caused by the clay at the surface, which becomes semi-liquid when met with "excess water".[29]'))
        self.assertEqual(str(s1), "Abu Mena is a Cultural heritage site in Egypt")


unittest.main()
