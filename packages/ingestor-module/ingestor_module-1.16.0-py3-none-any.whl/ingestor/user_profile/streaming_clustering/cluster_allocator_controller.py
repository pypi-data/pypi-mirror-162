import pandas as pd
from pandas import DataFrame, concat
import numpy as np

from ingestor.common import CLUSTER_NODE_LABEL, IS_PAYTV, GENDER, PAYTVPROVIDER_ID, CUSTOMER_ID, \
    NEW_USER_CLUSTER_RELATIONSHIP_LABEL
from ingestor.user_profile.streaming_clustering.cluster_allocator_utils import ClusterAllocatorUtils
from ingestor.repository.graph_db_connection import ANGraphDb


class ClusterAllocatorController:

    @staticmethod
    def get_centroids():
        """
        Retrieve all the centroids for a
        particular cluster type from GraphDB
        :return: list of centroids and
        their properties
        """
        graph = ANGraphDb.new_connection_config().graph
        response = graph.custom_query(
            query="g.V().hasLabel('centroid').has('" +
                  CLUSTER_NODE_LABEL +
                  "').path().by(elementMap())", payload={CLUSTER_NODE_LABEL: CLUSTER_NODE_LABEL}
        )[0]
        graph.connection.close()
        return response

    @staticmethod
    def filter_centroids(
            is_paytv: bool,
            centroids: list
    ) -> list:
        """
        Filter out the centroids that do not belong
        to the same paytv type as that of the user
        :param is_paytv: paytv indicator boolean
        :param centroids: list of centroids
        :return: list of centroids that are to be
        proceeded with
        """
        centroids_to_keep = []

        for centroid in centroids:
            if IS_PAYTV in centroid[0].keys() and str(is_paytv) == centroid[0][IS_PAYTV]:
                centroids_to_keep.append(centroid[0])

        return centroids_to_keep

    @staticmethod
    def get_paytv_filtered_centroids():
        """
        Retrieve all centroids and filter them
        as per their respective paytv types
        into a dictionary. Dictionary key True
        holds centroids with is_paytv flag set
        to True and False for the rest
        :return: dictionary object
        """
        centroid_nodes = ClusterAllocatorController.get_centroids()
        centroids = {
            'True': ClusterAllocatorController.filter_centroids(
                is_paytv=True,
                centroids=centroid_nodes
            ),
            'False': ClusterAllocatorController.filter_centroids(
                is_paytv=False,
                centroids=centroid_nodes
            )
        }

        paytv_centroids = DataFrame.from_dict(centroids["True"])
        nopaytv_centroids = DataFrame.from_dict(centroids["False"])

        return paytv_centroids, nopaytv_centroids

    @staticmethod
    def compute_user_centroid_scores(
            centroids: DataFrame,
            user: list
    ) -> list:
        """
        Calculate Euclidean Distance scores between
        the considered user and all the centroids
        of the same paytv type.
        :param centroids: Dataframe object pandas
        :param user: list of features for the user
        :return: list of centroid scores
        """
        scores = []
        for index in range(len(centroids)):
            centroid = \
                centroids.loc[index, :].values.tolist()
            scores.append(
                ClusterAllocatorUtils.get_distance(
                    vector_a=user,
                    vector_b=centroid
                )
            )
        return scores

    @staticmethod
    def find_centroid_for_user(
            user: DataFrame,
            centroids: DataFrame
    ) -> int:
        """
        Find the index of the most suitable
        centroid to be assigned for the user
        :param user: dataframe object pandas
        :param centroids: dataframe object pandas
        :return: integer value for the
        centroid index
        """
        centroids, user = \
            ClusterAllocatorUtils.process_user_centroid_records(
                centroids=centroids,
                user=user
            )
        scores = \
            ClusterAllocatorController.compute_user_centroid_scores(
                centroids=centroids,
                user=user
            )
        min_value = min(scores)
        return scores.index(min_value)

    @staticmethod
    def check_features_available(
            users: DataFrame,
            index: int
    ) -> bool:
        """
        Check if any feature values are available for the user
        :param users: dataframe object pandas
        :param index: user record index
        :return: Boolean indicator
        """
        if (users.loc[index, GENDER] == -1 and (
                users.loc[index, PAYTVPROVIDER_ID] == -1)):
            return False
        return True

    @staticmethod
    def find_cluster_label(
            users=DataFrame,
            centroids=DataFrame
    ) -> DataFrame:
        """
        Find centroid for the users based on the
        dataframe supplied.
        :param users: paytv or nopaytv user dataframe
        :param centroids: paytv or no paytv centroids
        :return: dataframe with cluster label
        """
        if CLUSTER_NODE_LABEL not in users.columns:
            users[CLUSTER_NODE_LABEL] = np.nan

        users_na = users[users[CLUSTER_NODE_LABEL].isna()]
        users_int = users[~users[CLUSTER_NODE_LABEL].isna()]
        if len(users_na) > 0:
            users_na[CLUSTER_NODE_LABEL] = users_na[CLUSTER_NODE_LABEL].fillna(-1)
            users_na[CLUSTER_NODE_LABEL][users_na[CLUSTER_NODE_LABEL] == -1] = \
                list(users_na[users_na[CLUSTER_NODE_LABEL] == -1].index)
            users_na[CLUSTER_NODE_LABEL] = users_na[CLUSTER_NODE_LABEL].apply(
                lambda x: ClusterAllocatorController.find_centroid_for_user(
                    user=DataFrame(users.loc[x, :]).T,
                    centroids=centroids
                )
            )

            users = concat([users_na, users_int], axis=0)

        return users.reset_index(drop=True)

    @staticmethod
    def controller(
            users=DataFrame
    ):
        """
        Driver function for finding cluster labels
        for new users
        :param users: dataframe object pandas
        :return: None, updates the relationships in graphDB
        """
        users = ClusterAllocatorUtils.preprocess_user_attributes(users)

        paytv_centroids, nonpaytv_centroids = \
            ClusterAllocatorController.get_paytv_filtered_centroids()

        nonpaytv_users, paytv_users = \
            ClusterAllocatorUtils.get_paytv_wise_users(users)

        paytv_users = ClusterAllocatorController.find_cluster_label(paytv_users, paytv_centroids)
        nonpaytv_users = ClusterAllocatorController.find_cluster_label(nonpaytv_users, nonpaytv_centroids)

        paytv_users = paytv_users[[CUSTOMER_ID, CLUSTER_NODE_LABEL]]
        nonpaytv_users = nonpaytv_users[[CUSTOMER_ID, CLUSTER_NODE_LABEL]]
        cluster_data = ClusterAllocatorUtils.prepare_cluster_data(paytv_cluster_user=paytv_users,
                                                                  no_paytv_cluster_user=nonpaytv_users)

        ClusterAllocatorUtils.dump_cluster_relations(dump_data=cluster_data,
                                                     destination_label=CLUSTER_NODE_LABEL,
                                                     relation_label=NEW_USER_CLUSTER_RELATIONSHIP_LABEL,
                                                     df_attribute=CLUSTER_NODE_LABEL)
        cluster_data = ClusterAllocatorUtils.prepare_s3_format(new_cluster_data=cluster_data)
        return cluster_data

