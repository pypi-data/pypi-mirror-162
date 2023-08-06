from stochasticx.deployment.deployments import Deployments
from stochasticx.utils.logging import configure_logger

import requests

logger = configure_logger(__name__)


class InferenceStatus:
    ALIVE = "alive"
    READY = "ready"
    DOWN = "down"


class InferenceModel:
    def __init__(
        self,
        deployment_id
    ):
        self.deployment_id = deployment_id
        self.deployment = Deployments.get_deployment(self.deployment_id)
        self.task_type = self.deployment.get_task_type()
        deployment_status = self.deployment.get_status()
        
        assert self.deployment is not None, "This deployment is not available"
        
        assert deployment_status == "running", "InferenceModel object cannot be created until the deployment has been successfully created"
        
    def get_status(self):
        return self.deployment.get_status()
        
    def get_task_type(self):
        return self.task_type
    
    def inference(self, *args, **kwargs):
        raise NotImplementedError("This method should be implemented by the child class")
    
    
class SequenceClassificationModel(InferenceModel):
    def __init__(
        self,
        deployment_id
    ):
        super().__init__(deployment_id)
        
    def format_inputs(self, texts):
        return {
            "inputs": [{
                "name": "text",
                "datatype": "BYTES",
                "shape": [1, len(texts)],
                "data": texts
            }]
        }
    
    def format_output(self, outputs):
        outputs = outputs.get("outputs")
        if outputs is not None and isinstance(outputs, list):
            labels, scores = outputs[0], outputs[1]
            return labels.get("data"), scores.get("data")
        
    
    def inference(self, texts):
        model_inputs = self.format_inputs(texts)
        endpoint_url = self.deployment.get_endpoint()
        api_key = self.deployment.get_api_key()
        
        assert endpoint_url is not None
        assert api_key is not None
        
        auth_header = {
            "apiKey": api_key
        }
        
        r = requests.post(endpoint_url, headers=auth_header, json=model_inputs)
        r.raise_for_status()
        
        outputs = r.json()
        labels, scores = self.format_output(outputs)
        
        return labels, scores
    

class QuestionAnsweringModel(InferenceModel):
    def __init__(self, deployment_id):
        super().__init__(deployment_id)
        
    def format_inputs(self, questions, contexts):
        return {
            "inputs": [
                {
                    "name": "question",
                    "datatype": "BYTES",
                    "shape": [1, len(questions)],
                    "data": questions
                },
                {
                    "name": "text",
                    "datatype": "BYTES",
                    "shape": [1, len(contexts)],
                    "data": contexts
                }
            ]
        }
    
    def format_output(self, outputs):
        outputs = outputs.get("outputs")
        if outputs is not None and isinstance(outputs, list):
            answers = outputs[0]
            return answers.get("data")
        
    def inference(self, questions, contexts):
        model_inputs = self.format_inputs(questions, contexts)
        endpoint_url = self.deployment.get_endpoint()
        api_key = self.deployment.get_api_key()
        
        assert endpoint_url is not None
        assert api_key is not None
        
        auth_header = {
            "apiKey": api_key
        }
        
        r = requests.post(endpoint_url, headers=auth_header, json=model_inputs)
        r.raise_for_status()
        
        outputs = r.json()
        answers = self.format_output(outputs)
        
        return answers
        
        
class SummarizationModel(InferenceModel):
    def __init__(self, deployment_id):
        super().__init__(deployment_id)
        
    def format_inputs(self, texts, min_lengths, max_lengths):
        return {
            "inputs":[
                {
                    "name":"text",
                    "datatype":"BYTES",
                    "shape":[1, len(texts)],
                    "data":texts
                },
                {
                    "name":"min_length",
                    "datatype":"INT32",
                    "shape":[1, len(min_lengths)],
                    "data": min_lengths
                },
                {
                    "name":"max_length",
                    "datatype":"INT32",
                    "shape":[1, len(max_lengths)],
                    "data": max_lengths
                }
            ]
        }
    
    def format_output(self, outputs):
        outputs = outputs.get("outputs")
        if outputs is not None and isinstance(outputs, list):
            summaries = outputs[0]
            return summaries.get("data")
        
    def inference(self, texts, min_lengths, max_lengths):
        model_inputs = self.format_inputs(texts, min_lengths, max_lengths)
        endpoint_url = self.deployment.get_endpoint()
        api_key = self.deployment.get_api_key()
        
        assert endpoint_url is not None
        assert api_key is not None
        
        auth_header = {
            "apiKey": api_key
        }
        
        r = requests.post(endpoint_url, headers=auth_header, json=model_inputs)
        r.raise_for_status()
        
        outputs = r.json()
        summaries = self.format_output(outputs)
        
        return summaries
       

class TranslationModel(InferenceModel):
    def __init__(self, deployment_id):
        super().__init__(deployment_id)
        
    def format_inputs(self, texts, max_lengths):
        return {
            "inputs":[
                {
                    "name":"text",
                    "datatype":"BYTES",
                    "shape":[1, len(texts)],
                    "data":texts
                },
                {
                    "name":"max_length",
                    "datatype":"INT32",
                    "shape":[1, len(max_lengths)],
                    "data": max_lengths
                }
            ]
        }
    
    def format_output(self, outputs):
        outputs = outputs.get("outputs")
        if outputs is not None and isinstance(outputs, list):
            translations = outputs[0]
            return translations.get("data")
        
    def inference(self, texts, max_lengths):
        model_inputs = self.format_inputs(texts, max_lengths)
        endpoint_url = self.deployment.get_endpoint()
        api_key = self.deployment.get_api_key()
        
        assert endpoint_url is not None
        assert api_key is not None
        
        auth_header = {
            "apiKey": api_key
        }
        
        r = requests.post(endpoint_url, headers=auth_header, json=model_inputs)
        r.raise_for_status()
        
        outputs = r.json()
        translations = self.format_output(outputs)
        
        return translations
    

class TokenClassificationModel(InferenceModel):
    def __init__(self, deployment_id):
        super().__init__(deployment_id)
        
    def format_inputs(self, texts):
        return {
            "inputs": [
                {
                    "name": "text",
                    "datatype": "BYTES",
                    "shape": [1, len(texts)],
                    "data": texts
                }
            ]
        }
    
    def format_output(self, outputs):
        outputs = outputs.get("outputs")
        if outputs is not None and isinstance(outputs, list):
            tokens, tags, scores = outputs[0], outputs[1], outputs[2]
            return tokens.get("data"), tags.get("data"), scores.get("data")
        
    def inference(self, texts):
        model_inputs = self.format_inputs(texts)
        endpoint_url = self.deployment.get_endpoint()
        api_key = self.deployment.get_api_key()
        
        assert endpoint_url is not None
        assert api_key is not None
        
        auth_header = {
            "apiKey": api_key
        }
        
        r = requests.post(endpoint_url, headers=auth_header, json=model_inputs)
        r.raise_for_status()
        
        outputs = r.json()
        tokens, tags, scores = self.format_output(outputs)
        
        return tokens, tags, scores