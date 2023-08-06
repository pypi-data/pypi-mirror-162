# dlt-pipedrive-source

prototype for source creation


# Parent tables 
`'deal', 'deal_participant', 'deal_flow'`


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
copy the file below and add credentials, then run it


[run_load.py](run_load.py)
```python run_load.py```

If you want only some of the tables, pass them as an argument in the tables list in the loader (see below)
```
# of all tables, get only deal_participant
tables = ['deal_participant'] 
# get all tables
tables = [] 

You can also toggle "mock data" to True in the load function, or pass None credentials, to try mock sample data.