from stochasticx.constants.urls import MODELS_URL, OPTIMIZED_MODELS_URL
from stochasticx.utils.auth_utils import AuthUtils
from stochasticx.utils.file_utils import ModelUtils
import requests


class ModelType:
    """Model type
    """
    
    HUGGINGFACE = "hf"
    PYTORCH = "pt"
    ONNX = "onnx"
    CUSTOM = "custom"


class Model:
    """Model class
    """
    
    def __init__(
        self,
        name: str,
        directory_path: str,
        model_type: str = ModelType.HUGGINGFACE
    ):
        """Initializer

        Args:
            name (str): model name
            directory_path (str): directory path where the model is located
            model_type (str, optional): model type. Defaults to ModelType.HUGGINGFACE.
        """
        assert isinstance(name, str), "The provided name {} is not valid".format(name)
        
        self.name = name
        self.directory_path = directory_path
        self.model_type = model_type
        self.model_id = None
        self.model_info = None
        self.is_uploaded = False
        
    def upload(self):
        """Upload the model to the stochastic platform
        """
        
        model_id = ModelUtils.upload_model(
            self.directory_path, 
            self.name, 
            self.model_type
        )
        
        self.set_id(model_id)
        self.is_uploaded = True
        
    def set_id(self, model_id: str):
        """Sets the model ID

        Args:
            model_id (str): new ID
        """
        self.model_id = model_id
        
    def sync(self):
        """Syncs the model information with the stochastic platform
        """
        
        if self.model_id is not None:
            temp_model = Models.get_model(self.model_id)
            self.name = temp_model.name
            self.model_info = temp_model.model_info
            self.is_uploaded = True
    
    def get_id(self):
        """Gets the model ID

        Returns:
            str: the model ID
        """
        return self.model_id
    
    def get_model_info(self):
        """Gets the model information

        Returns:
            dict: model information
        """
        
        self.sync()
        
        return self.model_info
                
    def set_model_info(self, model_info):
        """Sets the model information

        Args:
            model_info (dict): model info
        """
        self.model_info = model_info
    
    def download(self, local_path: str):
        """Download the model for the Stochastic platform

        Args:
            local_path (str): path where the model will be saved
        """
        assert self.model_id is not None
        ModelUtils.download_model(self.model_id, local_path)
                    
    def __str__(self):
        """Convert the object to string

        Returns:
            str
        """
        return "Model ID: {} ; Name: {} ; Directory path: {} ; Model type: {} ; Uploaded: {}".format(
            self.model_id,
            self.name,
            self.directory_path,
            self.model_type,
            self.is_uploaded
        )
    

class OptimizedModel:
    """Optimized model class
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        size: str,
        benchmark_results: dict
    ):
        """Initializer

        Args:
            id (str): model ID
            name (str): model name
            type (str): model type
            size (str): model size in bytes
            benchmark_results (dict): benchmark results
        """
        
        self.id = id
        self.name = name
        self.type = type
        self.size = size
        self.benchmark_results = benchmark_results
        
    def download(self, local_path: str):
        """Downloads the model from the Stochastic platform

        Args:
            local_path (str): path where the model will be saved
        """
        
        ModelUtils.download_optimized_model(self.id, local_path)
    
    def get_benchmark_results(self):
        """Get benchmark results

        Returns:
            dict: benchmark results
        """
        return self.benchmark_results
    
    def __str__(self):
        """Converts the object to a string

        Returns:
            str
        """
        
        return "Optimized model ID: {} ; Name: {} ; Type: {} ; Size: {} ".format(
            self.id,
            self.name,
            self.type,
            self.size
        )
        

class Models:
    """Class to get the models uploaded in the Stochastic platform
    """
    
    @staticmethod
    def get_model(model_id: str):
        """Gets the model from the Stochastic platform

        Args:
            model_id (str): model ID

        Returns:
            Model: model
        """
        
        url = MODELS_URL + "/{}".format(model_id)

        auth_header = AuthUtils.get_auth_headers()
        response = requests.get(url, headers=auth_header)
        model_data = response.json().get("data")
        
        if model_data is not None:
            model = Model(
                name=model_data.get("name"),
                directory_path=None,
                model_type=model_data.get("type")
            )
            
            model.set_id(model_data.get("id"))
            model.set_model_info(model_data.get("modelInfo"))
            model.is_uploaded = True
            
            return model
        
        return None
    
    @staticmethod
    def get_models():
        """Gets all the models from the stochastic platform

        Returns:
            List[Model]: list of models
        """
        models = []

        auth_header = AuthUtils.get_auth_headers()
        response = requests.get(MODELS_URL, headers=auth_header)
        models_data = response.json().get("data")

        if models_data is not None:
            for model_data in models_data:
                model = Model(
                    name=model_data.get("name"),
                    directory_path=None,
                    model_type=model_data.get("type")
                )
                
                model.set_id(model_data.get("id"))
                model.set_model_info(model_data.get("modelInfo"))
                model.is_uploaded = True
                models.append(model)

        return models
    
    @staticmethod
    def get_optimized_models():
        """Gets all the optimized models from the Stochastic platform

        Returns:
            List[OptimizedModel]: list of optimized models
        """
        
        models = []

        auth_header = AuthUtils.get_auth_headers()
        response = requests.get(OPTIMIZED_MODELS_URL, headers=auth_header)
        models_data = response.json().get("optimizedModels")

        if models_data is not None:
            for model_data in models_data:
                model = OptimizedModel(
                    id=model_data.get("id"),
                    name=model_data.get("userGivenName"),
                    type=model_data.get("type"),
                    size=model_data.get("size"),
                    benchmark_results=model_data.get("result").get("results")
                )

                models.append(model)

        return models
    
    @staticmethod
    def get_optimized_model(model_id: str):
        """Gets an optimized model from the Stochastic plarform

        Args:
            model_id (str): model ID

        Returns:
            OptimizedModel: optimized model
        """
        
        url = OPTIMIZED_MODELS_URL + "/{}".format(model_id)

        auth_header = AuthUtils.get_auth_headers()
        response = requests.get(url, headers=auth_header)
        model_data = response.json().get("data")
                
        if model_data is not None and len(model_data) > 0:
            model = OptimizedModel(
                id=model_data.get("id"),
                name=model_data.get("userGivenName"),
                type=model_data.get("type"),
                size=model_data.get("size"),
                benchmark_results=model_data.get("result").get("results")
            )
            
            return model
        
        return None