from typing import Optional

from wj_social_net_queries.controllers.meta_controller import (
    download_recent_media_ig,
    download_recent_media_ig_by_post,
    get_hashtag_media_ig,
)
from wj_social_net_queries.utils.AWS.s3 import AwsS3
from wj_social_net_queries.utils.constants.api_graph_constants import (
    RECENT_MEDIA_OPTION,
)
from wj_social_net_queries.utils.constants.constants import TOKEN
from wj_social_net_queries.utils.ig_utils import (
    get_shortcode_from_permalink,
)
from wj_social_net_queries.utils.utils import (
    generate_file_name_with_datetime,
    save_data_on_json,
    download_image
)


class Instagram():
    """
    Description
    ----------
    Allows the use of functions related with Instagram platform
    
    """

    token=None
    def __init__(self, token: Optional[str]=None) -> None:
        if token:
            self.token = token
        else:
            self.token = TOKEN

    
    def download_recent_all_media(self, query:str, file_type:str):
        download_recent_media_ig(
            query=query, token=self.token, file_type=file_type
        )
    
    def download_recent_media_ig_by_post(self, query:str):
        download_recent_media_ig_by_post(
            query=query, token=self.token, 
        )
    
    def upload_hashtag_media_to_s3(
        self,
        query:str,
        bucket_name:str,
        aws_access_key_id:str,
        aws_secret_access_key:str
    ):
        data, addional_data = get_hashtag_media_ig(
            query=query,
            token=self.token,
            hashtag_content=RECENT_MEDIA_OPTION,
            aditional_fields=True
        )
        
        s3 = AwsS3(
            bucket=bucket_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        json_path = generate_file_name_with_datetime(
            extension="json"
        )
        save_data_on_json(
            path=json_path,
            data=addional_data
        )
        s3.upload_file(local_file=json_path, s3_filename=json_path, directory='raw')
        for post in data:
            if not post or post["media_type"] !="IMAGE":
                continue
            shortcode = get_shortcode_from_permalink(
               permalink=post["permalink"]
            )
            s3.upload_file_from_url_to_aws_s3(
                url=post["media_url"],
                directory='raw',
                file_name=shortcode
            )
        folders = s3.files_in_folder(folder='raw')
        print(folders)
