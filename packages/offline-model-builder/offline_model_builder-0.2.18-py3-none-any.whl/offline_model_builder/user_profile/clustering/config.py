SPARSITY_THRESHOLD = 0.98
K_NO_PAYTV = 30
K_PAYTV = 26
MINIBATCH_SIZE = 6
MIN_MEMBER_COUNT = 15
TENDENCY_CUTOFF = 3
ENSEMBLE_SD_CUTOFF = 5
TOP_N_MEMBERS_COUNT = 5

GENDER_MAP = {
    0: -1,
    "na": -1,
    "nan": -1,
    "m": 0,
    "f": 1
}
USER_CLUSTER_DIST = "data/historical/user/raw/mapping/31052022/user_cluster_dist.pkl"
PAY_TV_CENTROID_FEATURES = "data/historical/user/raw/mapping/31052022/paytv_minibatch_kmeans_centroids_feature.csv"
PAY_TV_USER_CLUSTER_FEATURE = "data/historical/user/raw/mapping/31052022/paytv_minibatch_kmeans_users_clustering_feature.csv"
NO_PAY_TV_USER_CLUSTER_FEATURE = 'data/historical/user/raw/mapping/31052022/no_paytv_minibatch_kmeans_users_clustering_feature.csv'
NO_PAY_TV_CENTROID_FEATURES = "data/historical/user/raw/mapping/31052022/no_paytv_minibatch_kmeans_centroids_feature.csv"
PAYTV_USER_CLUSTER_MAPPING_PATH = "data/historical/user/raw/mapping/31052022/paytv_minibatch_kmeans.csv"
NO_PAYTV_USER_CLUSTER_MAPPING_PATH = 'data/historical/user/raw/mapping/31052022/nonpaytv_minibatch_kmeans.csv'
PAY_TV_CLUSTER_CENTROID = 'data/historical/user/raw/mapping/31052022/paytv_minibatch_kmeans_centroids.csv'
NO_PAY_TV_CLUSTER_CENTROID = 'data/historical/user/raw/mapping/31052022/no_paytv_minibatch_kmeans_centroids.csv'
