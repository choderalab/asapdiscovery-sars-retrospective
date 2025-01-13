#!/bin/bash

source ~/.bashrc
conda activate asapdiscovery

echo Start
# network device info
ifconfig
# dask info
dask info versions
ulimit -c 0


python test_import_speed.py

echo Done
date