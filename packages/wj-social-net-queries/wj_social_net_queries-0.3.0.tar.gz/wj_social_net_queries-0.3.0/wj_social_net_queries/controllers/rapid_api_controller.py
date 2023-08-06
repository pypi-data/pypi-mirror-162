from typing import Optional
from wj_social_net_queries.connectors.rapid_api_connector import RapidAPIConnector

def get_ig_post_info(permalink:str):
    """
    Description
    ----------
    Given a Facbook account token, this function searches if there is a
    business account id related with this account.

    Arguments
    ---------
    token: str
        Facebook token

    Return
    -------
    is_business: bool, str | bool, error_message

    """
    rapid_api =  RapidAPIConnector()
    post_success, data = rapid_api.instagram_data_post_metadata(permalink=permalink)
    if not post_success:
        return
    
    return data