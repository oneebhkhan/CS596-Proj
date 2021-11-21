#!/bin/bash
module purge
module load llvm/9.0.1
module load libpng/1.6.37
module load cmake/3.15.4
module load libjpeg-turbo/2.0.6
module load zlib/1.2.11
cd ~/proj/CS596-Proj
source ../mitsuba2/setpath.sh
conda activate mitsu