import time
import unittest
from src.rhclient import client
import argparse
import os


host = os.environ.get('RH_HOST', 'localhost')
port = os.environ.get('RH_PORT', '5000')
client.configUrl(f"http://{host}:{port}")

class test_delay(unittest.TestCase) :

    @classmethod
    def setUpClass(self) -> None:
            print('\n\n###################################    Testing Endpoint Delay    #############################################\n\n')
            return super().setUpClass()

    @classmethod
    def tearDownClass(self) -> None:
            print('\n\n###################################    Done Testing Endpoint Delay    #############################################\n\n')
            return super().tearDownClass()

    #Test 0 second delay route
    def test_01_no_delay(self) :
        #Create test with zero delay
        client.create_path('/test', 200, 'Test with no delay')
        expected = 0.1
        start_time = time.time()
        client.get_path('/test')
        end_time = time.time()
        actual = start_time - end_time - 2
        self.assertLessEqual(actual, expected)
        print(f"Real time: {(end_time - start_time - 2):2f}")
        client.delete_path('/test')


    #Create path with 2 second delay
    #Test 2 second delay route
    def test_02_two_second_delay(self) :
        client.create_path('/test1', 200, 'Test with 2 second delay', 2)
        expected = 2
        #Measure start time
        start_time = time.time()
        #Access route
        client.get_path('/test1')
        #Measure end time
        end_time = time.time()
        #Calculate the difference between start and end time(minus 2 seconds for average execution time)
        actual = end_time - start_time
        self.assertGreaterEqual(actual, expected)
        print(f"Real time: {(end_time - start_time):2f} seconds")
        client.delete_path('/test1')


    #Test 5 second time delay
    #See above 2 second test for more info
    def test_03_five_second_delay(self) :
        client.create_path('/test2', 200, 'Test with 5 second delay', 5)
        expected = 5
        #Measure start time
        start_time = time.time()
        #Access route
        client.get_path('/test2')
        #Measure end time
        end_time = time.time()
        #Calculate the difference between start and end time(minus 2 seconds for average execution time)
        actual = end_time - start_time
        self.assertGreaterEqual(actual, expected)
        print(f"Real time: {(end_time - start_time):2f} seconds")
        client.delete_path('/test2')

    def test_04_delay_format_invalid(self) :
        print('\nThis test tries to fail by creating an endpoint with a string as a delay value and expects a TypeError:')
        client.create_path('/test3', 200, 'Test with improper syntax', 'baddelay')
        self.assertRaises(TypeError)




if __name__ == '__main__' :
    unittest.main()
