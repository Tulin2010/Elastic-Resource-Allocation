"""Result from the greedy algorithm"""

from __future__ import annotations
from typing import List, Tuple
from operator import attrgetter

import numpy as np

from core.job import Job
from core.server import Server


class Result(object):
    """Generic results class"""

    def __init__(self, algorithm_name: str, jobs: List[Job],  servers: List[Server], show_money: bool = False):
        self.algorithm_name = algorithm_name

        self.show_money = show_money

        self.total_utility = sum(sum(job.utility for job in server.allocated_jobs) for server in servers)
        self.percentage_total_utility = sum(job.utility for job in jobs if job.running_server) / \
            sum(job.utility for job in jobs)
        self.percentage_jobs_allocated = sum(1 for job in jobs if job.running_server) / len(jobs)

        self.total_price = sum(job.price for job in jobs)

    def print(self, servers: List[Server]):
        """
        Prints the results data
        :param servers: The list of servers
        """
        print("Algorithm {}".format(self.algorithm_name))
        if self.show_money:
            print("Total money: {}, percentage jobs: {.3f}\n".format(self.total_price, self.percentage_jobs_allocated))
        else:
            print("Total utility: {}, Percentage utility: {:.3f}, percentage jobs: {:.3f}\n"
                  .format(self.total_utility, self.percentage_total_utility, self.percentage_jobs_allocated))

        for server in servers:
            if self.show_money:
                print("Server - {}:  Money - {}".format(server.name, sum(job.price for job in server.allocated_jobs)))
            else:
                print("Server - {}:  Utility - {}".format(server.name,
                                                          sum(job.utility for job in server.allocated_jobs)))
            print("\tStorage used: {:.3f}"
                  .format(sum(job.loading_speed for job in server.allocated_jobs) / server.max_storage))
            print("\tComputation used: {:.3f}"
                  .format(sum(job.compute_speed for job in server.allocated_jobs) / server.max_computation))
            print("\tBandwidth used: {:.3f}"
                  .format(sum(job.sending_speed for job in server.allocated_jobs) / server.max_bandwidth))

            max_job_id_len = max(len(job.name) for job in server.allocated_jobs)+1
            print("\tJob |{:^{id_len}}| Loading | Compute | Sending".format("Id", id_len=max_job_id_len))
            for job in server.allocated_jobs:
                print("\t\t|{:<{id_len}}|{:^9}|{:^9}|{:^8}"
                      .format(job.name, job.loading_speed, job.compute_speed, job.sending_speed, id_len=max_job_id_len))
            print()


class AlgorithmResults(object):
    """
    A class on the algorithm results
    where the mean and standard deviation of the result's utility, percentage utility and percentage jobs
    """

    def __init__(self, results: List[Result], optimal_results: List[Result]):
        self.algorithm_name = results[0].algorithm_name

        self.utility = (float(result.total_utility) for result in results)
        self.percentage_utility = (float(result.percentage_total_utility) for result in results)
        self.percentage_jobs = (float(result.percentage_jobs_allocated) for result in results)

        self.mean_utility = np.mean([result.total_utility for result in results])
        self.std_utility = np.std([result.percentage_total_utility - optimal.percentage_total_utility
                                   for result, optimal in zip(results, optimal_results)])
        self.mean_percentage_utility = np.mean([result.percentage_total_utility for result in results])
        self.std_percentage_utility = np.std([result.percentage_total_utility - optimal.percentage_total_utility
                                              for result, optimal in zip(results, optimal_results)])
        self.mean_percentage_jobs = np.mean([result.percentage_jobs_allocated for result in results])
        self.std_percentage_jobs = np.std([result.percentage_total_utility - optimal.percentage_total_utility
                                           for result, optimal in zip(results, optimal_results)])


def print_job_values(job_values: List[Tuple[Job, float]]):
    """
    Print the job utility values
    :param job_values: A list of tuples with the job and its value
    """
    print("\t\tJobs")
    max_job_id_len = max(len(job.name) for job, value in job_values)+1
    print("{:<{id_len}}| Value | Storage | Compute | models | Utility | Deadline ".format("Id", id_len=max_job_id_len))
    for job, value in job_values:
        # noinspection PyStringFormat
        print("{:<{id_len}}|{:^7.3f}|{:^9}|{:^9}|{:^8}|{:^9.3f}|{:^10}"
              .format(job.name, value, job.required_storage, job.required_computation,
                      job.required_results_data, job.utility, job.deadline, id_len=max_job_id_len))
    print()


def print_job_allocation(job: Job, allocated_server: Server, s: int, w: int, r: int):
    """
    Prints the job allocation
    :param job: The job
    :param allocated_server: The server
    :param s: The loading speed
    :param w: The compute speed
    :param r: The sending speed
    """
    print("Job {} - Server {}, loading speed: {}, compute speed: {}, sending speed: {}"
          .format(job.name, allocated_server.name, s, w, r))


def print_repeat_results(results: List[AlgorithmResults]):
    """
    Print repeat results
    :param results: A list of results
    """
    ordered_results = sorted(results, key=attrgetter('mean_utility'))
    print("Algorithm Results")
    print("  Utility   | Percent Utility | Percent Jobs | Name")
    print(" Mean | Std |   Mean   | Std  |  Mean  | Std | ")
    for result in results:
        print("{:6f}|{:5f}|{:10f}|{:6f}|{:6f}|{:5f}|{}"
              .format(result.mean_utility, result.std_utility,
                      result.mean_percentage_utility, result.std_percentage_utility,
                      result.mean_percentage_jobs, result.std_percentage_jobs, result.algorithm_name))
