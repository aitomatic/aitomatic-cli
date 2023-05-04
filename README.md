# WebModel Library User Manual
The WebModel library is a tool for building, tuning, and inference of models that are built with the Aitomatic system. The target users of this library are AI Engineers who use the Aitomatic system.

## Requirements
- Python 3.9 or higher
- `requests` library
- `pandas` library
- `numpy` library
- `tqdm` library

## Installation
The WebModel library can be installed using pip:

```bash
pip install aitomatic==1.2.1 -i https://test.pypi.org/simple/ 
```
## Quick Start
To get started, you can create a WebModel object by passing in the model name and API token:

```python
from aitomatic.api.web_model import WebModel

# load model
API_ACCESS_TOKEN = '<API_ACCESS_TOKEN>'
project_name="<project name>"
model_name = "<model name>"

model = WebModel(api_token=API_ACCESS_TOKEN, project_name=project_name model_name=model_name)
model.load()

# view model training statistics and info
print(model.stats)

# run model inference
data = {'X':  my_dataframe}
response = model.predict({'X': data})
print(response['predictions'])
```

## Methods
The `WebModel` class provides several methods for working with the model:

* **Constructor**
  ```python
  model_names = WebModel.get_model_names(api_token="YOUR_API_TOKEN", project_name="MyProject")
  ```

* **Load model**
  `load` set up the model ready by loading all parameter from Aitomatic model repo.
  ```python
  model.load()
  ```
  __Return__ the model with loaded params 

* **Predict**
The `predict` method takes a dictionary as input with the data you want to make predictions on. The input data should be a pandas DataFrame, Series, or numpy array with the key "X". The method returns a dictionary with the predictions, with the key "predictions".
  ```python
  response = model.predict(input_data={'X': df})
  ```
  * input_data: input data for prediction, dictionary with data under key 'X'
  __Return__
  Result of the prediction call in a dictionary where the actual result is under `prediction` key

* **Tuning**
  `tune_model` is a statis method to generate multiple versions of a given model with the set of input params
  ```python
  tune_model(
      project_name=PROJECT_NAME,
      base_model=BASE_MODEL_NAME,
      conclusion_tuning_range=conclusion_threshold_ranges,
      ml_tuning_params=ML_MODELS_PARAMS,
      output_model_df_path='tuning.parquet',
      wait_for_tuning_to_complete=True,
      prefix="[HUNG7]",
  )
  ```
    * `project_name`: A string containing the name of the Aitomatic project to use.
    * `base_model`:A string containing the name of the base model to use.
    * `conclusion_tuning_range`: A dictionary specifying the range of values to use for the final layer of the tuned model.
  * `ml_tuning_params`: A dictionary specifying the AutoML tuning parameters to use.
  * `output_model_df_path`: A string specifying the path to save the resulting DataFrame
  containing the tuned model's hyperparameters and performance.
  * `wait_for_tuning_to_complete`: A boolean specifying whether to wait for the tuning process
  to complete before returning. Default is True.
  * `prefix`: A string containing a prefix to add to the name of the new model. Default is "finetune".
  __Return__
  A Pandas DataFrame containing the hyperparameters and performance of the tuned model.


* **Log model metrics**

* **Get models in project `static`**
  ```python
  model_names = WebModel.get_model_names(api_token="YOUR_API_TOKEN", project_name="MyProject")
  ```
  * The `api_token` A string containing the access token for the Aitomatic API. If not provided, the AITOMATIC_API_TOKEN environment variable will be used.
  * The `project_name` A string containing the name of the Aitomatic project to use. If not provided, the AITOMATIC_PROJECT_ID environment variable will be used.
  __Return__ a list of the names of all models in the specified project.
  



# Load sample dataset
data = pd.read_csv("sample_data.csv")

# Initialize WebModel object
model = WebModel("MyModelName", api_token="YOUR_API_TOKEN")

# Load model parameters
model.load()

# Make predictions on sample data
predictions = model.predict({"X": data})
Here's an example of using the log_metrics method to log custom metrics:

python
Copy code
# Log custom metric for model accuracy
model.log_metrics("accuracy", 0.95)
Here's an example of using the get_model_names method to retrieve a list of model names for a given project:

python
Copy code
# Retrieve list of model names for a given project
model_names = WebModel.get_model_names(api_token="YOUR_API_TOKEN", project_name="MyProject")