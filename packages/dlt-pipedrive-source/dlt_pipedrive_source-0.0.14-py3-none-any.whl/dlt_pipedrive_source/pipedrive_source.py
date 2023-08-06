from pipedrive import Pipedrive

class PipedriveSource:

    def __init__(self, username_or_api_key, password=None):
        if password:
            username = username_or_api_key
            self.client = Pipedrive(username, password)
        else:
            api_key = username_or_api_key
            self.client = Pipedrive(api_key)

    def paginated_request(self, endpoint, method='GET'):
        next_page = True
        next_start_row = 0
        while next_page == True:
            resp = self.client._request(endpoint, {'start': next_start_row, 'limit': 500}, method=method)
            for row in resp['data']:
                    yield row

            next_page = resp.get('additional_data', {}).get('pagination', {}).get('more_items_in_collection')
            next_start_row = resp.get('additional_data', {}).get('pagination', {}).get('next_start')


    def get_deals(self):
        for row in self.paginated_request('deals'):
            yield row

    def get_deals_participants(self):
        for row in self.paginated_request('deals'):
            endpoint = f"deals/{row['id']}/participants"
            for subrow in self.paginated_request(endpoint):
                yield subrow

    def get_deals_flow(self):
        for row in self.paginated_request('deals'):
            endpoint = f"deals/{row['id']}/flow"
            for subrow in self.paginated_request(endpoint):
                yield subrow

    def tables(self):
        return [{'table_name': 'deal', 'data': self.get_deals()},
                {'table_name': 'deal_participant', 'data': self.get_deals_participants()},
                {'table_name': 'deal_flow', 'data': self.get_deals_flow()},
        ]

