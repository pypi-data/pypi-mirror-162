import logging
from datetime import datetime

import numpy as np
from pandas import DataFrame, concat
from math import sqrt
from graphdb import Node, Relationship
from ingestor.common import ASSIGN_CLUSTER_FEATURES, PAYTVPROVIDER_ID, GENDER, AGE, GENDER_MAP, CLUSTER_NODE_LABEL, \
    DEFAULT_CLUSTER_LABEL, IS_PAYTV, LABEL, USER_LABEL, PROPERTIES, CUSTOMER_ID, IS_PAY_TV, RELATIONSHIP, CLUSTER_ID, \
    CLUSTER_IS_PAY_TV, UPDATED_ON, CREATED_ON, PREVIOUS_CLUSTER_ID, PREVIOUS_TO_PREVIOUS_CLUSTER_ID, STATUS, ACTIVE, \
    DEFAULT_NAN
from ingestor.repository.graph_db_connection import ANGraphDb


class ClusterAllocatorUtils:

    @staticmethod
    def filter_features(
            data=DataFrame
    ) -> DataFrame:
        """
        Filter the dataframe object to only keep
        the features used for identifying
        the cluster labels
        :param data: dataframe object pandas
        :return dataframe object pandas
        """
        return data[ASSIGN_CLUSTER_FEATURES]

    @staticmethod
    def user_has_paytv(
            paytv_val
    ) -> bool:
        """
        Check whether the user is of paytv
        type or non-paytv type
        :param paytv_val: paytv provider
        value in the user record
        :return: boolean indicator
        """
        if paytv_val == -1:
            return False
        return True

    @staticmethod
    def process_user_centroid_records(
            centroids: DataFrame,
            user: DataFrame
    ):
        """
        Remove unnecessary features from user
        and centroid dataframe objects
        :param centroids: dataframe object pandas
        :param user: dataframe object pandas
        :return: processed centroid and user
        objects
        """
        user = user.reset_index(drop=True)
        user = ClusterAllocatorUtils.filter_features(data=user)
        user = user.loc[0, :].values.tolist()
        centroids = ClusterAllocatorUtils.filter_features(
            data=centroids
        )
        return centroids, user

    @staticmethod
    def process_paytv_feature(
            users: DataFrame
    ):
        """
        Process the paytvprovider_id field for
        user records
        :param users: dataframe object pandas
        :return: dataframe object pandas
        """
        users[PAYTVPROVIDER_ID] = \
            users[PAYTVPROVIDER_ID].fillna(-1)

        for index in range(len(users)):
            if not isinstance(
                    users.loc[index, PAYTVPROVIDER_ID],
                    int
            ):
                paytv = (users.loc[index, PAYTVPROVIDER_ID])[0]
                users.loc[index, PAYTVPROVIDER_ID] = \
                    paytv[PAYTVPROVIDER_ID]

        return users

    @staticmethod
    def get_paytv_wise_users(
            users
    ):
        """
        Segregate users dataframe object into
        paytv and non-paytv users
        :param users: dataframe object pandas
        :return: paytv and nonpaytv users
        dataframe objects
        """
        paytv_users = users[users[STATUS] == ACTIVE] \
            .reset_index(drop=True)
        nonpaytv_users = users[users[STATUS] != ACTIVE] \
            .reset_index(drop=True)

        return nonpaytv_users, paytv_users

    @staticmethod
    def preprocess_user_attributes(
            users: DataFrame
    ):
        if GENDER and AGE and PAYTVPROVIDER_ID not in users.columns:
            users = users.assign(gender=-1, age=-1, paytvprovider_id=-1)
            return users

        users[GENDER] = users[GENDER].apply(lambda x: GENDER_MAP[str(x)])
        users[STATUS] = users[STATUS].fillna(DEFAULT_NAN)
        users[PAYTVPROVIDER_ID] = users[PAYTVPROVIDER_ID].fillna(-1)
        users[PAYTVPROVIDER_ID] = users[PAYTVPROVIDER_ID].apply(
            lambda x: x[0][PAYTVPROVIDER_ID] if isinstance(x, list) else -1
        )
        user_paytv = users[users[STATUS] == ACTIVE]
        user_no_paytv = users[users[STATUS] != ACTIVE]
        user_no_paytv_label = user_no_paytv[user_no_paytv[STATUS] == DEFAULT_NAN]
        user_no_paytv_label[CLUSTER_NODE_LABEL] = DEFAULT_CLUSTER_LABEL
        user_no_paytv_nlabel = user_no_paytv[user_no_paytv[STATUS] != DEFAULT_NAN]
        user_no_paytv = concat([user_no_paytv_label, user_no_paytv_nlabel], axis=0)
        users = concat([user_paytv, user_no_paytv], axis=0).reset_index(drop=True)

        return users.reset_index(drop=True)

    @staticmethod
    def get_distance(
            vector_a: list,
            vector_b: list
    ):
        """
        Compute Euclidean Distance between two vectors
        :param vector_a: Vector for user features
        :param vector_b: Vector for corresponding
        centroid features
        :return: Euclidean Distance
        """
        vector_a = [float(val) for val in vector_a]
        vector_b = [float(val) for val in vector_b]
        return sqrt(
            sum(
                [(va - vb) ** 2 for va, vb in zip(
                    vector_a, vector_b
                )]
            )
        )

    @staticmethod
    def prepare_cluster_data(
            paytv_cluster_user: DataFrame,
            no_paytv_cluster_user: DataFrame
    ):
        """
        Add fields to update cluster data on S3 and redis
        :param paytv_cluster_user: DataFrame object pandas
        :param no_paytv_cluster_user: DataFrame object pandas
        """
        if not paytv_cluster_user.empty:
            paytv_cluster_user[CLUSTER_NODE_LABEL] = paytv_cluster_user[CLUSTER_NODE_LABEL].astype(int)
            paytv_cluster_user[IS_PAYTV] = "True"
        if not no_paytv_cluster_user.empty:
            no_paytv_cluster_user[CLUSTER_NODE_LABEL] = no_paytv_cluster_user[CLUSTER_NODE_LABEL].astype(int)
            no_paytv_cluster_user[IS_PAYTV] = np.where(
                (no_paytv_cluster_user[CLUSTER_NODE_LABEL] != -999), "False", np.nan
            )
        cluster_data = concat([paytv_cluster_user, no_paytv_cluster_user], axis=0)
        return cluster_data.reset_index(drop=True)

    @staticmethod
    def dump_cluster_relations(
            dump_data: DataFrame,
            destination_label: str,
            relation_label: str,
            df_attribute: str
    ):
        """
        Function to dump user preferences in graphdb
        using custom query.
        :param dump_data: preference dataframe to be dumped
        :param destination_label: label of destination node
        :param relation_label: name of edge
        :param df_attribute: dataframe attribute
        """
        dump_data = dump_data.reset_index(drop=True)
        graph = ANGraphDb.new_connection_config().graph
        print("Starting dumping {}".format(relation_label).center(100, '*'))
        for index in range(len(dump_data)):
            try:
                node_from = Node.parse_obj(
                    {LABEL: USER_LABEL, PROPERTIES: {CUSTOMER_ID: str(dump_data.loc[index, CUSTOMER_ID])}}
                )
                node_to = Node.parse_obj(
                    {
                        LABEL: destination_label,
                        PROPERTIES: {CLUSTER_NODE_LABEL: int(dump_data.loc[index, df_attribute]),
                                     IS_PAY_TV: str(dump_data.loc[index, IS_PAYTV])}
                    }
                )
                if int(dump_data.loc[index, df_attribute]) == -999:
                    node_to = Node.parse_obj(
                        {
                            LABEL: destination_label,
                            PROPERTIES: {CLUSTER_NODE_LABEL: int(dump_data.loc[index, df_attribute])}
                        }
                    )
                graph.create_relationship_without_upsert(
                    node_from, node_to, rel=Relationship(**{RELATIONSHIP: relation_label})
                )
            except Exception as e:
                logging.error(f"Error while creating relation {relation_label} on graph, Error: {e}")
                continue
        print("Successfully dumped all {}...".format(relation_label))
        graph.connection.close()

    @staticmethod
    def prepare_s3_format(
            new_cluster_data: DataFrame
    ) -> DataFrame:
        """
        Function to prepare cluster data as per required
        format to save in S3
        :param new_cluster_data: Dataframe object pandas
        :return: Dataframe object pandas
        """
        new_cluster_data = new_cluster_data.rename(columns={CLUSTER_NODE_LABEL: CLUSTER_ID,
                                                            IS_PAYTV: CLUSTER_IS_PAY_TV})
        new_cluster_data[IS_PAY_TV] = new_cluster_data[CLUSTER_IS_PAY_TV]
        new_cluster_data[CLUSTER_ID] = new_cluster_data[CLUSTER_ID].astype(int)
        new_cluster_data[IS_PAY_TV] = new_cluster_data[IS_PAY_TV].replace(["nan"], "False")
        new_cluster_data[PREVIOUS_CLUSTER_ID] = ''
        new_cluster_data[PREVIOUS_TO_PREVIOUS_CLUSTER_ID] = ''
        new_cluster_data[CREATED_ON] = datetime.utcnow().isoformat()
        new_cluster_data[UPDATED_ON] = datetime.utcnow().isoformat()

        return new_cluster_data.reset_index(drop=True)
