import datetime
import unittest

from dateutil import tz

from onedrivee.common import dateparser


class TestTimeConversion(unittest.TestCase):
    s = '1970-01-01T00:01:01.860000Z'
    d = datetime.datetime(1970, 1, 1, 0, 1, 1, 860000, tzinfo=tz.gettz('UTC'))
    t = 61.86

    def test_convert(self):
        self.assertEqual(self.d, dateparser.str_to_datetime(self.s))
        self.assertEqual(self.s, dateparser.datetime_to_str(self.d))
        self.assertEqual(self.t, dateparser.datetime_to_timestamp(self.d))
        # self.assertEqual(self.d, onedrivee.timestamp_to_datetime(self.t))
