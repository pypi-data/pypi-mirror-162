from stochasticx.utils.auth_utils import AuthUtils
from stochasticx.constants.urls import JOBS_URL
from stochasticx.models.models import Model, Models
from stochasticx.datasets.datasets import Dataset

from typing import List, Dict

import requests


class OptimizationCriteria:
    LATENCY = "latency"
    LOSSLESS = "lossless"

 
class TaskType:
    def __init__(self):
        pass
    
    def get_dataset_columns(self):
        raise NotImplementedError("This method should be implemented by the child class")
    
    def get_task_arguments(self):
        raise NotImplementedError("This method should be implemented by the child class")
    
    def get_task_type(self):
        raise NotImplementedError("This method should be implemented by the child class")

 
class SequenceClassificationTask(TaskType):
    def __init__(
        self,
        sentence1_column,
        sentence2_column,
        labels_column,
        max_seq_length=128
    ):
        self.sentence1_column = sentence1_column
        self.sentence2_column = sentence2_column
        self.labels_column = labels_column
        self.max_seq_length = max_seq_length
        
    def get_dataset_columns(self):
        return {
            "sentence1_column": self.sentence1_column,
            "sentence2_column": self.sentence2_column,
            "labels_column": self.labels_column
        }
    
    def get_task_arguments(self):
        return {
            "max_seq_length": self.max_seq_length
        }
        
    def get_task_type(self):
        return "sequence_classification"

 
class QuestionAnsweringTask(TaskType):
    def __init__(
        self,
        question_column,
        answer_column,
        context_column,
        max_seq_length=128,
        stride=30
    ):
        self.question_column = question_column
        self.answer_column = answer_column
        self.context_column = context_column
        self.max_seq_length = max_seq_length
        self.stride = stride
        
    def get_dataset_columns(self):
        return {
            "question_column": self.question_column,
            "answer_column": self.answer_column,
            "context_column": self.context_column
        }
    
    def get_task_arguments(self):
        return {
            "max_seq_length": self.max_seq_length,
            "stride": self.stride
        }
        
    def get_task_type(self):
        return "question_answering"

 
class SummarizationTask(TaskType):
    def __init__(
        self,
        text_column,
        summary_column,
        max_source_length=256,
        max_target_length=64,
	    lang="en",
        pad_to_max_length=False,
        num_beams=4,
        ignore_pad_token_for_loss=True,
        source_prefix="",
        forced_bos_token=None
    ):
        self.text_column = text_column
        self.summary_column = summary_column
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length
        self.lang = lang
        self.pad_to_max_length = pad_to_max_length
        self.num_beams = num_beams
        self.ignore_pad_token_for_loss = ignore_pad_token_for_loss
        self.source_prefix = source_prefix
        self.forced_bos_token = forced_bos_token
        
    def get_dataset_columns(self):
        return {
            "text_column": self.text_column,
            "summary_column": self.summary_column
        }
    
    def get_task_arguments(self):
        return {
            "max_source_length": self.max_source_length,
            "max_target_length": self.max_target_length,
            "lang": self.lang,
            "pad_to_max_length": self.pad_to_max_length,
            "num_beams": self.num_beams,
            "ignore_pad_token_for_loss": self.ignore_pad_token_for_loss,
            "source_prefix": self.source_prefix,
            "forced_bos_token": self.forced_bos_token
        }
        
    def get_task_type(self):
        return "summarization"

  
class TranslationTask(TaskType):
    def __init__(
        self,
        translation_column,
        src_lang="en",
        tgt_lang="es",
        max_source_length=256,
        max_target_length= 256,
        pad_to_max_length=False,
        num_beams=4,
        ignore_pad_token_for_loss=True,
        source_prefix="",
        forced_bos_token=None
    ):
        self.translation_column = translation_column
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length
        self.pad_to_max_length = pad_to_max_length
        self.num_beams = num_beams
        self.ignore_pad_token_for_loss = ignore_pad_token_for_loss
        self.source_prefix = source_prefix
        self.forced_bos_token = forced_bos_token
        
    def get_dataset_columns(self):
        return {
            "translation_column": self.translation_column
        }
    
    def get_task_arguments(self):
        return {
            "src_lang": self.src_lang,
            "tgt_lang": self.tgt_lang,
            "max_source_length": self.max_source_length,
            "max_target_length": self.max_target_length,
            "pad_to_max_length": self.pad_to_max_length,
            "num_beams": self.num_beams,
            "ignore_pad_token_for_loss": self.ignore_pad_token_for_loss,
            "source_prefix": self.source_prefix,
            "forced_bos_token": self.forced_bos_token
        }

    def get_task_type(self):
        return "translation"


