from unittest import TestCase

from pid import PID, URL, HDL, DOI


class TestPID(TestCase):
    def test_pid(self):
        self.assertEqual(PID('https://b2share.eudat.eu/records/d64361c0a6384760a8a8f32e0dc4a481').pid_type(), URL)
        self.assertEqual(PID('11304/a287e5b9-feca-4ad6-bc16-14675d574088').pid_type(), HDL)
        self.assertEqual(PID('10.23728/b2share.d64361c0a6384760a8a8f32e0dc4a481').pid_type(), DOI)
