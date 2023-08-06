"""Minimal testing interface for GAIuS"""
from copy import deepcopy
import datetime
import json
import os


from ia.gaius.data_ops import Data
from ia.gaius.tests import classification

class MinTest:
    def __init__(self, **kwargs):
        """
        Pass this a configuration dictionary as the argument such as:

        test_config = {'name':'backtest-classification',
                        'test_type': 'classification', ## 'classification' or 'utility'
                        'shuffle_data': True,
                        'fresh_start_memory': True, ## Clear all memory when starting and between runs
                        'learning_strategy': 'continuous', # None, 'continuous' or 'on_error'
                        'agent_client': agent_client,
                        'data_source': dataset, ## or provide 'data_directories' as iterable of data.
                        'percent_reserved_for_training': 20,
                        'percent_of_dataset_chosen': 100,
                        'total_test_counts': 1 }

        test = BackTest(**test_config)

        mongo_location provides the location of a mongo database where the test results will be stored.

        Option of either data_source or data_directories can be provided:

            data_source provided is a sequence of sequences of GDF objects.
            data_directories provided should be a list of directories containing files of GDF as json dumps.

        """
        self.configuration = kwargs
        self.errors = []
        self.name = str(kwargs['name'])
        self.test_type = kwargs['test_type']
        self.shuffle_data = kwargs['shuffle_data']
        self.learning_strategy = kwargs['learning_strategy']
        self.fresh_start_memory = kwargs['fresh_start_memory']
        self.agent_client = kwargs['agent_client']
        self.agent_client.summarize_for_single_node = False
        if 'data_directories' in self.configuration:
            self.data_directories = kwargs['data_directories']
            self.data_source = None
        elif 'data_source' in self.configuration:
            self.data_source = kwargs['data_source']
            self.configuration['data_source'] = 'from-source'
            self.data_directories = None
        self.percent_reserved_for_training = int(kwargs['percent_reserved_for_training'])
        self.percent_of_dataset_chosen = int(kwargs['percent_of_dataset_chosen'])
        self.total_test_counts = int(kwargs['total_test_counts'])
        self.current_test_count = 0
        
        # self.mongo_client = MongoClient(self.mongo_location)  # , document_class=OrderedDict)
        # # Collection storing the backtesting results is the bottle's name.
        # self.mongo_client.backtesting = self.mongo_client['{}-{}-{}'.format(
        #     self.name, self.bottle.genome.agent, self.bottle.name)]
        # self.test_configuration = self.mongo_client.backtesting.test_configuration
        # self.test_status = self.mongo_client.backtesting.test_status
        # self.test_errors = self.mongo_client.backtesting.test_errors
        # self.backtesting_log = self.mongo_client.backtesting.backtesting_log
        # self.interrupt_status = self.mongo_client.backtesting.interrupt_status
        
        if self.test_type == 'classification':
            self._tester = classification.Tester(**kwargs)
        
        else:
            self._tester = None
            # print(f"Unsupported test type: {self.test_type}")
            raise Exception(f"Unsupported test_type: {self.test_type}")
        
        if self.data_directories:
            self.data = Data(data_directories=self.data_directories)
        elif self.data_source:
            self.data = Data(dataset=self.data_source)
            
        self.data.prep(self.percent_of_dataset_chosen, self.percent_reserved_for_training, shuffle=self.shuffle_data)
        
        sequence_count = len(self.data.train_sequences) + len(self.data.test_sequences)
        
        self.number_of_things_to_do = self.total_test_counts * sequence_count
        
        self.number_of_things_done = 0
        
        self.test_configuration = {
            'name': self.name,
            'test_type': self.test_type,
            # 'utype': self.utype,
            'shuffle_data': self.shuffle_data,
            'learning_strategy': self.learning_strategy,
            'fresh_start_memory': self.fresh_start_memory,
            "agent_name": self.agent_client.name,
            "agent": self.agent_client.genome.agent,
            "ingress_nodes": self.agent_client.ingress_nodes,
            "query_nodes": self.agent_client.query_nodes
        }
        self.test_status = {}
        self.backtesting_log = []
        
        self.status = "not started"
        
        self.test_status = {'status': 'not started',
                            'number_of_things_to_do': self.total_test_counts * sequence_count,
                            'number_of_things_done': 0,
                            'current_test_count': self.current_test_count
                            }
        
        self.backtesting_log.append({"timestamp_utc": datetime.datetime.utcnow(), "status": "test-started"})

        
                                     
        print("Saving results for test locally")
        
    def _reset_test(self):
        """Reset the instance to the state it was in when created."""
        if self.data_directories:
            self.data = Data(data_directories=self.data_directories)
        elif self.data_source:
            self.data = Data(dataset=self.data_source)
        self.data.prep(self.percent_of_dataset_chosen, self.percent_reserved_for_training, shuffle=self.shuffle_data)
        self._tester.next_test_prep()
        
    def _end_test(self):
        """Called when the test ends."""
        self.status = "finished"
        nodes_status = self.agent_client.show_status()
        self.test_status = {'status': 'finished',
                            'nodes_status': nodes_status,
                            'number_of_things_to_do': self.number_of_things_to_do,
                            'number_of_things_done': self.number_of_things_to_do,
                            'current_test_count': self.current_test_count}
        
    def run(self):
        self.backtesting_log.append({"timestamp_utc": datetime.datetime.utcnow(), 
                                     "status": "run"})
        while self.current_test_count < self.total_test_counts:
            self.current_test_count += 1
            self._setup_training()
            for sequence in self.data.train_sequences:
                self._train(sequence)
                self.number_of_things_done += 1
                print(f'training: {self.number_of_things_done}')
                # self.progress.description = '%0.2f%%' % (100 * self.number_of_things_done / self.number_of_things_to_do)
        
            self._setup_testing()
            for sequence in self.data.test_sequences:
                self._test(sequence)
                self.number_of_things_done += 1
                print(f'testing: {self.number_of_things_done}')
                # self.progress.value = self.number_of_things_done
                # self.progress.description = '%0.2f%%' % (100 * self.number_of_things_done / self.number_of_things_to_do)

            if self.current_test_count < self.total_test_counts:
                self._reset_test()
            else:
                self._end_test()
        
    def _setup_training(self):
        """Setup instance for training."""
        self.backtesting_log.insert_one({"timestamp_utc": datetime.datetime.utcnow(), "status": "setupTraining"})
        self.status = "training"
        self.test_status.replace_one({}, {'status': 'training',
                                          'number_of_things_to_do': self.number_of_things_to_do,
                                          'number_of_things_done': self.number_of_things_done,
                                          'current_test_count': self.current_test_count}, upsert=True)
        if self.fresh_start_memory:
            self.agent_client.clear_all_memory()
        return 'ready'
    
    def _setup_training(self):
        """Setup instance for training."""
        self.backtesting_log.append({"timestamp_utc": datetime.datetime.utcnow(), "status": "setupTraining"})
        self.test_status = {'status': 'training',
                            'number_of_things_to_do': self.number_of_things_to_do,
                            'number_of_things_done': self.number_of_things_done,
                            'current_test_count': self.current_test_count}
        if self.fresh_start_memory:
            self.agent_client.clear_all_memory()
        return 'ready'
    
    def _train(self, sequence):
        """Train with the sequence in *sequence*."""
        if self.data_directories:
            self.backtesting_log.append({"timestamp_utc": datetime.datetime.utcnow(), 
                                         "status": "training", "file": os.path.basename(sequence)})
            with open(sequence) as f:
                sequence = [json.loads(data.strip()) for data in f if data]
                
        elif self.data_source:
            sequence = sequence
            self.backtesting_log.append({"timestamp_utc": datetime.datetime.utcnow(), "status": "training"})

        result_log_record = self._tester.train(sequence)
        result_log_record['trial'] = self.number_of_things_done
        result_log_record['run'] = self.current_test_count
        self.backtesting_log.append(deepcopy(result_log_record))
        return 'ready'
    
    def _setup_testing(self):
        """Set up the instance to begin backtesting."""
        self.backtesting_log.append({"timestamp_utc": datetime.datetime.utcnow(), 
                                     "status": "setupTesting"})
        self.status = "testing"
        self.test_status = {'status': 'testing',
                            'number_of_things_to_do': self.number_of_things_to_do,
                            'number_of_things_done': self.number_of_things_done,
                            'current_test_count': self.current_test_count}
        return 'ready'
    
    def _test(self, sequence):
        """Run the backtest on *sequence*."""
        ## get a sequence either from a file, or directly as a list:
        if self.data_directories:
            self.backtesting_log.append(
                {"timestamp_utc": datetime.datetime.utcnow(), 
                 "status": "testing", 
                 "file": os.path.basename(sequence)})
            with open(sequence) as f:
                sequence = [json.loads(data.strip()) for data in f if data]
        elif self.data_source:
            sequence = sequence
            self.backtesting_log.append({"timestamp_utc": datetime.datetime.utcnow(), 
                                         "status": "testing"})

        ## Test the sequence and record the results.
        result_log_record = self._tester.test(sequence)
        result_log_record['trial'] = self.number_of_things_done
        result_log_record['run'] = self.current_test_count
        self.backtesting_log.append(deepcopy(result_log_record))
        return 'ready'