import os

import stochasticx

LOGIN_URL = stochasticx.BASE_URI + "/v1/auth/login"
MODELS_URL = stochasticx.BASE_URI + "/v1/models"
OPTIMIZED_MODELS_URL = stochasticx.BASE_URI + "/v1/processedModels"
REQUEST_UPLOAD_URL = stochasticx.BASE_URI + "/v1/upload/requestUpload"
MODEL_UPLOAD_URL = stochasticx.BASE_URI + "/v1/upload/model"
DATASET_UPLOAD_URL = stochasticx.BASE_URI + "/v1/upload/dataset"
DATASETS_URL = stochasticx.BASE_URI + "/v1/datasets"
ME_URL = stochasticx.BASE_URI + "/v1/auth/me"
JOBS_URL = stochasticx.BASE_URI + "/v1/jobs"
INSTANCES_URL = stochasticx.BASE_URI + "/v1/instances"
DEPLOYMENT_URL = stochasticx.BASE_URI + "/v1/deploy"

TOKEN_AUTH_PATH = os.path.expandvars("$HOME/.stochastic/token.json")

INFERENCE_URL = stochasticx.BASE_URI + "http://infer.stochastic.ai:8000/"
