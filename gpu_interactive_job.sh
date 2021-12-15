#!/bin/bash
cd ~/proj/CS596-Proj
salloc --nodes=1 --ntasks=64 --cpus-per-task=1 --mem=0 --time=01:00:00 --partition=gpu --gres=gpu:a100:2 --account=anakano_429