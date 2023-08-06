from pandas import DataFrame

from offline_model_builder.user_profile.clustering.config import SPARSITY_THRESHOLD
from offline_model_builder.user_profile.constants import INTERMEDIATE_RESULTS_DIRECTORY, \
    NAN_DUMMY_FEATURE


class ClusteringUtils:

    def __init__(
            self,
            data=DataFrame,
    ):
        """
        :param data: consolidated user demographics
        and behaviour data
        """
        self.data = data

    def drop_sparse_features(
            self,
    ) -> DataFrame:
        """
        drop sparse features from being considered
        for clustering purposes
        :return:
        """
        size = len(self.data)
        features_to_drop = []

        self.data = self.data.fillna(0)

        for feature in self.data.columns:
            values = self.data[feature].to_numpy().tolist()
            # More the frequency of zero, greater the sparsity
            sparsity = sum(map(lambda val: val == 0, values)) / size
            # identify features greater than specified threshold
            if (sparsity > SPARSITY_THRESHOLD) or (feature[len(feature) - 4:] == NAN_DUMMY_FEATURE):
                features_to_drop.append(feature)

        features = self.data.drop(columns=features_to_drop)
        
        return features

    def remove_attributes(
            self,
            attributes: DataFrame,
            to_drop: list
    ) -> DataFrame:
        """
        removes the specified list of attributes
        from a given dataframe
        :param attributes: dataframe object pandas
        :param to_drop: list of df columns
        :return:
        """
        feature_set = attributes.drop(columns=to_drop)
        return feature_set

    def save_intermediate_results(
            self,
            df: DataFrame,
            filename: str
    ):
        """
        Can be called at any point if in
        case any df result needs to be saved for
        computation or observation purposes
        :param df: dataframe object pandas
        :param filename: df shall be saved with this
        Must include .csv at the end.
        :return:
        """
        df.to_csv(INTERMEDIATE_RESULTS_DIRECTORY + "/" + filename,
                  index=False)
