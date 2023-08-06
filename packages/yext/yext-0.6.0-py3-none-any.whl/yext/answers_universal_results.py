import json
from requests import Response

class AnswersUniversalResults:

    '''
    Utility class for handling results from Answers Universal
    '''

    def __init__(self, response: Response):
        self.response = response
        self.response.raise_for_status()
        self.raw_response = response.json()
        self.response = self.raw_response['response']
        self.query_id = self.response['queryId']

    def __repr__(self):
        pretty = json.dumps(self.raw_response, indent=2)
        msg = f'AnswersUniversalResults object. \n {pretty}'
        return msg

    @property
    def verticals_returned(self) -> list:
        '''Returns a list of all verticalKeys returned.'''
        verticals = [module['verticalConfigId']
                     for module in self.response['modules']]
        return verticals

    @property
    def km_verticals_returned(self) -> list:
        '''Returns a list of all Knowledge Graph verticals.'''
        verticals = [module['verticalConfigId'] for
                     module in self.response['modules']
                     if module['source'] == 'KNOWLEDGE_MANAGER']
        return verticals

    @property
    def non_km_verticals_returned(self) -> list:
        '''Returns a list of all third-party-backend verticals.'''
        verticals = [module['verticalConfigId'] for
                     module in self.response['modules']
                     if module['source'] != 'KNOWLEDGE_MANAGER']
        return verticals

    @property
    def gcse_verticals_returned(self) -> list:
        '''Returns a list of all Google Custom Search Engine (links) verticals.'''
        verticals = [module['verticalConfigId'] for
                     module in self.response['modules']
                     if module['source'] == 'GOOGLE_CSE']
        return verticals

    @property
    def no_results(self) -> bool:
        '''Returns bool for whether or not the query had no results.'''
        return not self.response['modules']

    @property
    def result_counts(self) -> dict:
        '''Returns a dictionary of result counts for each vertical'''
        result_counts = {module['verticalConfigId']: module['resultsCount']
                         for module in self.response['modules']}
        return result_counts

    def get_vertical_results(self, vertical_key: str):
        '''Returns the results from a particular vertical.'''
        if vertical_key not in self.verticals_returned:
            raise ValueError(
                f'{vertical_key} was not returned in the response.')
        else:
            for module in self.response['modules']:
                if module['verticalConfigId'] == vertical_key:
                    return module['results']