class TokenClassificationTask(TaskType):
    def __init__(
        self,
        tokens_column,
        domains_column,
        ner_tags_column,
        max_seq_length=128,
        label_all_tokens=False
    ):
        self.tokens_column = tokens_column
        self.domains_column = domains_column
        self.ner_tags_column = ner_tags_column
        self.max_seq_length = max_seq_length
        self.label_all_tokens = label_all_tokens
        
    def get_dataset_columns(self):
        return {
            "tokens_column": self.tokens_column,
            "domains_column": self.domains_column,
            "ner_tags_column": self.ner_tags_column
        }
    
    def get_task_arguments(self):
        return {
            "max_seq_length": self.max_seq_length,
            "label_all_tokens": self.label_all_tokens
        }
        
    def get_task_type(self):
        return "token_classification"


class Job:
    def __init__(
        self,
        name
    ):
        self.id = None
        self.name = name
        self.original_model = None
        self.optimization_type = None
        self.optimization_criteria = None
        self.optimized_models = []
        self.job_status = None
        self.created_at = None
    
    def _populate_job(self, info_from_api):
        self.id = info_from_api.get("id")
        self.name = info_from_api.get("name")
        
        original_model_id = None 
        original_model_data = info_from_api.get("model")
        if original_model_data is not None and isinstance(original_model_data, dict):
            original_model_id = original_model_data.get("id")
        self.original_model = Models.get_model(original_model_id)
        
        self.optimization_type = info_from_api.get("optimizationType")
        self.optimization_criteria = info_from_api.get("optimizationCriteria")
        self.job_status = info_from_api.get("jobStatus")
        self.created_at = info_from_api.get("createdAt")
        
        if info_from_api.get("models") is not None and isinstance(info_from_api.get("models"), list):
            for optimized_model_id in info_from_api.get("models"):
                optimized_model = Models.get_optimized_model(optimized_model_id)
                self.optimized_models.append(optimized_model)
                
    def sync(self):
        if self.id is not None:
            temp_job = Jobs.get_job(self.id)
            self.name = temp_job.name
            self.original_model = temp_job.original_model
            self.optimization_type = temp_job.optimization_type
            self.optimization_criteria = temp_job.optimization_criteria
            self.optimized_models = temp_job.optimized_models
            self.job_status = temp_job.job_status
            self.created_at = temp_job.created_at
    
    def launch_auto(
        self,
        model: Model,
        dataset: Dataset,
        task_type: TaskType,
        optimization_criteria: str = OptimizationCriteria.LATENCY,
    ):
        assert model.is_uploaded, "This model has not been uploaded. Upload it first"
        assert dataset.is_uploaded, "This dataset has not been uploaded. Upload it first"
        assert isinstance(task_type, TaskType), "The task type is not valid"
        
        job_parameters = {
            "dataset": dataset.get_id(),
            "model": model.get_id(),
            "modelCloud": "s3",
            "jobName": self.name,
            "optimizationCriteria": optimization_criteria,
            "selectedColumns": task_type.get_dataset_columns(),
            "taskArguments": task_type.get_task_arguments(),
            "taskType": task_type.get_task_type(),
            "optimizationType": "auto",
            "finetuningArguments": {},
            "knowledgeDistillationArguments": {},
            "instanceType": "g4dn.xlarge",
            "isCPU": False,
            "isGPU": True
        }
        
        auth_header = AuthUtils.get_auth_headers()
        r = requests.post(
            JOBS_URL, 
            headers=auth_header, 
            json=job_parameters
        )
        r.raise_for_status()
        
        data = r.json().get("data")
        if data is not None:
            self.id = data.get("id")
        
    def get_status(self):
        self.sync()
        
        return self.job_status
        
    def __str__(self):
        return "Job ID: {} ; Name: {} ; Status: {} ; Created at: {} ; Optimization type: {} ; Optimization criteria: {}".format(
            self.id,
            self.name,
            self.job_status,
            self.created_at,
            self.optimization_type,
            self.optimization_criteria
        )
        

class Jobs:
    
    @staticmethod
    def get_jobs():
        jobs = []

        auth_header = AuthUtils.get_auth_headers()
        response = requests.get(JOBS_URL, headers=auth_header)
        jobs_data = response.json().get("data")
        
        if jobs_data is not None:
            for job_data in jobs_data:
                job = Job(
                    name=None
                )
                
                job._populate_job(job_data)
                jobs.append(job)
                
        return jobs
    
    @staticmethod
    def get_job(job_id):
        url = JOBS_URL + "/{}".format(job_id)

        auth_header = AuthUtils.get_auth_headers()
        response = requests.get(url, headers=auth_header)
        job_data = response.json().get("data")
        
        if job_data is not None:
            job_data = job_data.get("job")

        if job_data is not None:
            job = Job(
                name=job_data.get("name")
            )
            
            job._populate_job(job_data)
            
            return job
        
        return None