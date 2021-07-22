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
    inputs = {'input_str': ['https://dataverse.no/dataset.xhtml?persistentId=doi:10.18710/PGDWXC',
                            '10.23728/b2share.d64361c0a6384760a8a8f32e0dc4a481',
                            '11304/a287e5b9-feca-4ad6-bc16-14675d574088'],
              'repo_names': ['Trolling',
                             'B2SHARE',
                             'B2SHARE'],
              'first_pid': ['https://dataverse.no/api/access/datafile/:persistentId/?persistentId=doi:10.18710/PGDWXC/LQYPHP',
                            'http://hdl.handle.net/11304/12656642-adeb-4368-9d41-abe58e17b2a7',
                            'https://zenodo.org/api/files/6887cd07-b1f4-4a22-ba6b-0629508f2162/Tour-de-CLARIN-volume-I-2018.pdf',
                            ]}
    dog = DOG()

    def test_sniff(self):
        for input_str, repo_name in zip(self.inputs['input_str'], self.inputs['repo_names']):
            self.assertTrue(repo_name in self.dog.sniff(input_str))

    def test_fetch(self):
        for input_str, first_pid in zip(self.inputs['input_str'], self.inputs['first_pid']):
            first_fetched_pid = self.dog.fetch(input_str)['ref_files'][0]['pid']
            self.assertEqual(first_pid, first_fetched_pid)
