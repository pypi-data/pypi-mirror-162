from orkg.utils import NamespacedClient, simcomp_available
from orkg.out import OrkgResponse
from typing import List, Tuple
import pandas as pd
from ast import literal_eval


class ContributionsClient(NamespacedClient):

    @simcomp_available
    def similar(self, cont_id: str) -> OrkgResponse:
        self.client.simcomp._append_slash = True
        response = self.client.simcomp.similar(cont_id).GET()
        return self.client.wrap_response(response=response)

    @simcomp_available
    def compare(self, contributions: List[str], response_hash: str = None) -> OrkgResponse:
        self.client.simcomp._append_slash = False
        params = f'?contributions={",".join(contributions)}'
        if response_hash is not None:
            params = f'{params}&response_hash={response_hash}'
        response = self.client.simcomp.compare.GET(params)
        return self.client.wrap_response(response=response)

    def __get_contributions_from_comparison(self, comparison_id: str) -> Tuple[List[str], str]:
        resource = self.client.resources.by_id(comparison_id).content
        if 'Comparison' not in resource['classes']:
            raise ValueError("This id is not for a comparison")
        response = self.client.json.get_json(resource_id=comparison_id).content
        url = response['data']['url']
        response_hash = None
        if 'response_hash=' in url:
            response_hash = url[url.index('response_hash=')+14:]
        return url[15:url.index('&')].split(','), response_hash

    @simcomp_available
    def compare_dataframe(self, contributions: List[str] = None, comparison_id: str = None) -> pd.DataFrame:
        if contributions is None and comparison_id is None:
            raise ValueError("either provide the contributions, or the comparison ID")
        response_hash = None
        if comparison_id is not None:
            contributions, response_hash = self.__get_contributions_from_comparison(comparison_id)
        response = self.compare(contributions=contributions, response_hash=response_hash)
        if not response.succeeded:
            return pd.DataFrame()
        content = response.content
        contributions_list = content['contributions']
        columns = [f"{contribution['title']}/{contribution['contributionLabel']}" for contribution in
                   contributions_list]
        properties_list = content['properties']
        property_lookup = {prop['id']: prop['label'] for prop in properties_list}
        # create table view of the data
        data = content['data']
        indices = []
        rows = []
        for prop_id, values in data.items():
            indices.append(property_lookup[prop_id])
            row = []
            for index, value in enumerate(values):
                if not value[0]:
                    row.append('')
                else:
                    if len(value) == 1:
                        try:
                            # Try parse the single value into datatype
                            row.append(literal_eval(value[0]['label']))
                        except (SyntaxError, ValueError):
                            # If it fails, that means it is a string
                            row.append(value[0]['label'])
                    else:
                        cell = []
                        # Rather than parsing it in a list comprehension that might fail
                        # Then the whole list will be typed as strings, we parse it one item at a time
                        for v in value:
                            try:
                                # Try parse each value by itself
                                cell.append(literal_eval(v['label']))
                            except (SyntaxError, ValueError):
                                # If it fails, that means it is a string
                                cell.append(v['label'])
                        row.append(cell)
            rows.append(row)
        # create data frame from pieces
        df = pd.DataFrame(rows, columns=columns, index=indices)
        return df
