"""
This is a simple pipeline that you can use without further configuration.
If you want to parallelise the load or do a different workflow, create your own pipeline.
"""

from dlt_pipedrive_source._helpers import extract_data_and_prepare_schema, load_data
from dlt_pipedrive_source.pipedrive_source import PipedriveSource as DataSource
from dlt_pipedrive_source.mock_source import MockDataSource


def load(api_key=None,
         user=None,
         password=None,
         # for target credentials, pass a client_secrets.json or a credential json suitable for your db type.
         target_credentials={},
         #default tables, remove some if you do not want all of them
         tables=[],
         schema_name = 'pipedrive',
         mock_data = False):

    if mock_data:
        source = MockDataSource(url='', user='', password='')
    else:
        if api_key:
            source = DataSource(api_key)
        elif user and password:
            source = DataSource(user, password)
        else:
            #if incorrect credentials, auth will fail, if no credentials then do mock data
            source = MockDataSource()


    if tables == []:
        tables = [t['table_name']  for t in source.tables()]
    tables_to_load = [t for t in source.tables() if t['table_name'] in tables]


    pipeline = None
    for table in tables_to_load:
        #add data to pipeline
        pipeline = extract_data_and_prepare_schema(pipeline,
                                        table['data'],
                                        #target creds will be moved to load
                                        credentials=target_credentials,
                                        table_name=table['table_name'],
                                        schema_file='schema',
                                        update_schema=False)
    #now load the data
    load_data(pipeline, credentials = target_credentials,
                  dataset_prefix='dlt',
                  dataset_name=schema_name)

    print(f"loaded {','.join(tables)}")


if __name__ == "__main__":

    load(api_key='98af5bbaee437dc46daaa4535bd1bd61e1907899',
         user=None,
         password=None,
         # for target credentials, pass a client_secrets.json or a credential json suitable for your db type.
         target_credentials={
  "type": "service_account",
  "project_id": "zinc-mantra-353207",
  "private_key_id": "7dd0871cfc3031c58f503d2876735d607df049c4",
  "private_key": "",
  "client_email": "data-load-tool-public-demo@zinc-mantra-353207.iam.gserviceaccount.com",
  "client_id": "100909481823688180493",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/data-load-tool-public-demo%40zinc-mantra-353207.iam.gserviceaccount.com"
}

            ,
         # default tables, remove some if you do not want all of them
         tables=[],
         schema_name='pipedrive',
         mock_data=True)



