"""Implements the "Agent" interface."""
import functools
import io
import json
import uuid
from typing import Dict, List, Any, Tuple, Union
from os.path import join
from datetime import datetime
import requests

from ia.gaius.genome_info import Genome


class AgentQueryError(BaseException):
    """Raised if any query to any node returns an error."""
    pass


class AgentConnectionError(BaseException):
    """Raised if connecting to any node returns an error."""
    pass


def _ensure_connected(f):
    @functools.wraps(f)
    def inner(self, *args, **kwargs):
        if not self._connected:
            raise AgentConnectionError(
                'Not connected to a bottle. You must call `connect()` on a AgentClient instance before making queries'
            )
        return f(self, *args, **kwargs)

    return inner


def _remove_unique_id(response: dict) -> dict:
    """Return *response* with the key 'unique_id' removed regardless of nesting."""
    if isinstance(response, dict):
        if 'unique_id' in response:
            del response['unique_id']
        for value in response.values():
            if isinstance(value, dict):
                _remove_unique_id(value)
    return response


class AgentClient:
    """Interface for interacting with bottles."""

    def __init__(self, bottle_info):
        """
        Provide bottle information in a dictionary.

        ex:
        from ia.gaius.AgentClient import AgentClient

        bottle_info = {'api_key': 'ABCD-1234',
                    'name': 'gaius-agent',
                    'domain': 'intelligent-artifacts.com',
                    'secure': False}

        bottle = AgentClient(bottle_info)
        bottle.connect()

        bottle.setIngressNodes(['P1'])
        bottle.setQueryNodes(['P1'])

        """
        self.session = requests.Session()
        self.genome = None
        self._bottle_info = bottle_info
        self.name = bottle_info['name']
        self._domain = bottle_info['domain']
        self._api_key = bottle_info['api_key']
        self.ingress_nodes = []
        self.query_nodes = []
        self._headers = {'X-API-KEY': self._api_key}
        self.all_nodes = []
        self._connected = False
        self.genome = None
        self.gaius_agent = None
        self.send_unique_ids = True
        self.summarize_for_single_node = True
        if 'secure' not in self._bottle_info or self._bottle_info['secure']:
            self._secure = True
            self._url = 'https://{name}.{domain}/'.format(**self._bottle_info)
        else:
            self._secure = False
            self._url = 'http://{name}.{domain}/'.format(**self._bottle_info)

    def __repr__(self) -> str:
        return (
            '<{name}.{domain}| secure: %r, connected: %s, gaius_agent: %s, \
                  ingress_nodes: %i, query_nodes: %i>'.format(
                **self._bottle_info
            )
            % (
                self._secure,
                self._connected,
                self.gaius_agent,
                len(self.ingress_nodes),
                len(self.query_nodes),
            )
        )

    def receive_unique_ids(self, should_set: bool = True) -> bool:
        self.send_unique_ids = should_set
        return self.send_unique_ids

    def connect(self) -> Dict:
        """Grabs the bottle's gaius_agent's genome for node definitions."""
        response_data = self.session.get(self._url + 'connect', verify=self._secure, headers=self._headers).json()
        if 'status' not in response_data or response_data['status'] != 'okay':
            self._connected = False
            raise AgentConnectionError("Connection failed!", response_data)

        self.genome = Genome(response_data['genome'])
        self.gaius_agent = response_data['genome']['agent']
        self.all_nodes = [{"name": i['name'], "id": i['id']} for i in self.genome.primitives.values()]
        if response_data['connection'] == 'okay':
            self._connected = True
        else:
            self._connected = False

        return {'connection': response_data['connection'], 'agent': response_data['genie']}

    def set_ingress_nodes(self, nodes: List = None) -> List:
        """Use list of primitive names to define where data will be sent."""
        if nodes is None:
            nodes = []
        self.ingress_nodes = [{'id': self.genome.primitive_map[node], 'name': node} for node in nodes]
        return self.ingress_nodes

    def set_query_nodes(self, nodes: List = None) -> List:
        """Use list of primitive names to define which nodes should return answers."""
        if nodes is None:
            nodes = []
        self.query_nodes = [{'id': self.genome.primitive_map[node], 'name': node} for node in nodes]
        return self.query_nodes

    def _query(
        self, query_method: Any, path: str, data: Union[dict, str] = None, nodes: List = None, unique_id: str = None
    ) -> Union[dict, Tuple[dict, str]]:
        """Internal helper function to make a REST API call with the given *query* and *data*."""
        if not self._connected:
            raise AgentConnectionError(
                'Not connected to a bottle. You must call `connect()` on a AgentClient instance before making queries'
            )
        result = {}
        if unique_id is not None:
            if data:
                data['unique_id'] = unique_id
            else:
                data = {'unique_id': unique_id}
                
        data = json.loads(json.dumps(data))
        
        if isinstance(nodes[0], str):
            nodes = [{'name': name, 'id': self.genome.primitive_map[name]} for name in nodes]
        for node in nodes:
            full_path = f'{self._url}{node["id"]}/{path}'
            try:
                if data is not None:
                    response = query_method(full_path, verify=self._secure, headers=self._headers, json={'data': data})
                else:
                    response = query_method(full_path, verify=self._secure, headers=self._headers)
                response.raise_for_status()
                response = response.json()
                if response['status'] != 'okay':
                    raise AgentQueryError(response['message'])
                if not self.send_unique_ids:
                    response = _remove_unique_id(response['message'])
                else:
                    response = response['message']
                if len(nodes) == 1 and self.summarize_for_single_node:
                    result = response
                else:
                    result[node['name']] = response
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        if unique_id is not None:
            return result, unique_id
        return result

    def set_summarize_for_single_node(self, value: bool):
        """When True, queries against a single node return responses directly instead of in a dict key."""
        self.summarize_for_single_node = value

    def observe(self, data: Dict, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Exclusively uses the 'observe' call."""
        if nodes is None:
            nodes = self.ingress_nodes
        return self._query(self.session.post, 'observe', data=data, nodes=nodes)

    def _observe_event(self, data: Dict, unique_id: str = None) -> Tuple[dict, str]:
        """Exclusively uses the 'observe' call."""
        results = {}
        uid = None
        if unique_id is None:
            unique_id = str(uuid.uuid4())
        for node, node_data in data.items():
            response, uid = self._query(self.session.post, 'observe', data=node_data, nodes=[node], unique_id=unique_id)
            results[node] = response
        return results, uid

    @_ensure_connected
    def observe_classification(self, data=None, nodes: List = None):
        """Send a classification to all nodes as a singular symbol in the last event.

        Sending the classification as a single symbol in the last event is the canonical way to classify a sequence.
        """
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.post, 'observe', data=data, nodes=nodes)

    def show_status(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return the current status of the bottle."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'status', nodes=nodes)

    def learn(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return the learn results."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'learn', nodes=nodes)

    def get_wm(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return information about Working Memory."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'working-memory', nodes=nodes)

    def get_predictions(self, unique_id: str = None, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return prediction result data."""
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.post, 'predictions', nodes=nodes, unique_id=unique_id)

    def clear_wm(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Clear the Working Memory of the Genie."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'working-memory/clear', nodes=nodes)

    def clear_all_memory(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Clear both the Working Memory and persisted memory."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'clear-all-memory', nodes=nodes)

    def get_percept_data(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return percept data."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'percept-data', nodes=nodes)

    def get_cognition_data(self, unique_id: str = None, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return cognition data."""
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.get, 'cognition-data', nodes=nodes, unique_id=unique_id)

    @_ensure_connected
    def change_genes(self, gene_data: Dict, nodes: List = None) -> Union[dict, Any]:
        """Change the genes in *gene_data* to their associated values.

        This will do live updates to an existing agent, rather than stopping an agent and starting a new one, as
        per 'injectGenome'.
        gene_data of form:

            {gene: value}

        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]

        result = {}
        for node in nodes:
            response = self.session.post(
                f"{self._url}{node['id']}/genes/change",
                verify=self._secure,
                headers=self._headers,
                json={'data': gene_data},
            ).json()
            if 'error' in response or response['status'] == 'failed':
                if len(nodes) == 1 and self.summarize_for_single_node:
                    raise AgentQueryError(response)
            self.genome.change_genes(node['id'], gene_data)
            if len(nodes) == 1 and self.summarize_for_single_node:
                return response['message']
            result[node['name']] = response['message']
        return result

    @_ensure_connected
    def get_gene(self, gene: str, nodes: List = None) -> Union[dict, Dict[Any, Dict[str, Any]]]:
        """Return the value for the gene *gene* on *nodes*."""
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(
                    f"{self._url}{node['id']}/gene/{gene}", verify=self._secure, headers=self._headers
                ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return {gene: response['message']}
                result[node['name']] = {gene: response['message']}
            except BaseException as exception:
                raise AgentQueryError(exception) from None

        return result

    @_ensure_connected
    def get_model(self, model_name: str, nodes: List = None) -> Union[dict, Any]:
        """Returns model with name *model_name*.

        Model name is unique, so it should not matter that we query all nodes, only
        one model will be found.
        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(
                    f"{self._url}{node['id']}/model/{model_name}", headers=self._headers, verify=self._secure
                ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result
    
    @_ensure_connected
    def delete_model(self, model_name: str, nodes: List = None) -> Union[dict, Any]:
        """Deletes model with name *model_name*.

        Model name is unique, so it should not matter that we query all nodes, 
        all its duplicates everywhere will be deleted.
        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.delete(
                    f"{self._url}{node['id']}/model/{model_name}", headers=self._headers, verify=self._secure
                ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result
    
    @_ensure_connected
    def update_model(self, model_name: str, model: Dict, nodes: List = None) -> Union[dict, Any]:
        """Returns model with name *model_name*.

        Model name is unique, so it should not matter that we query all nodes, 
        all its duplicates everywhere will be updated.
        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.put(
                    f"{self._url}{node['id']}/model/{model_name}", headers=self._headers, verify=self._secure,
                    json={'model': model}
                ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result

    @_ensure_connected
    def resolve_model(self, model_name: str, nodes: List = None) -> Union[dict, Any]:
        """Returns model with name *model_name*.

        Model name is unique, so it should not matter that we query all nodes, only
        one model will be found.
        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(
                    f"{self._url}{node['id']}/model/{model_name}", headers=self._headers, verify=self._secure
                ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result    

    def get_name(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return name of *nodes*."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'name', nodes=nodes)

    def get_time(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return time on *nodes*."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'time', nodes=nodes)

    @_ensure_connected
    def get_vector(self, vector_name: str, nodes: List = None) -> Union[dict, Dict[Any, Dict[str, Any]]]:
        """Return the vector with *vector_name* on *nodes* (it will be present on at most one)."""
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(
                    f"{self._url}{node['id']}/vector", headers=self._headers, verify=self._secure, json={'data': vector_name}
                ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result

    @_ensure_connected
    def increment_recall_threshold(self, increment: float, nodes: List = None) -> Dict[Any, Dict[str, Any]]:
        """Increment recall threshold by *increment* on *nodes*."""
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.post(
                    f"{self._url}{node['id']}/gene/increment-recall-threshold",
                    verify=self._secure,
                    headers=self._headers,
                    json={'increment': increment},
                ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                else:
                    self.genome.primitives[node['id']]['recall_threshold'] += increment
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return {"recall_threshold": response['message']}
                result[node['name']] = {"recall_threshold": response['message']}
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result

    def start_sleeping(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Tells *nodes* to start sleeping."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'sleeping/start', nodes=nodes)

    def stop_sleeping(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Wakes up sleeping *nodes*."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'sleeping/stop', nodes=nodes)

    def start_predicting(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Tells *nodes* to start predicting."""
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'predicting/start', nodes=nodes)

    def stop_predicting(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Tells *nodes* to stop predicting.

        Useful for faster training, but abstracted nodes will not learn.
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'predicting/stop', nodes=nodes)

    @_ensure_connected
    def ping(self, nodes: List = None) -> Union[dict, Any]:
        """Ping a node to ensure it's up."""
        if nodes is None:
            return self.session.get(f'{self._url}gaius-api/ping', headers=self._headers).json()
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
            results = {}
            for node in nodes:
                response = self.session.get(f"{self._url}{node['id']}/ping", verify=self._secure, headers=self._headers).json()
                if 'error' in response or response["status"] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise Exception("Request Failure:", response)
                    print("Failure:", {node['name']: response})
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                results[node['name']] = response["message"]
            return results
    
    @_ensure_connected
    def get_kbs(self, directory='./'):
        """Returns the KBs for the agent.
        This is a mongo-db and can be used to store or analyze locally.
        Choose the directory to save in with the directory keyword. Default is in './'."""
        _headers = self._headers
        _headers['Content-Encoding'] = 'gzip'
        archive = self.session.get(
                    f"{self._url}database", 
                    headers=_headers,
                    verify=self._secure
                )
        archive_file = join(directory, f'{self.gaius_agent}-{self.name}-{datetime.now()}-kb.archive.gz')
        with open(archive_file, 'wb') as f:
            f.write(archive.content)
        return f"Saved as {archive_file}"
    
    @_ensure_connected
    def get_kbs_as_json(self, nodes: List = None, directory='./'):
        if nodes is None:
            nodes = self.all_nodes
        output = self._query(requests.get, 'get_kb', nodes=nodes)
        filenames = []
        if isinstance(output, dict):
            archive_file = join(directory, f'{self.gaius_agent}-{self.name}-{nodes[0]["id"]}-{datetime.now()}-kb.json')
            filenames.append(archive_file)
            with open(archive_file, 'w') as f:
                    f.write(json.dumps(output))
        else:
            for i, item in enumerate(output):
                archive_file = join(directory, f'{self.gaius_agent}-{nodes[i]["id"]}-{datetime.now()}-kb.json')
                filenames.append(archive_file)
                with open(archive_file, 'w') as f:
                    f.write(json.dumps(item))
        
        return f"saved kbs as {', '.join(filenames)}"
    
    @_ensure_connected
    def put_kbs(self, archive_file):
        """Uploads KBs from local archive_file file.
        """
        _headers = self._headers
        _headers['Content-Encoding'] = 'gzip'
        _headers['Content-type'] = 'application/octet-stream'
        with open(archive_file, 'rb') as f:
            data = f.read()
            response = self.session.put(f'{self._url}database', 
                        headers=_headers,
                        verify=self._secure,
                        data=data)
        return response.json()

    def set_target_class(self, target_class: str, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Provide a target_class symbol for the searcher to look for.

        The searcher will ignore all other classes. This is a symbol that is in the last event of a classification
        sequence.
        """
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.post, 'set-target-class', nodes=nodes, data=target_class)

    def clear_target_class(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Clears target selection."""
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.post, 'clear-target-class', nodes=nodes)

    @_ensure_connected
    def tf_attach(self, name, config):
        return self.session.post(f'{self._url}/thinkflux/{name}/attach', data={'config' : config})
        
    
__all__ = (AgentConnectionError, AgentClient, AgentQueryError)
