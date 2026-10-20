import unittest, sys
import databaseQuerys as db

class TestDBCalls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()

    def test_default(self):
        self.assertEqual(0, 0)

    def test_school_theme(self):
        schools = db.get_all_schools()
        if schools:
            school_id = schools[0]['id']
            db.update_school_theme(school_id, '#111111', '#222222', 'Arial', '#333333')
            theme = db.get_school_theme(school_id)
            self.assertEqual(theme['bg_color'], '#111111')
            self.assertEqual(theme['text_color'], '#222222')
            self.assertEqual(theme['font_family'], 'Arial')
            self.assertEqual(theme['border_color'], '#333333')

            sched = db.get_todays_schedule(school_id)
            self.assertEqual(sched['default_border_color'], '#333333')


if __name__ == '__main__':
    unittest.main()
