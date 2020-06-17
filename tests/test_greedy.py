"""
Tests the greedy testing
Todo add greedy testing for greedy and matrix greedy optimisations
"""

from __future__ import annotations

from typing import List, Dict, Tuple, Union

from tqdm import tqdm
import numpy as np

from core.core import reset_model
from core.result import Result
from greedy.greedy import greedy_algorithm
from greedy.resource_allocation_policy import SumPercentage, policies as resource_allocation_policies
from greedy.server_selection_policy import SumResources, all_policies as server_selection_policies
from greedy.value_density import UtilityDeadlinePerResource, all_policies as value_density_policies
from greedy_matrix.allocation_value_policy import SumServerMaxPercentage
from greedy_matrix.matrix_greedy import greedy_matrix_algorithm
from model.model_distribution import load_model_distribution, ModelDistribution


def test_greedy_policies(repeats: int = 5):
    distribution_name, task_distributions, server_distributions = load_model_distribution('models/basic.mdl')
    model = ModelDistribution(distribution_name, task_distributions, 20, server_distributions, 3)

    policy_results: Dict[str, Union[List[Result], Tuple[List[Result], float, float]]] = {}
    for repeat in tqdm(range(repeats)):
        tasks, servers = model.create()

        for value_density in value_density_policies:
            for server_selection_policy in server_selection_policies:
                for resource_allocation_policy in resource_allocation_policies:
                    reset_model(tasks, servers)

                    result = greedy_algorithm(tasks, servers, value_density, server_selection_policy,
                                              resource_allocation_policy)
                    print(f'\t{result.algorithm} - {result.data["solve time"]} secs')
                    if result.algorithm in policy_results:
                        policy_results[result.algorithm].append(result)
                    else:
                        policy_results[result.algorithm] = [result]

    for algo, results in policy_results.items():
        policy_results[algo] = (policy_results[algo],
                                float(np.mean([r.social_welfare for r in results])),
                                float(np.mean([r.data['solve time'] for r in results])))
    print(f'Algo | Avg SW | Avg Time | Social Welfare')
    for algo, (results, avg_sw, avg_time) in sorted(policy_results.items(), key=lambda r: r[2]):
        print(f'{algo} | {avg_sw} | {avg_time} | [{" ".join([result.sum_value for result in results])}]')


def test_optimisation(repeats: int = 10):
    """
    Compare the greedy and greedy matrix algorithm, particular in terms of solve time and social welfare#

    :param repeats: Number of repeats
    """
    distribution_name, task_distributions, server_distributions = load_model_distribution('models/basic.mdl')
    model = ModelDistribution(distribution_name, task_distributions, 20, server_distributions, 3)

    greedy_results, greedy_matrix_time = [], []
    print(f' Greedy     | Greedy Matrix')
    print(f' Time | Sum | Time   | Sum')
    for repeat in range(repeats):
        tasks, servers = model.create()

        greedy_result = greedy_algorithm(tasks, servers, UtilityDeadlinePerResource(), SumResources(), SumPercentage())
        greedy_results.append(greedy_result)

        reset_model(tasks, servers)
        greedy_matrix_results = greedy_matrix_algorithm(tasks, servers, SumServerMaxPercentage())

        print(f'{str(greedy_result.data["solve time"]):5} | {greedy_result.social_welfare:3} | '
              f'{str(greedy_matrix_results.data["solve time"]):5} | {greedy_matrix_results.social_welfare:3}')


if __name__ == "__main__":
    test_greedy_policies()
