# dlt-pipedrive-source

prototype for source creation


# Parent tables 



# Usage

optionally Create a virtual environment
```
python3 -m venv ./dlt_pipedrive_env
source ./dlt_pipedrive_env/bin/activate
```

install library

```pip install dlt-pipedrive-source```

If the library cannot be found, ensure you have the required python version as per the `pyproject.toml`file.
(3.8+)

You can run the snippet file below to load a sample data set. 
You would need to add your target credentials first.

```python run_load.py```

You can also toggle "mock data" to True in the load function, or pass None credentials, to try mock sample data.