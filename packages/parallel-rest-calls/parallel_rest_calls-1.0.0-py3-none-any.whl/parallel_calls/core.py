import requests
from concurrent.futures import ThreadPoolExecutor, wait

class ParallelCalls:
    def __init__(self, number_of_threads=10):
        self.number_of_threads = number_of_threads

    def _get_single_value(self, URL, resource_id, query_param_name=None):
        ret_val = {}
        try:
            if query_param_name:
                URL = f"{URL}?{query_param_name}={resource_id}"
            else:
                URL = f"{URL}/{resource_id}"
            response = requests.get(URL)
            ret_val['status_code'] = response.status_code
            
            if response.status_code == 200:
                ret_val['result'] = response.json()
            else:
                ret_val['result'] = None
        except:
            ret_val = {'status_code': -1, 'id': resource_id, 'result': None}
        return ret_val

    def _aggregate_responses(self, done):
        result = []
        for item in done:
            result.append(item.result())
        return result

    def path_calls(self, URL, resource_ids):
        with ThreadPoolExecutor(self.number_of_threads) as pool:
            futures = [pool.submit(self._get_single_value, URL, resource_id) for resource_id in resource_ids]
            done, _ = wait(futures)
        return self._aggregate_responses(done)

    def query_param_calls(self, URL, query_param_name,  resource_ids):
        with ThreadPoolExecutor(self.number_of_threads) as pool:
            futures = [pool.submit(self._get_single_value, URL, resource_id, query_param_name) for resource_id in resource_ids]
            done, _ = wait(futures)
        return self._aggregate_responses(done)