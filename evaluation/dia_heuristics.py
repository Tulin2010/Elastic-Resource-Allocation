"""
Evaluates the price change and initial price for the decentralised iterative auction. This is done in the two stages;
    a grid search for the price change and initial cost of the algorithm and the second part is to investigate the
    results when servers have non-uniform price change and initial price variables that are generated through
    gaussian random functions.
"""

from __future__ import annotations

import json
import pprint
from random import gauss
from typing import Iterable

from src.auctions.decentralised_iterative_auction import optimal_decentralised_iterative_auction
from src.core.core import reset_model, set_server_heuristics
from src.extra.io import parse_args, results_filename
from src.extra.model import ModelDistribution


def dia_heuristic_grid_search(model_dist: ModelDistribution, repeat_num: int, repeats: int = 50, time_limit: int = 2,
                              initial_prices: Iterable[int] = (20, 30, 35, 40),
                              price_changes: Iterable[int] = (1, 2, 5, 8, 10)):
    """
    Evaluates the difference in results with the decentralised iterative auction uses different price changes and
        initial price variables

    :param model_dist: The model distribution
    :param repeat_num: The repeat number
    :param repeats: The number of repeats
    :param time_limit: The time limit for the DIA Auction
    :param initial_prices: The initial price for auctions
    :param price_changes: The price change of the servers
    """
    print(f'DIA Heuristic grid search with initial prices: {initial_prices}, price changes: {price_changes}'
          f'for {model_dist.name} model with {model_dist.num_tasks} tasks and {model_dist.num_servers} servers')
    model_results = []
    pp = pprint.PrettyPrinter()
    filename = results_filename('dia_heuristic_grid_search', model_dist, repeat_num)

    for repeat in range(repeats):
        print(f'\nRepeat: {repeat}')
        tasks, servers = model_dist.generate()
        algorithm_results = {'model': {
            'tasks': [task.save() for task in tasks], 'servers': [server.save() for server in servers]
        }}
        pp.pprint(algorithm_results)

        for initial_price in initial_prices:
            for price_change in price_changes:
                set_server_heuristics(servers, price_change=price_change, initial_price=initial_price)

                results = optimal_decentralised_iterative_auction(tasks, servers, time_limit)
                algorithm_results[f'IP: {initial_price}, PC: {price_change}'] = results.store(
                    **{'initial price': initial_price, 'price change': price_change}
                )
                results.pretty_print()
                reset_model(tasks, servers)

        model_results.append(algorithm_results)

        # Save the results to the file
        with open(filename, 'w') as file:
            json.dump(model_results, file)
    print('Finished running')


def non_uniform_server_heuristics(model_dist: ModelDistribution, repeat_num: int, repeats: int = 20,
                                  time_limit: int = 2, random_repeats: int = 10,
                                  price_change_mean: int = 3, price_change_std: int = 3,
                                  initial_price_mean: int = 20, initial_price_std: int = 4):
    """
    Evaluates the effect of the server heuristics when they are non-uniform (all server's dont use the same value)

    :param model_dist: The model distribution
    :param repeat_num: The repeat number
    :param repeats: The number of repeats
    :param time_limit: The time limit for the decentralised iterative auction
    :param random_repeats: The number of random repeats for each model generated
    :param price_change_mean: The mean price change value
    :param price_change_std: The standard deviation of the price change value
    :param initial_price_mean: The mean initial change value
    :param initial_price_std: The standard deviation of the initial change value
    """
    print(f'DIA non-uniform heuristic investigation with initial price mean: {initial_price_mean} and '
          f'std: {initial_price_std}, price change mean: {price_change_mean} and price change std: {price_change_std}, '
          f'using {model_dist.name} model with {model_dist.num_tasks} tasks and {model_dist.num_servers} servers')
    model_results = []
    pp = pprint.PrettyPrinter()
    filename = results_filename('dia_non_uniform_heuristic', model_dist, repeat_num)

    def algorithm_name(_servers):
        """
        Generates the algorithm name from the initial price and price change of a list of servers

        :param _servers: List of servers
        :return: String representing the algorithm name
        """
        return f'IP: [{" ".join([str(server.initial_price) for server in _servers])}], ' \
               f'PC: [{" ".join([str(server.price_change) for server in _servers])}]'

    for repeat in range(repeats):
        print(f'\nRepeat: {repeat}')
        tasks, servers = model_dist.generate()
        algorithm_results = {'model': {
            'tasks': [task.save() for task in tasks], 'servers': [server.save() for server in servers]
        }}
        pp.pprint(algorithm_results)

        dia_result = optimal_decentralised_iterative_auction(tasks, servers, time_limit=time_limit)
        algorithm_results[algorithm_name(servers)] = dia_result.store()
        dia_result.pretty_print()
        reset_model(tasks, servers)

        for _ in range(random_repeats):
            for server in servers:
                server.price_change = max(1, int(gauss(price_change_mean, price_change_std)))
                server.initial_price = max(1, int(gauss(initial_price_mean, initial_price_std)))

                dia_result = optimal_decentralised_iterative_auction(tasks, servers, time_limit=time_limit)
                algorithm_results[algorithm_name(servers)] = dia_result.store()
                dia_result.pretty_print()
                reset_model(tasks, servers)

        model_results.append(algorithm_results)

        # Save the results to the file
        with open(filename, 'w') as file:
            json.dump(model_results, file)
    print('Finished running')


if __name__ == "__main__":
    args = parse_args()

    if args.extra == '' or args.extra == 'heuristic grid search':
        dia_heuristic_grid_search(ModelDistribution(args.file, args.tasks, args.servers), args.repeat)
    elif args.extra == 'non uniform heuristics':
        non_uniform_server_heuristics(ModelDistribution(args.file, args.tasks, args.servers), args.repeat)
    else:
        raise Exception(f'Unknown extra argument: {args.extra}')
