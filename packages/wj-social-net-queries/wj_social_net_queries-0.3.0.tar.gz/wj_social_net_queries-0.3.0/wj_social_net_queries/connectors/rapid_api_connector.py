import json
from wj_social_net_queries.connectors.api_connector import (
    ApiConnector,
)
from wj_social_net_queries.utils.constants.rapid_api_constans import (
    RAPID_API_URL,
    POST_METADATA,
    X_RAPIDAPI_HOST,
    X_RAPIDAPI_KEY

)
from wj_social_net_queries.utils.constants.constants import (
    GET
)


class RapidAPIConnector(ApiConnector):

    def __init__(self) -> None:
        self.api_url = RAPID_API_URL

    
    def instagram_data_post_metadata(self, permalink:str):
        """
        Description
        ----------
        Given a post permalink, gets all info from its user

        Arguments
        ---------
        permalink: str
            Post url

        Return
        -------
        is_business: bool, dict | bool, error_message
        
        """
        request_url = self.api_url + POST_METADATA
        params = dict(
            post=permalink
        )
        headers = {
            "X-RapidAPI-Key" : X_RAPIDAPI_KEY,
            "X-RapidAPI-Host" : X_RAPIDAPI_HOST
        }

        response = self.api_request(
            request_url=request_url,
            operation=GET,
            params=params,
            headers=headers
        )

        #TODO: use a http status code codification
        content = json.loads(response.content)
        if response.status_code == 200:
            return True, content
        else:
            function_name=self.instagram_data_post_metadata.__name__,
            message = function_name[0] + " :: error " + str(response.status_code)
            print(message)
            print(content)
            return False, None
