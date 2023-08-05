#
# AUTOMATICALLY GENERATED FILE, DO NOT EDIT!
#

"""Pybind11 version of the BMCToolkit C++ library."""
from __future__ import annotations
import BMCToolkit
import typing
import numpy
_Shape = typing.Tuple[int, ...]

__all__ = [
    "KL_divergence_rate_difference_between_models",
    "compute_bmcs_parameters",
    "compute_cluster_difference",
    "compute_cluster_improvement",
    "compute_clusters_from_trajectory",
    "compute_k_means",
    "compute_spectral_clustering",
    "compute_spectral_norm",
    "generate_sample_path",
    "generate_trimmed_matrix",
    "get_equilibrium_distribution_lift",
    "get_equilibrium_distribution_proj",
    "get_frequency_matrix_lift",
    "get_frequency_matrix_proj",
    "get_transition_matrix_lift",
    "get_transition_matrix_proj",
    "label_clusters_by_decr_equilibrium_distribution",
    "label_clusters_by_decr_size",
    "label_clusters_by_incr_equilibrium_distribution",
    "label_clusters_by_incr_size",
    "trim_frequency_matrix"
]


def KL_divergence_rate_difference_between_models(transition_matrix_P: numpy.ndarray[numpy.float64, _Shape[m, n]], transition_matrix_Q: numpy.ndarray[numpy.float64, _Shape[m, n]], sample_path_from_R: numpy.ndarray[numpy.uint32, _Shape[m, 1]], mixing_time_of_R_estimate_as_a_percentage_of_time_horizon: float = 0.1, confidence_level: float = 0.95, time_horizon: int = -1) -> typing.Dict[int, typing.Tuple[float, float]]:
    """
    If R is the ground truth (which generated the sample path) and P and Q are your models, then this calculates ( KL(R;Q) - KL(R;P) ) / window for various window sizes.
    """
def compute_bmcs_parameters(frequency_matrix: numpy.ndarray[numpy.uint32, _Shape[m, n]], cluster_assignment: numpy.ndarray[numpy.uint32, _Shape[m, 1]], verbose: bool = False) -> numpy.ndarray[numpy.float64, _Shape[m, n]]:
    """
    Estimates the parameters of a Block Markov Chain.
    """
def compute_cluster_difference(assignment_a: numpy.ndarray[numpy.uint32, _Shape[m, 1]], assignment_b: numpy.ndarray[numpy.uint32, _Shape[m, 1]]) -> int:
    """
    Computes the difference between two clusters.
    """
def compute_cluster_improvement(frequency_matrix: numpy.ndarray[numpy.uint32, _Shape[m, n]], cluster_assignment: numpy.ndarray[numpy.uint32, _Shape[m, 1]], max_iterations: int, verbose: bool = False) -> numpy.ndarray[numpy.uint32, _Shape[m, 1]]:
    """
    Executes the cluster improvement algorithm.
    """
def compute_clusters_from_trajectory(trajectory: numpy.ndarray[numpy.uint32, _Shape[m, 1]], num_states: int, num_clusters: int, seed: int = 1987, max_trials: int = 10000, max_iterations: int = 1000, num_largest_singular_values_to_ignore: int = 0, num_extra_singular_values_to_use: int = 0, verbose: bool = False) -> numpy.ndarray[numpy.uint32, _Shape[m, 1]]:
    """
    Compute the clusters from a trajectory. This function does the spectral clustering algorithm as well as the cluster improvement algorithm.
    """
def compute_k_means(matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], num_clusters: int, seed: int = 1987, max_trials: int = 10000, max_iterations: int = 1000, verbose: bool = False) -> numpy.ndarray[numpy.uint32, _Shape[m, 1]]:
    """
    A C++ implementation to compute a K-means assignment.
    """
def compute_spectral_clustering(matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], num_clusters: int, seed: int = 1987, max_trials: int = 10000, max_iterations: int = 1000, num_largest_singular_values_to_ignore: int = 0, num_extra_singular_values_to_use: int = 0, verbose: bool = False) -> numpy.ndarray[numpy.uint32, _Shape[m, 1]]:
    """
    Execute the spectral clustering algorithm.
    """
def compute_spectral_norm(matrix: numpy.ndarray[numpy.float64, _Shape[m, n]]) -> float:
    """
    Compute a spectral norm.
    """
