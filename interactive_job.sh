#!/bin/bash
cd ~/proj/CS596-Proj
salloc --nodes=2 --ntasks=64 --cpus-per-task=1 --mem=0 --time=16:00:00 --partition=epyc-64 --account=anakano_429