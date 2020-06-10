"""Result from the greedy algorithm"""

from __future__ import annotations

from typing import List

from src.core.job import Job
from src.core.server import Server


class Result(object):
    """Generic results class"""

    def __init__(self, algorithm_name: str, jobs: List[Job], servers: List[Server], solve_time: float,
                 show_money: bool = False, **kwargs):
        self.algorithm_name = algorithm_name

        self.data = dict()
        self.data['solve_time'] = round(solve_time, 3)

        # General total information
        self.sum_value = sum(sum(job.value for job in server.allocated_jobs) for server in servers)
        self.data['sum value'] = self.sum_value
        self.data['percentage value'] = round(sum(job.value for job in jobs if job.running_server) /
                                              sum(job.value for job in jobs), 3)
        self.data['percentage jobs'] = round(sum(1 for job in jobs if job.running_server) / len(jobs), 3)

        # The server information
        self.data['server value'] = {
            server.name: sum(job.value for job in server.allocated_jobs) for server in servers
        }
        self.data['server storage usage'] = {
            server.name: round(1 - server.available_storage / server.storage_capacity, 3) for server in servers
        }
        self.data['server computation usage'] = {
            server.name: round(1 - server.available_computation / server.computation_capacity, 3) for server in servers
        }
        self.data['server bandwidth usage'] = {
            server.name: round(1 - server.available_bandwidth / server.bandwidth_capacity, 3) for server in servers
        }
        self.data['num jobs'] = {
            server.name: len(server.allocated_jobs) for server in servers
        }

        # Additional information
        for key, value in kwargs.items():
            self.data[key] = value

        # For auction to add the price information
        if show_money:
            self.data['total money'] = sum(job.price for job in jobs)
            self.data['prices'] = {job.name: job.price for job in jobs}
            self.data['revenues'] = {server.name: server.revenue for server in servers}
            self.data['price change'] = {server.name: server.price_change for server in servers}

    def store(self, **kwargs):
        """
        Returns the results values for storage

        :return: The results values
        """
        for key, value in kwargs.items():
            self.data[key] = value
        return self.data