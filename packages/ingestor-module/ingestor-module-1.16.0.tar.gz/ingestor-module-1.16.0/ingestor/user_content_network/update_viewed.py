import logging

import pandas as pd
from pandas import DataFrame

from ingestor.common.constants import CONTENT_ID, CUSTOMER_ID, STATUS, \
    VIEW_COUNT, VIEW_HISTORY, CREATE, UPDATE, CREATED_ON, DURATION, VIDEO_ID1, CONTENT_LABEL, CONTENT_STATUS
from ingestor.common.convert_time_zone import ConvertTimeZone
from ingestor.common.read_write_from_s3 import ConnectS3
from ingestor.repository.graph_db_connection import ANGraphDb
from ingestor.user_content_network.utils import ViewedUtils
from ingestor.user_rating.config import S3_RESOURCE, VISIONPLUS_DEV, KMEANS_DATA_PATH


class UCNetworkGenerator:

    @staticmethod
    def filter_users(
            data: DataFrame
    ):
        """
        Filter streaming ubd users based
        on user present in graphdb
        :param data: Streaming ubd dataframe
        :return: dataframe object pandas
        """
        cluster_data = DataFrame()
        try:
            cluster_data = ConnectS3().read_compress_pickles_from_S3(bucket_name=VISIONPLUS_DEV,
                                                                     object_name=KMEANS_DATA_PATH,
                                                                     resource=S3_RESOURCE)
            cluster_data[CUSTOMER_ID] = cluster_data[CUSTOMER_ID].astype(str)
        except Exception as e:
            logging.error(f"Unable to read join_kmeans.pkl from S3, Error: {e}")
        data = data[data[CUSTOMER_ID].isin(cluster_data[CUSTOMER_ID])]
        return data

    @staticmethod
    def filter_features(
            data: DataFrame
    ):
        """
        Filters to keep only the required fields
        :param data: dataframe object pandas
        :return: dataframe object pandas
        """

        data = data[[CUSTOMER_ID, CREATED_ON, VIDEO_ID1, DURATION]]
        data[CUSTOMER_ID] = data[CUSTOMER_ID].astype(str)
        data = data[data[CUSTOMER_ID] != '0']
        data[CREATED_ON] = pd.to_datetime(data[CREATED_ON], unit='s')
        data[VIDEO_ID1] = data[VIDEO_ID1].astype(str)
        data = data[~data[VIDEO_ID1].str.contains(',', na=False)]
        data[VIDEO_ID1] = data[VIDEO_ID1].astype(int)
        return data

    @staticmethod
    def identify_create_update_relations(
            data: DataFrame,
    ):
        """
        Assign each user-content relation a label
        out of { 'create', 'update' }. If a relation
        already exists in the network, it is labeled
        as update, else create
        :param data: dataframe object pandas
        :return: dataframe object pandas
        """
        record_count = len(data)
        graph = ANGraphDb.new_connection_config().graph
        for index in range(record_count):
            print("Checking status of record ",
                  index + 1, " of ", record_count)

            customer_id = data.loc[index, CUSTOMER_ID]
            content_id = data.loc[index, CONTENT_ID]
            content_key = data.loc[index, CONTENT_LABEL]

            existing_view_count, existing_view_history = \
                ViewedUtils.get_viewed_relation_count(
                    customer_id=customer_id,
                    content_key=content_key,
                    content_id=content_id,
                    graph=graph
                )

            data.loc[index, VIEW_COUNT] = int(
                data.loc[index, VIEW_COUNT] +
                existing_view_count
            )

            if existing_view_count == 0:
                data.loc[index, STATUS] = CREATE
            else:
                existing_view_history.extend(data.loc[index, VIEW_HISTORY])
                data.at[index, VIEW_HISTORY] = existing_view_history
                data.loc[index, STATUS] = UPDATE
        graph.connection.close()
        return data

    @staticmethod
    def split_relations_on_status(
            data: DataFrame
    ):
        """
        Splits a single dataframe object into 2
        sub-components based on the status of the
        relationship
        :return: A set of two dataframe objects pandas
        """
        create_relations_df = data[data[STATUS] == CREATE]
        update_relations_df = data[data[STATUS] == UPDATE]
        return create_relations_df.reset_index(drop=True), update_relations_df.reset_index(drop=True)

    @staticmethod
    def get_view_counts(
            ubd: DataFrame,
    ) -> DataFrame:
        """
        Calculate view history attribute
        :param ubd: dataframe object pandas
        :return: dataframe object pandas
        """
        ubd = ubd.groupby(by=[CUSTOMER_ID, VIDEO_ID1]).size().reset_index()
        return ubd.rename(columns={0: VIEW_COUNT})

    @staticmethod
    def get_view_history(
            ubd: DataFrame,
    ) -> DataFrame:
        """
        Calculate view history attribute
        :param ubd: dataframe object pandas
        :return: dataframe object pandas
        """
        record_count = len(ubd)
        ubd[CREATED_ON] = ConvertTimeZone(ubd[CREATED_ON])
        ubd[VIEW_HISTORY] = [{DURATION: ubd.loc[index, DURATION],
                              CREATED_ON: ubd.loc[index, CREATED_ON]}
                             for index in range(record_count)]
        ubd = ubd.groupby(by=[CUSTOMER_ID, VIDEO_ID1])[VIEW_HISTORY] \
            .apply(list).reset_index()

        return ubd

    @staticmethod
    def merge_count_history(
            data: DataFrame
    ):
        """
        merge view_count and view_history
        :param data:
        :return:
        """
        view_count_df = UCNetworkGenerator.get_view_counts(data)
        view_history_df = UCNetworkGenerator.get_view_history(ubd=data.copy())
        new_data = view_count_df.merge(view_history_df, on=[CUSTOMER_ID, VIDEO_ID1], how="left")
        new_data = new_data.merge(data, on=[CUSTOMER_ID, VIDEO_ID1], how="inner")
        new_data = new_data.drop(columns=[CREATED_ON, DURATION])
        new_data = new_data.drop_duplicates(subset=[CUSTOMER_ID, VIDEO_ID1], ignore_index=True)
        return new_data

    @staticmethod
    def create_s3_format(
            data: DataFrame
    ):
        """
        create dataframe in required s3 format
        :param data: Dataframe object pandas
        :return: updated dataframe object pandas
        """
        tmp_df = ViewedUtils.fetch_status(data=data)
        data = data.merge(tmp_df, left_on=VIDEO_ID1, right_on=CONTENT_ID, how="left")
        data = data.drop_duplicates(subset=[CUSTOMER_ID, VIDEO_ID1], ignore_index=True)
        data = data.drop(columns=CONTENT_ID)
        data = data.rename({VIDEO_ID1: CONTENT_ID, STATUS: CONTENT_STATUS}, axis=1)
        data = data[data[CONTENT_STATUS].notna()]
        return data.reset_index(drop=True)

    @staticmethod
    def viewed_updater(
            data: DataFrame
    ):
        """
        Generate relationships between user and
        content nodes using the controller function
        of parent class
        :param data: Dataframe object pandas
        """
        data = UCNetworkGenerator.filter_features(data=data)
        data = UCNetworkGenerator.filter_users(data)
        data = ViewedUtils.get_is_paytv(data=data)
        data = UCNetworkGenerator.merge_count_history(data=data)
        data = UCNetworkGenerator.create_s3_format(data)
        data = UCNetworkGenerator.identify_create_update_relations(data=data)
        created_df, update_df = UCNetworkGenerator.split_relations_on_status(data=data)
        if len(update_df) > 0:
            update_df = ViewedUtils.fetch_edge_id(data=update_df)
            ViewedUtils.update_existing_relations(data=update_df)
        ViewedUtils.dump_relations(data=created_df)
        data = data.drop(columns=STATUS)
        return data
