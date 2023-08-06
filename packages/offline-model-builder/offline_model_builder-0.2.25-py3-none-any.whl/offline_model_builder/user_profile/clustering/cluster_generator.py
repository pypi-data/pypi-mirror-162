from offline_model_builder.common.read_write_s3 import ConnectS3
from pandas import DataFrame, Series, get_dummies
from sklearn.cluster import MiniBatchKMeans, KMeans

from offline_model_builder.user_profile.clustering.clustering_utils import ClusteringUtils
from offline_model_builder.user_profile.clustering.config import K_PAYTV, K_NO_PAYTV, MINIBATCH_SIZE
from offline_model_builder.user_profile.constants import CUSTOMER_ID, MINIBATCH_KMEANS_FEATURE, BIRTHDAY, \
    CUSTOMER_CREATED_ON, \
    CUSTOMER_MODIFIED_ON, PAYTVPROVIDER_ID, GENDER, UD_KEY, IS_PAY_TV, GENDER_NAN, STATUS, PAY_TV, NO_PAY_TV, \
    VISIONPLUS_DEV, CLUSTER_MODEL_PATH


class ClusterGenerator(ClusteringUtils):

    def __init__(
            self,
            data=DataFrame
    ):
        data[CUSTOMER_ID] = data[CUSTOMER_ID].astype(str)
        ClusteringUtils.__init__(self, data=data)
        self.clusters = DataFrame()

    def get_kmeans(
            self,
            features: DataFrame,
            paytv: bool
    ) -> Series:
        """
        Generate KMeans Clusters
        :param features: user features
        :return: list of assigned cluster values
        """
        if paytv:
            k = K_PAYTV
        else:
            k = K_NO_PAYTV
        model = KMeans(n_clusters=k, random_state=0)
        return model.fit_predict(features)

    def get_minibatch_kmeans(
            self,
            features: DataFrame,
            paytv: bool
    ) -> Series:
        """
        Generate MiniBatch-KMeans clusters
        :param features: user features
        :return: list of assigned cluster values
        """
        if paytv:
            k = K_PAYTV
        else:
            k = K_NO_PAYTV
        model = MiniBatchKMeans(n_clusters=k, init='k-means++', random_state=None,
                                batch_size=MINIBATCH_SIZE)
        model.fit(features)
        result = model.predict(features)
        ctl = ConnectS3()
        resource = ctl.create_connection()
        filename = MINIBATCH_KMEANS_FEATURE + "_" + (PAY_TV if paytv else NO_PAY_TV) + ".pkl"
        print("Write model to S3...")
        ctl.write_pkl_to_s3(bucket_name=VISIONPLUS_DEV,
                            object_name=CLUSTER_MODEL_PATH + filename,
                            data=model,
                            resource=resource)
        return result

    def controller(
            self,
            paytv: bool
    ):
        """
        Driver function for Cluster based feature
        processing and results generation
        :return: None
        """
        features = self.drop_sparse_features()

        self.clusters[CUSTOMER_ID] = features[CUSTOMER_ID]

        features = get_dummies(
            features,
            columns=[GENDER, PAYTVPROVIDER_ID]
        )

        # since we do not want to pass an identifier as a clustering feature
        if paytv:
            features = self.remove_attributes(attributes=features,
                                              to_drop=[CUSTOMER_ID,
                                                       BIRTHDAY,
                                                       CUSTOMER_CREATED_ON,
                                                       CUSTOMER_MODIFIED_ON,
                                                       IS_PAY_TV,
                                                       UD_KEY,
                                                       GENDER_NAN,
                                                       STATUS])
        else:
            features = self.remove_attributes(attributes=features,
                                              to_drop=[CUSTOMER_ID,
                                                       BIRTHDAY,
                                                       CUSTOMER_CREATED_ON,
                                                       CUSTOMER_MODIFIED_ON,
                                                       UD_KEY,
                                                       GENDER_NAN])

        self.clusters[MINIBATCH_KMEANS_FEATURE] = self.get_minibatch_kmeans(features=features, paytv=paytv)
