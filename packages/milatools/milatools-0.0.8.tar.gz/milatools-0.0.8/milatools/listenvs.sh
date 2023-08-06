#!/bin/bash

set -e

{
    module load miniconda/3
} &> /dev/null

{
    ls "$1/.milatools-env" "$1/.envrc" | awk '{print "ENVFILE:" $0}'
} 2> /dev/null

conda env list --json | jq -r '.envs[]' | awk '{print "CONDA:" $0}'
