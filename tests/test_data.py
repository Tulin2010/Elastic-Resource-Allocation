"""
Tests that the results data is valid
"""

import json
import os


def test_data_repeats():
    print(f'\nFilename - repeats')
    for filename in os.listdir('../data'):
        if '.json' in filename:
            with open(f'../data/{filename}') as file:
                data = json.load(file)
                print(f'{filename} - {len(data)}')

                if 'resource_ratio' in filename:
                    social_welfare = [result['social welfare'] for ratio, ratio_results in data[0].items()
                                      for algo, result in ratio_results.items() if ratio != 'model']
                elif 'batch_online' in filename:
                    social_welfare = [result['social welfare'] for algo, result in data[0].items()
                                      if algo != 'model' and 'length' not in algo]
                else:
                    social_welfare = [result['social welfare'] for algo, result in data[0].items() if algo != 'model']

                if all(social_welfare[0] == sw for sw in social_welfare):
                    print(f'[-] Social welfare is bugged ({filename})')
