from src.rhclient import client
#import client
import unittest, logging, os

host = os.environ.get('RH_HOST', 'localhost')
port = os.environ.get('RH_PORT', '5000')
client.configUrl(f"http://{host}:{port}")

class test_save_method(unittest.TestCase) :
    @classmethod
    def setUpClass(self) -> None:
            print('\n\n###################################    Testing Save Method    #############################################\n\n')
            logging.info(f"Testing {__class__.__name__}")
            return super().setUpClass()

    @classmethod
    def tearDownClass(self) -> None:
            client = None
            print('\n\n###################################    Done Testing Save Method    #############################################\n\n')
            return super().tearDownClass()

    def test_01_default_get(self):
        client.create_path('/test1', 200, 'content1')
        client.create_path('/test2', 200, 'content2')

        # testing default get
        expected = {'/test1': {'delay': 0, 'headers': {'Content-Type': 'application/json'}, 'rc': 200, 'return_value': 'content1'}, '/test2': {'delay': 0, 'headers': {'Content-Type': 'application/json'}, 'rc': 200, 'return_value': 'content2'}}
        actual = client.get_all()
        self.assertEqual(expected, actual)

        client.delete_path('/test1')
        client.delete_path('/test2')

    def test_02_save_robustness(self):
        client.create_path('/test1', 200, 'content1')
        client.create_path('/test2', 200, 'content2')

        pass_code = 200
        bad_code = 400

        # testing default save feature
        test1 = client.get_all(save=True, bucket='rhdevbucket', key='test.json')
        self.assertEqual(pass_code, test1.status_code)

        # testing missing all arguments
        test2 = client.get_all(save=True)
        self.assertEqual(bad_code, test2.status_code)

        # testing missing one argument
        test3 = client.get_all(save=True, bucket='rhdevbucket')
        self.assertEqual(bad_code, test3.status_code)

        # testing invalid bucket
        test4 = client.get_all(save=True, bucket="ytdckitdlogtullllyufyrhfxjyxzlxjgxc;.shjtedjgfckutdl", key="garbage_key")
        self.assertEqual(bad_code, test4.status_code)

        client.delete_path('/test1')
        client.delete_path('/test2')

if __name__ == "__main__" :
    unittest.main()
