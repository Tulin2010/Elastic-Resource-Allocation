#!/bin/bash
        
#SBATCH --time=60:00:00

#Change to the directory that the job was submitted from
cd ~/Elastic-Resource-Allocation/

# Load cplex
module load cplex/20.1.0
module unload python/3.6.4

# Load python 3.7
module load conda
source activate Elastic-Resource-Allocation

# Run the python script
echo $PWD
PYTHONPATH=~/Elastic-Resource-Allocation/src/
cmd="python -m evaluation.alibaba -m='alibaba' -t='20' -s='4' -r='0' -e='foreknowledge non-elastic'"
echo "Running $cmd"
eval "$cmd"