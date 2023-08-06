import numpy as np
from scipy import spatial, stats


def unmatched_components_rate(X, X_prime, eps=1e-4):
    unmatched_components = 0
    for feature_id in range(len(X)):
        if abs(X[feature_id] - X_prime[feature_id]) > eps:
            unmatched_components += 1
    return unmatched_components / len(X)


def euclidean_distance(X, X_prime):
    X_norm, X_prime_norm = np.linalg.norm(X), np.linalg.norm(X_prime)
    X_normalized, X_prime_normalized = X / X_norm, X_prime / X_prime_norm
    return np.linalg.norm(X_normalized - X_prime_normalized)


def cosine_distance(X, X_prime):
    return spatial.distance.cosine(X, X_prime)


def jaccard_distance(X, X_prime):
    s_u = set(X)
    s_v = set(X_prime)
    s_u_and_v = s_u.intersection(s_v)
    s_u_or_v = s_u.union(s_v)
    Js = len(s_u_and_v) / float(len(s_u_or_v))
    Jd = 1 - Js
    return Jd


def pearson_correlation_distance(X, X_prime):
    rho = stats.pearsonr(X, X_prime)[0]
    rho_d = 1 - rho
    return rho_d