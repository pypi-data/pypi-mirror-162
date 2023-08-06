from ast import literal_eval
from datetime import datetime
from operator import itemgetter

from pandas import DataFrame, concat

from ingestor.common.constants import CUSTOMER_ID, VIEW_COUNT, VIEW_HISTORY, CREATED_ON, DURATION
from ingestor.common.read_write_from_s3 import ConnectS3
from ingestor.user_rating.config import MILLISECONDS_IN_ONE_MINUTE, NUMBER_OF_DUPLICATE_VIEWS_THRESHOLD, VISIONPLUS_DEV, \
    VIEWED_DATA_PATH, S3_RESOURCE
from ingestor.user_rating.constants import RECENT_DURATION, IMPLICIT_RATING_SHIFTED, \
    MAX_RATING, IMPLICIT_RATING_VALUE, RECENT_DATE, CONTENT_STATUS, ACTIVE


class RatingUtils:

    @staticmethod
    def get_queried_log_data_for_user() -> DataFrame:
        s3_cls = ConnectS3()

        viewed = s3_cls.read_compress_pickles_from_S3(bucket_name=VISIONPLUS_DEV, object_name=VIEWED_DATA_PATH,
                                                      resource=S3_RESOURCE)
        return viewed[viewed[CONTENT_STATUS] == ACTIVE]

    @staticmethod
    def get_recent_viewed_date(data) -> DataFrame:
        recent_date_list = []
        for idx, val in data.iterrows():
            recent_date_dict = {}
            history_data = val[VIEW_HISTORY]
            list_history_data = literal_eval(history_data)
            list_history_data = sorted(list_history_data, key=itemgetter(CREATED_ON), reverse=True)
            recent_date = list_history_data[0][CREATED_ON]
            recent_date = datetime.fromisoformat(str(recent_date)).date()
            recent_date_dict[RECENT_DATE] = recent_date
            recent_date_list.append(recent_date_dict)
        recent_date_df = DataFrame(recent_date_list)
        df = concat([data, recent_date_df], axis=1)
        return df

    @staticmethod
    def get_recent_duration(data) -> DataFrame:
        recent_duration_list = []
        for idx, val in data.iterrows():
            recent_duration_dict = {}
            history_data = val[VIEW_HISTORY]
            list_history_data = literal_eval(history_data)
            list_history_data = sorted(list_history_data, key=itemgetter(DURATION), reverse=True)
            recent_duration = list_history_data[0][DURATION]
            recent_duration_dict[RECENT_DURATION] = recent_duration
            recent_duration_list.append(recent_duration_dict)
        recent_duration_df = DataFrame(recent_duration_list)
        df = concat([data, recent_duration_df], axis=1)
        return df

    @staticmethod
    def get_number_of_users(data) -> int:
        number_of_users = len(set(data[CUSTOMER_ID]))
        return number_of_users

    @staticmethod
    def milliseconds_to_minutes(data) -> DataFrame:
        data[RECENT_DURATION] = data[RECENT_DURATION] / MILLISECONDS_IN_ONE_MINUTE
        return data

    @staticmethod
    def get_maximum_of_two_implicit_ratings(data) -> DataFrame:
        data[IMPLICIT_RATING_SHIFTED] = data[IMPLICIT_RATING_VALUE].shift()
        data[MAX_RATING] = data[[IMPLICIT_RATING_VALUE, IMPLICIT_RATING_SHIFTED]].max(axis=1)
        data.drop(columns=[IMPLICIT_RATING_SHIFTED], inplace=True)

        return data

    @staticmethod
    def round_partial(value, resolution):
        return round(value / resolution) * resolution

    @staticmethod
    def cap_ubd_data(data) -> DataFrame:
        data.loc[
            data[VIEW_COUNT] > NUMBER_OF_DUPLICATE_VIEWS_THRESHOLD, VIEW_COUNT] = NUMBER_OF_DUPLICATE_VIEWS_THRESHOLD
        return data
