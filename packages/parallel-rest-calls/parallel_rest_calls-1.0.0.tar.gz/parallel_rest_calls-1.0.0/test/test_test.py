import re
import requests_mock
from src.parallel_calls import ParallelCalls
import unittest

class TestParallelCalls(unittest.TestCase):
    
    @requests_mock.Mocker()
    def test_path_parallel_calls_ok(self, mocker):
        parallel_calls = ParallelCalls()
        ids = list(range(3))
        URL = "https://reqres.in/api/users"
        matcher = re.compile("https://reqres.in/api/users/*")
        mocker.register_uri('GET', matcher, json = {'a': 'b'})
        response = parallel_calls.path_calls(URL, ids)
        assert len(response) == 3
        assert response[0].get('status_code') != None
        assert response[0].get('result') != None

    @requests_mock.Mocker()
    def test_query_param_parallel_calls_ok(self, mocker):
        parallel_calls = ParallelCalls()
        ids = list(range(3))
        URL = "https://reqres.in/api/users?page="
        matcher = re.compile(r"https://reqres.in/api/users\?page=*")
        mocker.register_uri('GET', matcher, json = {'a': 'b'})
        response = parallel_calls.query_param_calls(URL, "page", ids)
        assert len(response) == 3
        assert response[0].get('status_code') != None
        assert response[0].get('result') != None

    @requests_mock.Mocker()
    def test_path_parallel_calls_non_200(self, mocker):
        parallel_calls = ParallelCalls()
        ids = list(range(3))
        URL = "https://reqres.in/api/users"
        matcher = re.compile("https://reqres.in/api/users/*")
        mocker.register_uri('GET', matcher, json = {'a': 'b'}, status_code = 403)
        response = parallel_calls.path_calls(URL, ids)
        assert len(response) == 3
        assert response[0].get('status_code') != 200
        assert response[0].get('result') == None
    
    @requests_mock.Mocker()
    def test_query_param_parallel_calls_non_200(self, mocker):
        parallel_calls = ParallelCalls()
        ids = list(range(3))
        URL = "https://reqres.in/api/users?page="
        matcher = re.compile(r"https://reqres.in/api/users\?page=*")
        mocker.register_uri('GET', matcher, json = {'a': 'b'}, status_code = 403)
        response = parallel_calls.query_param_calls(URL, "page", ids)
        assert len(response) == 3
        assert response[0].get('status_code') != 200
        assert response[0].get('result') == None

    @requests_mock.Mocker()
    def test_path_parallel_calls_exception(self, mocker):
        parallel_calls = ParallelCalls()
        ids = list(range(3))
        URL = "https://reqres.in/api/users"
        response = parallel_calls.path_calls(URL, ids)
        assert len(response) == 3
        assert response[0].get('status_code') == -1
        assert response[0].get('result') == None

    @requests_mock.Mocker()
    def test_query_param_parallel_calls_exception(self, mocker):
        parallel_calls = ParallelCalls()
        ids = list(range(3))
        URL = "https://reqres.in/api/users?page="
        response = parallel_calls.query_param_calls(URL, "page", ids)
        assert len(response) == 3
        assert response[0].get('status_code') == -1
        assert response[0].get('result') == None