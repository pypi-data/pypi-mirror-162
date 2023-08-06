import unittest
import os
from src.rhclient import client

host = os.environ.get('RH_HOST', 'localhost')
port = os.environ.get('RH_PORT', '5000')
client.configUrl(f"http://{host}:{port}")

class test_dynamicHeaders(unittest.TestCase) :

    @classmethod
    def setUpClass(self) -> None:
            print('\n\n###################################    Testing Dynamic Headers    #############################################\n\n')
            return super().setUpClass()

    @classmethod
    def tearDownClass(self) -> None:
            print('\n\n###################################    Done Testing Dynamic Headers    #############################################\n\n')
            return super().tearDownClass()

    def test_01_single_path_default_header(self):
        #Base test. No header given, should create path normally
        client.create_path('/test1', 200, 'test1')
        expected = {'delay': 0, 'headers': {'Content-Type': 'application/json'}, 'rc': 200, 'return_value': 'test1'}
        actual = client.get_path('/test1')
        self.assertEqual(expected, actual)
        client.delete_path('/test1')

    def test_02_single_path_additional_header(self):
        #Tests additional headers. Should post + include additional header info.
        client.create_path('/test2', 200, 'test2', headers={'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT'})
        expected = {'delay': 0, 'headers': {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT', 'Content-Type':'application/json'}, 'rc': 200, 'return_value': 'test2'}
        actual = client.get_path('/test2')
        self.assertEqual(expected, actual)
        client.delete_path('/test2')

    def test_03_single_path_garbage_header(self):
        #Tests error handling for invalid header object.
        with self.assertRaises(TypeError) as err_context1:
            client.create_path('/test3-1', 200, 'test3-1', headers='Content-Type : application/json')
        with self.assertRaises(TypeError) as err_context2:
            client.create_path('/test3-2', 200, 'test3-2', headers=['Content-Type', 'application/json'])
        with self.assertRaises(TypeError) as err_context3:
            client.create_path('/test3-3', 200, 'test3-3', headers=123456)

        self.assertEqual(type(err_context1.exception), type(err_context2.exception))
        self.assertEqual(type(err_context1.exception), type(err_context3.exception))

    def test_04_update_single_path_with_header(self):
        #Tests update function compatibility with new header introduction.
        client.create_path('/test4', 200, 'test4')
        client.update_path('/test4', 200, 'test4', headers={'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT'})
        expected = {'delay': 0, 'headers': {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT', 'Content-Type': 'application/json'}, 'rc': 200, 'return_value': 'test4'}
        actual = client.get_path('/test4')
        self.assertEqual(expected, actual)
        client.delete_path('/test4')

    def test_05_multipath_default_header(self):
        #Tests if create_paths() handles no additional headers. Default setting tests.
        data = [
                {'path' : '/test5-1', 'rc' : 200, 'return_value' : 'test5-1'},
                {'path' : '/test5-2', 'rc' : 200, 'return_value' : 'test5-2'},
                {'path' : '/test5-3', 'rc' : 200, 'return_value' : 'test5-3'},
                {'path' : '/test5-4', 'rc' : 200, 'return_value' : 'test5-4'}
            ]

        client.create_paths(data)
        expected = [
                {'delay': 0, 'headers': {'Content-Type' : 'application/json'},'rc':200, 'return_value':'test5-1'},
                {'delay': 0, 'headers': {'Content-Type' : 'application/json'},'rc':200, 'return_value':'test5-2'},
                {'delay': 0, 'headers': {'Content-Type' : 'application/json'},'rc':200, 'return_value':'test5-3'},
                {'delay': 0, 'headers': {'Content-Type' : 'application/json'},'rc':200, 'return_value':'test5-4'}
                ]

        actual = []
        for obj in data:
            path = client.get_path(obj['path'])
            actual.append(path)

        self.assertEqual(expected, actual)

        for obj in data:
            client.delete_path(obj['path'])

    def test_06_multipath_additional_headers(self):
        #Tests introduction of new headers to each path.
        data = [
                {'path' : '/test6-1', 'rc' : 200, 'return_value' : 'test6-1', 'headers' : {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT'}},
                {'path' : '/test6-2', 'rc' : 200, 'return_value' : 'test6-2', 'headers' : {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT'}},
                {'path' : '/test6-3', 'rc' : 200, 'return_value' : 'test6-3', 'headers' : {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT'}},
                {'path' : '/test6-4', 'rc' : 200, 'return_value' : 'test6-4', 'headers' : {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT'}}
            ]

        client.create_paths(data)
        expected = [
                {'delay': 0, 'headers': {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT', 'Content-Type' : 'application/json'},'rc':200, 'return_value':'test6-1'},
                {'delay': 0, 'headers': {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT', 'Content-Type' : 'application/json'},'rc':200, 'return_value':'test6-2'},
                {'delay': 0, 'headers': {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT', 'Content-Type' : 'application/json'},'rc':200, 'return_value':'test6-3'},
                {'delay': 0, 'headers': {'Expires': 'Wed, 21 Oct 2015 07:28:00 GMT', 'Content-Type' : 'application/json'},'rc':200, 'return_value':'test6-4'}
                ]

        actual = []
        for obj in data:
            path = client.get_path(obj['path'])
            actual.append(path)

        self.assertEqual(expected, actual)

        for obj in data:
            client.delete_path(obj['path'])

if __name__ == "__main__" :
    unittest.main()
