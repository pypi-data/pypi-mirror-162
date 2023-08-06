
# import xml.etree.ElementTree as ET
import webbrowser
import requests
from pathlib import Path
import time
from typing import Any, Dict, List
import logging
import os
import json
import httpx

class RbAutoML():

    def __init__(self, domain, token, protocol='https://', verify=True):
        """
        Initialise a RbAutoML object passing in the domain and authorisation token to be
        used whenever making calls to the Rest API.
        :param domain: the domain to send requests to i.e. beta.rbautoml.com
        :param token: all API requests require token authorisation
        """
        self.domain = domain
        self.token = token
        self.protocol = protocol
        self.verify = verify
        self.limits = httpx.Limits(max_keepalive_connections=5, max_connections=10,
                              keepalive_expiry=5000)
        self.headers = self._get_headers()

    def delete_trainer(self, trainer: int = None, name: str = None):
        """
        Delete trainer setups by id or name. Note multiple trainers with this name
        will be deleted where no id is specified.
        :param id: the id of the trainer record wishing to be deleted
        :param lat2: the name of the trainer record(s) to be deleted
        :return: array of integers representing the ids of deleted records
        """

        result = []
        delete_ids = []
        if trainer:
            delete_ids = [trainer]
        elif name:
            url = os.path.join(self.protocol, self.domain, 'eveml_config', 'trainers', '')
            payload = {"name": name}

            with httpx.Client(limits=self.limits, verify=self.verify) as client:
                response = client.get(url, headers=self.headers, params=payload)
            # response = requests.request("GET", url, headers=headers, data=json.dumps(payload),
            #                             verify=self.verify)
            for trainer in response.json():
                delete_ids.append(trainer['id'])
        else:
            raise ValueError("function must be called with id or name")

        for trainer_id in delete_ids:
            url = os.path.join(self.protocol, self.domain, 'eveml_config', 'trainers', str(trainer_id), '')
            with httpx.Client(limits=self.limits, verify=self.verify) as client:
                response = client.delete(url, headers=self.headers)

            if response.status_code == 204:
                result.append(trainer_id)

        return result


    def _get_headers(self):
        return {
            'Authorization': 'Bearer {0}'.format(self.token),
            'Content-Type': 'application/json',
        }

    def new_trainer(self, name: str, subject: str, type: str = 'binary classification',
                    train_to_test_split: str = '3/1', description: str = ''):
        """
        Create a new trainer setup. Then datasets can be attached before training ML models
        :param name: the name to be associated with the trainer setup
        :param subject: this the subject of the prediction i.e. a prediction to buy something
        would have a subject of person, so a person will buy X = 80% probability
        :param type: this is the kind of ML to take place, currently only binary classification
        is available (this is the default)
        :param train_to_test_split: Defaults to 3/1 meaning 75% of the data is used to train and
        25% is used to evaluate performance. Can have a third value i.e. 3/1/1 in this case 60%
        is used to train, 20% is used to evaulate and 10% is used to test the completed models to
        minimise any chance of overfitting not being visible in final performance results.
        :param description: provide a free text description of the trainer.
        :return: the trainer object created. This item contains the Trainer's id, name, subject,
        date_created, train_to_test_split, and description.
        """
        # Create the trainer record
        url = os.path.join(self.protocol, self.domain, 'eveml_config', 'trainers', '')
        payload = {
            "name": name,
            "subject": subject,
            "type": type,
            "train_to_test_split": train_to_test_split,
            "description": description,
            "data_set": []
        }

        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.post(url, headers=self.headers, content=json.dumps(payload),
                                   timeout=httpx.Timeout(1000))
        # response = requests.request("POST", url, headers=headers, data=json.dumps(payload),
        #                             verify=self.verify)
        if response.status_code == 201:
            return response.json()
        else:
            raise ValueError("Failed to create trainer")

    def upload_dataset(self, file_location: Dict, source_type: str = 'csv',
                       filename: str = None, replace: bool = False):
        """
        Pass a csv file to AutoML to be saved and then used as a dataset associated with a trainer.
        Returned will be the filename used to save the dataset.
        :param file_location: the relative path to the csv file to upload
        :param source_type: Currently only 'csv' is supported
        :param filename: the file name to use if the filename in the file_location parameter should
        not be used.
        :param replace: if the filename exists as a dataset already then by default it is not 
        replaced but rather simply the filename is returned. State True if looking to replace the
        existing filename with this filename. 
        :return: The filename uploaded and to be used to attach the dataset to a trainer's data
        setup.
        """
        if not filename:
            filename = Path(file_location).name
        
        # Check file isn't above size limit
        size = os.stat(file_location).st_size
        if size > 5242880:
            raise ValueError('Maximum csv file size is 50MB')

        url = os.path.join(self.protocol, self.domain, 'eveml_config', 'data_sets', 'upload_data',
                           '')
        payload = {
            "source_type": source_type,
            "replace": replace
        }
        if file_location:
            files = {'upload-file': (filename, open(file_location, 'rb'))}
        else:
            raise NotImplementedError('Currently only csv files can be used, more options will ' +
                                      'come in the future')

        response = requests.post(url, files=files, data=payload,
                                 headers={'Authorization': 'Bearer {0}'.format(self.token)})
        if response.status_code == 201:
            return response.json()
        else:
            raise ValueError("Failed to create dataset")

    def list_datasets(self):
        """
        Returns a list of uploaded datasets.
        :return: a list of uploaded datasets
        """
        url = os.path.join(self.protocol, self.domain, 'eveml_config', 'data_sets', 'list', '')

        response = requests.get(url, headers={'Authorization': 'Bearer {0}'.format(self.token)})
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError("Failed to get list of datasets")

    def add_dataset_to_trainer(self, trainer: int, source_type: str ='csv', filename: str = None):
        """
        Create a new dataset associated with a trainer. The dataset will detail where to find the
        data to be used to train the models.
        :param trainer: the id of the trainer to associate the dataset with
        :param source: this storage type used to hold the dataset's data. Currently only
        'gcp_storage' is supported.
        :param file_location: the path to a csv file.
        :return: integer of the dataset id created. This is then used to attach column details to.
        """
        url = os.path.join(self.protocol, self.domain, 'eveml_config', 'data_sets', '')
        payload = {
            "trainer": trainer,
            "filename": filename,
            "source_type": source_type
        }

        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.post(url, headers=self.headers, content=json.dumps(payload),
                                   timeout=httpx.Timeout(1000))

        if response.status_code == 201:
            return response.json()
        else:
            raise ValueError("Failed to create dataset")

    def set_columns_to_dataset(self, dataset: int, column_dict: Dict[str, List] = None,
                               column_array: List[Dict[str, Any]] = None):
        """
        Using the columns dictionary iterate through creating columns using the 
        add_column_to_dataset() function. Example columns = {'column_index': [0,3,5],
        'attribute_name': ['Price', 'Qty', 'Type']....} would create three columns.
        Dictionary must have keys for all add_column_to_dataset() inputs - "column_index,
        attribute_name, category_type, attribute_type, fixed_value_count, target, selected,
        fill_none_value, value_for_none" and array values all with equal length.
        """
        result = []
        if column_dict:
            for index in range(len(column_dict['column_index'])):
                result.append(self.add_column_to_dataset(
                    dataset=dataset,
                    column_index=column_dict['column_index'][index],
                    attribute_name=column_dict['attribute_name'][index],
                    category_type=column_dict['category_type'][index],
                    attribute_type=column_dict['attribute_type'][index],
                    fixed_value_count=column_dict['fixed_value_count'][index],
                    target=column_dict['target'][index],
                    selected=column_dict['selected'][index],
                    fill_none_value=column_dict['fill_none_value'][index],
                    value_for_none=column_dict['value_for_none'][index]))
        elif column_array:
            for item in column_array:
                result.append(self.add_column_to_dataset(
                    dataset=dataset, **item))
        else:
            raise ValueError("must pass in a value for column_dict or column_array value")
        return result

    def add_column_to_dataset(self, dataset: int, column_index: int, attribute_name: str,
                              category_type: str, attribute_type: str,
                              fixed_value_count: int = None, target: bool = False,
                              selected: bool = True, fill_none_value: str = None,
                              value_for_none: str = None):
        """
        Create a column definition associated with a dataset. For every column in a dataset
        there must be a column definition. Column Definitons can be assigned as selected False
        to indicate they should not be used at model training time.
        :param dataset: the id of the dataset to associate the column with
        :param column_index: the first column requires an column_index of 0, second 1, etc.
        :param attribute_name: the name to use for this column, it does not need to correlate with
        the column's actual header, note these must not contains special characters. 
        :param category_type: a value of 'nominal', 'ordinal', 'interval' or 'ratio'. Defaults to
        'nominal'. Nominal is general text although can be a numerical representation where the
        numeric has no mathematical relevance. Ordinal is ordered categories such as Grades A - F,
        Interval differences have meaning so for example temperature in celsius or farenhuit. Ratio
        - most numerics such as weight, price, etc.
        :param attribute_type: a value of 'int', 'float', 'categoric', 'date', or 'boolean'
        :param fixed_value_count: If this field has a distinct count of possible values then
        specify this number, i.e. for a month column there will only ever be 12 possible values.
        If it's possible the number could grow then leave this as the 'None' default.
        :param target: this is the column that is to be predicted in the future using the trained
        model. Known as label and target. Default False. One and only one (currently) column in a
        dataset must be set as the target. 
        :param selected: Default True. Indicates whether this column will be used as part of the
        auto ml processes.
        :param fill_none_value: when a column may contain blanks then a value can be entered that
        will be used in these instances. This applies a training and prediction time. Additionally
        a strategy can be defined so one of '*mode', '*mean', '*median', '*min', '*max' or '*zero'.
        If for example '*max' is given as the fill_none_value of a price column then the highest
        price in the column will be used when no price is available.
        :param value_for_none: when a value is used in the column i.e. 'Unknown' to indicate there
        is no value then this value is the 'value for none'. Using this these instances will be set
        to None and can then be influenced by fill_none_value for example.
        :return: integer of the trainer id created. This is then used to attach datasets and instruct
        models to be created.
        """
        url = os.path.join(self.protocol, self.domain, 'eveml_config', 'columns', '')
        payload = {
            "data": str(dataset),
            "column_index": str(column_index),
            "attribute_name": attribute_name,
            "category_type": category_type,
            "attribute_type": attribute_type,
            "fixed_value_count": fixed_value_count,
            "target": target,
            "selected": selected,
            "fill_none_value": fill_none_value,
            "value_for_none": value_for_none
        }

        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.post(url, headers=self.headers, content=json.dumps(payload))
        # response = requests.request("POST", url, headers=headers, data=json.dumps(payload),
        #                             verify=self.verify)
        if response.status_code == 201:
            return response.json()
        else:
            raise ValueError("Failed to create column definition")

    def train_models(self, trainer: int):
        """
        Using the trainer configuration with dataset(s) and columns trigger the automl pipeline
        process to build numerous models returning the model uuids of each algorithms best
        performing model. Currently performance is based purely on binary accuracy therefore
        a balanced target column is important. The returned uuids can subsequently be used to
        retrieve predictions and the engineering report detailing training data analysis and
        model performance.
        :param trainer: the id of the trainer to build ML models for
        :return: model training results including a list of uuids refering to models built.
        There is also a list of the algorithms in the same order as the related model uuid.
        """
        logging.basicConfig(level=logging.DEBUG) 
        url = os.path.join(self.protocol, self.domain, 'eveml_engineer', 'train-result',
                           'build_models', '')
        payload = {
            "trainer": str(trainer)
        }

        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.post(url, headers=self.headers, content=json.dumps(payload),
                                   timeout=httpx.Timeout(5000), follow_redirects=True)

        if response.status_code == 200:

            train_result = response.json()
            start = end = time.time()
            result = ''
            url = os.path.join(self.protocol, self.domain, 'eveml_engineer', 'train-result',
                                str(train_result['id']), 'build_status', '')

            errors = 0
            while result not in ['Successful', 'Unsuccessful'] and end - start < 7200:
                time.sleep(30)
                result = self._get_build_status(url, client, errors)
                end = time.time()
        else:
            raise ValueError("Failed to start model training")

        if result == 'Successful':
            results = self._get_model_instances(train_result)
        
        return results
    
    def best_model(self, models):
        result = None
        best_score = 0
        for model in models:
            if model['accuracy'] > best_score:
                result = model
                best_score = model['accuracy']
        return result

    def make_prediction(self, input_data, model=None, model_id=None):
        if not model and not model_id:
            raise ValueError('model and model_id cannot be None')

        if model:
            model_id = model['model_id']

        url = os.path.join(self.protocol, self.domain, 'eveml_predict', 'predict', '')

        payload = {'ml_instance_id': model_id, 'model_input': input_data},
        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.post(url, headers=self.headers, content=json.dumps(payload),
                                   timeout=httpx.Timeout(5000), follow_redirects=True)

        if response.status_code == 201:
            return response.json()['results']

        raise ValueError('An error occurred trying to make prediction')

    def make_prediction_by_file(self, input_file, model=None, model_id=None,
                                output_file='prediction_output.csv', source_type='csv'):
        if not model and not model_id:
            raise ValueError('model and model_id cannot be None')

        if model and not model_id:
            model_id = model['model_id']

        # Check file isn't above size limit
        size = os.stat(input_file).st_size
        if size > 5242880:
            raise ValueError('Maximum csv file size is 50MB')

        url = os.path.join(self.protocol, self.domain, 'eveml_predict', 'predict', '')

        payload = {'ml_instance_id': model_id, 'output_file': output_file,
                   'source_type': source_type}
        files = {'input_file': open(input_file, 'rb')}

        response = requests.post(url, files=files, data=payload,
                                 headers={'Authorization': 'Bearer {0}'.format(self.token)})

        if response.status_code == 200:
            with Path(output_file) as filename:
                filename.write_bytes(response.content)
                logging.info('Saved predictions by file results to {0}'.format(filename))
                if open:
                    url = ('file://' + os.path.realpath(filename))
                    webbrowser.open_new_tab(url)
        else:
            logging.error('An error occurred trying to make predictions by passing in file')

    def download_model_confusion_matrix_graph(self, model, open=True,
                                              to_filename='confusion_matrix.jpg'):
        return self.download_model_graph(model, 'confusion matrix graph', open=open,
                                         to_filename=to_filename)

    def download_feature_representation_graph(self, model, column, open=True,
                                              to_filename='feature_representation_graph.jpg'):
        return self.download_model_graph(model, 'feature representation graph', open=open,
                                         to_filename=to_filename, name=column)

    def download_model_graph(self, model, graph_description, open=True,
                             to_filename='model_report.pdf', name=None):
        # Build report so graph is definitely available
        payload = {'ml_instance_id': str(model['model_id']), 'element': 'engineer report'}
        url = os.path.join(self.protocol, self.domain, 'eveml_explain', 'model-element',
                           'engineer-report', '')

        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.post(url, headers=self.headers, content=json.dumps(payload),
                                   timeout=httpx.Timeout(1000), follow_redirects=True)
        if response.status_code == 201:
            pass
        else:
            raise ValueError('Could not get report')

        payload = {'ml_instance_id': str(model['model_id']),
                   'element': graph_description}
        if name:
            payload['name'] = name
        url = os.path.join(self.protocol, self.domain, 'eveml_explain', 'model-element',
                           'download-model-item', '')

        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.get(url, headers=self.headers, params=payload,
                                  timeout=httpx.Timeout(1000), follow_redirects=True)
        if response.status_code == 200:
            with Path(to_filename) as filename:
                filename.write_bytes(response.content)
                logging.info('downloaded report to {0}'.format(filename))
                if open:
                    url = ('file://' + os.path.realpath(filename))
                    webbrowser.open_new_tab(url)
        else:
            logging.error('Failed to download {0}'.format(graph_description))
        return response

    def download_model_report(self, model, open=True, to_filename='model_report.pdf'):
        # Build reports
        payload = {'ml_instance_id': str(model['model_id']), 'element': 'engineer report'}
        url = os.path.join(self.protocol, self.domain, 'eveml_explain', 'model-element',
                           'engineer-report', '')

        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.post(url, headers=self.headers, content=json.dumps(payload),
                                   timeout=httpx.Timeout(1000), follow_redirects=True)
        if response.status_code == 201:
            pass
        else:
            raise ValueError('Could not get report')

        payload = {'ml_instance_id': str(model['model_id']),
                   'element': 'engineer report'}
        url = os.path.join(self.protocol, self.domain, 'eveml_explain', 'model-element',
                           'download-model-item', '')

        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.get(url, headers=self.headers, params=payload,
                                  timeout=httpx.Timeout(1000), follow_redirects=True)
        if response.status_code == 200:
            with Path(to_filename) as filename:
                filename.write_bytes(response.content)
                logging.info('downloaded report to {0}'.format(filename))
                if open:
                    url = ('file://' + os.path.realpath(filename))
                    webbrowser.open_new_tab(url)
        else:
            logging.error('Failed to download engineer report')
        return response

    def download_knowledge_map(self, model, filename='knowledge_map.xml'):
        payload = {'instance_id': model['model_id']}

        url = os.path.join(self.protocol, self.domain, 'eveml_ext_rainbird', 'rblang',
                           'generate_rblang', '')

        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.post(url, headers=self.headers, content=json.dumps(payload),
                                   timeout=httpx.Timeout(1000), follow_redirects=True)

        if response.status_code == 200:
            # Save rblang to file
            with open(filename, "wb") as f:
                logging.debug('RbLang:\n{0}'.format(response.json()['rblang'])) 
                f.write(bytearray(response.json()['rblang'], 'utf-8'))
                logging.info('Knowledge map saved to file: {0}'.format(Path(filename).resolve()))
            return response

        raise ValueError('An error occurred trying to download knowledge map')

    def _get_model_instances(self, train_result):
        results = []
        url = os.path.join(self.protocol, self.domain, 'eveml_engineer', 'train-result',
                                str(train_result['id']), '')
        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            response = client.get(url, headers=self.headers)
            if response.status_code == 200:
                for model in response.json()['instances']:
                    url = os.path.join(self.protocol, self.domain, 'eveml_engineer',
                                           'ml-instance', model, '')
                    response = client.get(url, headers=self.headers)
                    if response.status_code == 200:
                        item = response.json()
                        results.append({'model_id': item['id'],
                                        'accuracy': item['accuracy_score'],
                                        'algorithm': item['algorithm']})
        return results

    def _get_build_status(self, url, client, error):
        with httpx.Client(limits=self.limits, verify=self.verify) as client:
            try:
                build_update = client.get(url, headers=self.headers)
                if build_update.status_code == 200:
                    status = build_update.json()
                    # logging.info("""***Model Training Progress***
                    print("""***Model Training Progress***
'Initial Data Preparation': {0}
'Data Analysis': {1}
'Transform Train Evaluate': {2}
'Save Results': {3}""".format(
    status['tasks']['Initial Data Preparation'],
    status['tasks']['Data Analysis'],
    status['tasks']['Transform Train Evaluate'],
    status['tasks']['Save Results']))
                    result = status['status']
                else:
                    raise ValueError("Cannot get training progress")
                return result
            except:
                if error > 3:
                    raise ValueError("Stopped getting build updates after multiple failures getting status")
                else:
                    error += 1
