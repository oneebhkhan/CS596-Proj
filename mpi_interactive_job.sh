#!/bin/bash
cd ~/proj/CS596-Proj
salloc --nodes=13 --ntasks=13 --cpus-per-task=64 --mem=0 --time=1:00:00 --partition=epyc-64 --account=anakano_429