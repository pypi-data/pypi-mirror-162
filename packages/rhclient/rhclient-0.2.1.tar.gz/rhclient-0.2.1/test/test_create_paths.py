# # DEPRECATED FUNCTIONALITY # #

# from src.pythonClient import PyRH_Client
# from multiprocessing import Process
# import unittest
# import os

# host = os.environ.get('RH_HOST', 'localhost')
# port = os.environ.get('RH_PORT', '5000')
# client = PyRH_Client(f"http://{host}:{port}")

# def getPathInfo(url) :
#       client.get_path(url)

      
# def deletePath(url) :
#       client.delete_path(url)
      
# def createPath(url) :
#       client.create_path(url)

# class create_paths_test(unittest.TestCase) :
      
#       @classmethod
#       def setUpClass(self) -> None:
#             print('\n\n###################################    Testing Creation of Multiple Paths    #############################################\n\n')
#             return super().setUpClass()
      
#       @classmethod
#       def tearDownClass(self) -> None:
#             client = None
#             print('\n\n###################################    Done Testing Multiple Path Creation    #############################################\n\n')
#             return super().tearDownClass()
      
            
#       def test_01_create_paths(self) :
            
#             path_data = [ 
#                   {'path': '/test', 'rc':200, 'return_value': 'test'},
#                   {'path': '/test2', 'rc':200, 'return_value': 'test2'},
#                   {'path': '/test3', 'rc':200, 'return_value': 'test3'},
#                   {'path': '/test4', 'rc':200, 'return_value': 'test4'}
#             ]
            
#             client.create_paths(path_data)
#             try :
#                   list = []
#                   for i in range(len(path_data)) :
#                         p = Process(target=getPathInfo, args=(f"{path_data[i]['path']}",))
#                         p.start()
#                         list.append(p)
#                         #p.join()
#                         #p.map(self.getPathInfo, ['/test', '/test2', '/test3', '/test4'])
#                   for i in range(len(list)) :
#                         list[i].join()
#             except :
#                   self.fail('One of the paths was improperly implemented.')
            
#             list = []
#             for i in range(len(path_data)) :
#                   p = Process(target=deletePath, args=(f"{path_data[i]['path']}",))
#                   p.start()
#                   list.append(p)
#                   #p.join()
#                   #p.map(self.getPathInfo, ['/test', '/test2', '/test3', '/test4'])
#             for i in range(len(list)) :
#                   list[i].join()

#       # def test_01_create_path(self) :
            
#       #       path_data = [ 
#       #             {'path': '/test', 'rc':200, 'return_value': 'test'},
#       #             {'path': '/test2', 'rc':200, 'return_value': 'test2'},
#       #             {'path': '/test3', 'rc':200, 'return_value': 'test3'},
#       #             {'path': '/test4', 'rc':200, 'return_value': 'test4'}
#       #       ]
            
#       #       for i in range(len(path_data)) :
#       #             p = Process(target=deletePath, args=(f"{path_data[i]['path']}",))
#       #             p.start()
#       #             list.append(p)
#       #             #p.join()
#       #             #p.map(self.getPathInfo, ['/test', '/test2', '/test3', '/test4'])
#       #       for i in range(len(list)) :
#       #             list[i].join()
            
#       #       try :
#       #             list = []
#       #             for i in range(len(path_data)) :
#       #                   p = Process(target=getPathInfo, args=(f"{path_data[i]['path']}",))
#       #                   p.start()
#       #                   list.append(p)
#       #                   #p.join()
#       #                   #p.map(self.getPathInfo, ['/test', '/test2', '/test3', '/test4'])
#       #             for i in range(len(list)) :
#       #                   list[i].join()
#       #       except :
#       #             self.fail('One of the paths was improperly implemented.')
            
#       #       list = []
#       #       for i in range(len(path_data)) :
#       #             p = Process(target=deletePath, args=(f"{path_data[i]['path']}",))
#       #             p.start()
#       #             list.append(p)
#       #             #p.join()
#       #             #p.map(self.getPathInfo, ['/test', '/test2', '/test3', '/test4'])
#       #       for i in range(len(list)) :
#       #             list[i].join()
            
# if __name__ == '__main__' :
#       unittest.main()