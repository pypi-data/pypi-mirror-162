from datetime import timedelta, date
from math import log, floor

from pandas import DataFrame, concat, cut, get_dummies

from ingestor.common.constants import VIEW_COUNT, CUSTOMER_ID, CONTENT_ID
from ingestor.user_rating.config import DAYS, weight_duration, weight_top_rating, weight_very_positive, weight_positive, \
    weight_not_sure, SCALING_FACTOR, NUMBER_OF_BINS, RESOLUTION
from ingestor.user_rating.constants import BINS, NOT_SURE, POSITIVE, VERY_POSITIVE, TOP_RATING, AGE_OF_EVENT, \
    TIME_DECAY_FACTOR, IMPLICIT_RATING, RECENT_DATE, RECENT_DURATION, COUNT, RATING_DATA_FILE, DURATION_VALUE, \
    TOP_RATING_VALUE, VERY_POSITIVE_VALUE, POSITIVE_VALUE, NOT_SURE_VALUE, IMPLICIT_RATING_VALUE, \
    NORMALISED_IMPLICIT_RATING, MAX_RATING
from ingestor.user_rating.rating_utils import RatingUtils
from ingestor.repository.graph_db_connection import ANGraphDb

connection_uri_writer = "ws://dev-neptune-write-292706514.ap-southeast-1.elb.amazonaws.com:8183/gremlin"
connection_uri_reader = "ws://dev-neptune-376859199.ap-southeast-1.elb.amazonaws.com:8182/gremlin"

graph = ANGraphDb.new_connection_config().graph


class RatingGenerator:

    def define_rating_events(self) -> DataFrame:
        """
        Define rating events based on view counts:
        TOP RATING : Occurs in top first bin (maximum view counts)
        VERY POSITIVE : Occurs in second top bin
        POSITIVE : third bin
        NOT SURE : last bin (least view counts)
        """
        data = RatingUtils.get_queried_log_data_for_user()
        data = RatingUtils.cap_ubd_data(data)
        bins = data[VIEW_COUNT].value_counts(bins=NUMBER_OF_BINS, sort=False).rename_axis(BINS).reset_index(name=COUNT)
        bins_list = bins[BINS].to_list()
        data[BINS] = cut(data[VIEW_COUNT],
                         bins=[floor(bins_list[0].left), floor(bins_list[0].right), floor(bins_list[1].right),
                               floor(bins_list[2].right),
                               floor(bins_list[3].right)], labels=[NOT_SURE, POSITIVE, VERY_POSITIVE, TOP_RATING])
        rating_data = get_dummies(data[BINS])
        data = concat([data, rating_data], axis=1)
        return data.reset_index()

    def calculate_time_decay(self
                             ) -> DataFrame:
        """
        Find two rating parameters:
        1. Age of most recent view events (in days) = "created_on" (date) to days conversion
        2. time decay factor = 1/age of view events
        Add all 2 above computed parameters as additional attributes in final dataframe
        """
        data = self.define_rating_events()

        data = RatingUtils.get_recent_viewed_date(data)
        data = RatingUtils.get_recent_duration(data)

        data[AGE_OF_EVENT] = (date.today() - data[RECENT_DATE]) // timedelta(days=DAYS)
        data[TIME_DECAY_FACTOR] = 1 / data[AGE_OF_EVENT]

        return data

    def calculate_implicit_rating_with_inverse_user_frequency(self) -> DataFrame:
        """
        Inverse user frequency = log(N/(1 + n)), where:
                                 N = Total number of users in the catalog
                                 n = total number of top rating events
        """
        data = self.calculate_time_decay()

        INVERSE_USER_FREQUENCY = log(RatingUtils.get_number_of_users(data) / (1 + data[TOP_RATING].sum()))
        data = RatingUtils.milliseconds_to_minutes(data)
        data[DURATION_VALUE] = weight_duration * data[RECENT_DURATION] * data[
            TIME_DECAY_FACTOR] * INVERSE_USER_FREQUENCY
        data[TOP_RATING_VALUE] = weight_top_rating * data[TOP_RATING] * data[VIEW_COUNT] * data[
            TIME_DECAY_FACTOR] * INVERSE_USER_FREQUENCY
        data[VERY_POSITIVE_VALUE] = weight_very_positive * data[VERY_POSITIVE] * data[VIEW_COUNT] * data[
            TIME_DECAY_FACTOR] * INVERSE_USER_FREQUENCY
        data[POSITIVE_VALUE] = weight_positive * data[POSITIVE] * data[VIEW_COUNT] * data[
            TIME_DECAY_FACTOR] * INVERSE_USER_FREQUENCY
        data[NOT_SURE_VALUE] = weight_not_sure * data[NOT_SURE] * data[VIEW_COUNT] * data[
            TIME_DECAY_FACTOR] * INVERSE_USER_FREQUENCY

        data[IMPLICIT_RATING_VALUE] = data[DURATION_VALUE] + data[TOP_RATING_VALUE] + data[VERY_POSITIVE_VALUE] + data[
            POSITIVE_VALUE] + data[NOT_SURE_VALUE]

        data = RatingUtils.get_maximum_of_two_implicit_ratings(data)

        data[NORMALISED_IMPLICIT_RATING] = data[IMPLICIT_RATING_VALUE] / data[MAX_RATING]

        data[IMPLICIT_RATING] = RatingUtils.round_partial((SCALING_FACTOR * data[NORMALISED_IMPLICIT_RATING]),
                                                          RESOLUTION)

        data = data[[CUSTOMER_ID, CONTENT_ID, IMPLICIT_RATING]]

        data.to_pickle(RATING_DATA_FILE)

        return data
