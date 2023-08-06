#!/bin/bash

set -e

ENV_PATH=$1
PROJECT_PATH=$2

module load miniconda/3
conda activate $ENV_PATH
mkdir -p ~/.milatools/sockets
jupyter notebook --sock ~/.milatools/sockets/$(hostname).sock $PROJECT_PATH