def generate_sample_path(transition_matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], rel_size: numpy.ndarray[numpy.float64, _Shape[m, 1]], abs_size: int, trajectory_length: int, seed: int) -> numpy.ndarray[numpy.uint32, _Shape[1, n]]:
    """
    Generate a random sample path of a Block Markov Chain.
    """
def generate_trimmed_matrix(transition_matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], rel_size: numpy.ndarray[numpy.float64, _Shape[m, 1]], abs_size: int, trajectory_length: int, num_states_to_trim: int, seed: int) -> numpy.ndarray[numpy.uint32, _Shape[m, n]]:
    """
    Generate a random trimmed frequency matrix of a Block Markov Chain.
    """
def get_equilibrium_distribution_lift(transition_matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], relative_sizes: numpy.ndarray[numpy.float64, _Shape[m, 1]], abs_size: int) -> numpy.ndarray[numpy.float64, _Shape[m, 1]]:
    """
    Returns the lifted equilibrium distribution of a Block Markov Chain.
    """
def get_equilibrium_distribution_proj(transition_matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], relative_sizes: numpy.ndarray[numpy.float64, _Shape[m, 1]], abs_size: int) -> numpy.ndarray[numpy.float64, _Shape[m, 1]]:
    """
    Returns the projected equilibrium distribution of a Block Markov Chain.
    """
def get_frequency_matrix_lift(transition_matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], relative_sizes: numpy.ndarray[numpy.float64, _Shape[m, 1]], abs_size: int) -> numpy.ndarray[numpy.float64, _Shape[m, n]]:
    """
    Returns a BMCs lifted frequency matrix.
    """
def get_frequency_matrix_proj(transition_matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], relative_sizes: numpy.ndarray[numpy.float64, _Shape[m, 1]], abs_size: int) -> numpy.ndarray[numpy.float64, _Shape[m, n]]:
    """
    Returns the projected frequency matrix of a Block Markov Chain.
    """
def get_transition_matrix_lift(transition_matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], relative_sizes: numpy.ndarray[numpy.float64, _Shape[m, 1]], abs_size: int) -> numpy.ndarray[numpy.float64, _Shape[m, n]]:
    """
    Returns the lifted transition matrix of a Block Markov Chain.
    """
def get_transition_matrix_proj(transition_matrix: numpy.ndarray[numpy.float64, _Shape[m, n]], relative_sizes: numpy.ndarray[numpy.float64, _Shape[m, 1]], abs_size: int) -> numpy.ndarray[numpy.float64, _Shape[m, n]]:
    """
    Returns the projected transition matrix of a Block Markov Chain.
    """
def label_clusters_by_decr_equilibrium_distribution(frequency_matrix: numpy.ndarray[numpy.uint32, _Shape[m, n]], cluster_assignment: numpy.ndarray[numpy.uint32, _Shape[m, 1]]) -> numpy.ndarray[numpy.uint32, _Shape[m, n]]:
    """
    Relabels a cluster assignment by increasing equilibrium distribution.
    """
def label_clusters_by_decr_size(frequency_matrix: numpy.ndarray[numpy.uint32, _Shape[m, n]], cluster_assignment: numpy.ndarray[numpy.uint32, _Shape[m, 1]]) -> numpy.ndarray[numpy.uint32, _Shape[m, n]]:
    """
    Relabels a cluster assignment by increasing cluster size.
    """
def label_clusters_by_incr_equilibrium_distribution(frequency_matrix: numpy.ndarray[numpy.uint32, _Shape[m, n]], cluster_assignment: numpy.ndarray[numpy.uint32, _Shape[m, 1]]) -> numpy.ndarray[numpy.uint32, _Shape[m, n]]:
    """
    Relabels a cluster assignment by increasing equilibrium distribution.
    """
def label_clusters_by_incr_size(frequency_matrix: numpy.ndarray[numpy.uint32, _Shape[m, n]], cluster_assignment: numpy.ndarray[numpy.uint32, _Shape[m, 1]]) -> numpy.ndarray[numpy.uint32, _Shape[m, n]]:
    """
    Relabels a cluster assignment by increasing cluster size.
    """
def trim_frequency_matrix(frequency_matrix: numpy.ndarray[numpy.uint32, _Shape[m, n]], num_states_to_trim: int) -> numpy.ndarray[numpy.uint32, _Shape[m, n]]:
    """
    Zeroes out a desired number of rows and columns corresponding to the most-visited states.
    """
__version__ = 'dev'
