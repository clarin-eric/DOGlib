from unittest import TestCase

from pid import PID, URL, HDL, DOI
from doglib import DOG


class TestPID(TestCase):
    def test_init(self):
        self.assertEqual(PID('https://dataverse.no/dataset.xhtml?persistentId=doi:10.18710/PGDWXC').get_pid_type(), URL)
        self.assertEqual(PID('https://b2share.eudat.eu/records/d64361c0a6384760a8a8f32e0dc4a481').get_pid_type(), URL)
        self.assertEqual(PID('11304/a287e5b9-feca-4ad6-bc16-14675d574088').get_pid_type(), HDL)
        self.assertEqual(PID('10.23728/b2share.d64361c0a6384760a8a8f32e0dc4a481').get_pid_type(), DOI)
        self.assertEqual(PID('http://hdl.handle.net/11304/a287e5b9-feca-4ad6-bc16-14675d574088').get_pid_type(), HDL)
        self.assertEqual(PID('https://doi.org/10.23728/b2share.d64361c0a6384760a8a8f32e0dc4a481').get_pid_type(), DOI)
        self.assertRaises(ValueError, PID, 'notapid')

    def test_tourl(self):
        pass


class TestDOG(TestCase):
    def test_sniff(self):
        dog = DOG()

        inputs = {'input_str': ['https://dataverse.no/dataset.xhtml?persistentId=doi:10.18710/PGDWXC',
                                '10.23728/b2share.d64361c0a6384760a8a8f32e0dc4a481',
                                '11304/a287e5b9-feca-4ad6-bc16-14675d574088'],
                  'repo_names': ['Trolling',
                                'B2SHARE',
                                'B2SHARE']}

        for input_str, repo_name in zip(inputs['input_str'], inputs['repo_names']):
            b = dog.sniff(input_str)
            self.assertTrue(repo_name in dog.sniff(input_str))