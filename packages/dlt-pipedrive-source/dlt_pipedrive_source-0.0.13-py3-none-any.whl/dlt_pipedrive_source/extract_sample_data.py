from dlt_pipedrive_source.pipedrive_source import PipedriveSource as DataSource
import jsonlines

"""
This utility runs the data source extractor and writes the data to files in the sample_data folder
From here the data is automatically used to populate the mock source tables().
If you publish the source, take care that the data does not contain "Personally Identifiable Information"
"""

api_key = '98af5bbaee437dc46daaa4535bd1bd61e1907899'
s = DataSource(api_key)

tables = s.tables()

for table in tables:
    with jsonlines.open(f"sample_data/{table['table_name']}.jsonl", mode='w') as writer:
        writer.write_all(table['data'])


