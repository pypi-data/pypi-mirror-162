# This software is the sole property of Prime Solutions Group, Inc.

# Project Title:
__REST Harness Python Client__

REST Harness is a tool to stand in the place of another REST service. This can be used to Mock out a service that doesn't exist yet, or where we need to reproduce a particular set of inputs from an opaque service. It can also serve as a simple shared cache. This library contains a client that can be used to interact with the REST Harness web server.

# Getting Started:
__Requirements/Built with:__<br>
Python3<br>
requests
## Import
__Usage: from rhclient import client__<br>
__client.configUrl("base url")__
(before configuration, base url is http://localhost:5000)
## Methods
__(Subject to change)__

### create_path(path, rc, return_value, delay=0)
<hr>

#### Parameters:
__path__ : required, specifies the path of the endpoint you would like to create<br>
__rc__ : required, specifies the return code you would like to receive upon hitting the created endpoint<br>
__return_value__ : required, specifies the value you would like to return from the created endpoint<br>
__delay__ : optional, can be used to force an endpoint to wait for a specified amount of time before returning its contents.(useful for mimicking a bad connection)

#### Description
Creates an endpoint on a REST Harness web server given parameters as information
#### Examples:
> client.create_path("/test", 200, "test data")<br>
Creates an endpoint at /test that returns "test data" upon access.<br>
> client.create_path("/test", 203, {"prop1" : "value1", "prop2" : "value2"}, 3)<br>
Creates an endpoint at /test that returns the provided JSON data after a 3 second delay upon access.

### create_paths(path)
<hr>

#### Parameters:
__path__ : required, contains all data of each path you would like to create in a JSON object, list, or other compatible data structure

#### Description:
Creates multiple endpoints given a list of endpoints and their parameters

#### Examples:
> client.create_paths({"/path1" : {"delay" : 0, "rc" : 200, "return_value" : "test test"}, "/path2" : {"delay" : 0, "rc" : 204, "return_value" : "test test"}, "/path3" : {"delay" : 2, "rc" : 200, "return_value" : "returned something"}, "/path4" : {"delay" : 1, "rc" : 202, "return_value" : "test something"},})<br>
Creates 4 endpoints: /path1, /path2, /path3, and /path4 which return their corresponding return codes and return values after a given delay.

### get_path(path)
<hr>

#### Parameters:
__path__ : required, specifies the path of the endpoint you would like to get data from

#### Description:
Hits an endpoint and returns the information associated with it.

#### Examples:
> client.create_path("/test", 200, "test data")<br>
> ...(some code)<br>
> client.get_path("/test")<br>
Creates an endpoint at /test, then hits the endpoint and returns "test data" upon access.<br>

> client.create_path("/test", 203, {"prop1" : "value1", "prop2" : "value2"}, 3)<br>
> ...(some code)<br>
> client.get_path("/test")<br>
Creates an endpoint at /test, then hits the endpoint and returns the JSON return value after a 3 second delay.

### get_all()
<hr>

#### Parameters
N/A

#### Description:
Gets all information from all created paths and returns it in a JSON format.

#### Examples:
> client.create_path("/test", 200, "test data")<br>
> client.create_path("/test2", 203, {"prop1" : "value1", "prop2" : "value2"}, 3)<br>
> ...(some code)<br>
> client.get_path("/test")<br>
Creates an endpoint at /test and /test2, then gets all information associated with both endpoints(no programmable delay) as a JSON object.

### update_path(path, rc, return_value, delay=0)
<hr>

#### Parameters:
__path__ : required, specifies the path of the endpoint you would like to update<br>
__rc__ : required, specifies the return code you would like to receive upon hitting the updated endpoint<br>
__return_value__ : required, specifies the value you would like to return from the updated endpoint <br>
__delay__ : optional, can be used to force an endpoint to wait for a specified amount of time before returning its contents.(useful for mimicking a bad connection)

#### Description
Updates an endpoint on a REST Harness web server given parameters as information
#### Examples:
> client.create_path("/test", 200, "test data")<br>
> client.update_path("/test", 203, {"prop1" : "value1", "prop2" : "value2"}, 3)<br>
Creates an endpoint at /test, then updates its return value and return code so that it returns different values when hit

### delete_path(path)
<hr>

#### Parameters:
__path__ : required, specifies the path of the endpoint you would like to delete

#### Description
Deletes an endpoint on a REST Harness web server given a path as a parameter

#### Examples:
> client.create_path("/test", 200, "test data")<br>
> ...(some code)<br>
> client.delete_path("/test")<br>
Deletes the /test endpoint from the REST Harness server.

# Notes:
To be determined at a later date.
