#!/bin/bash

git clone https://github.com/WeWyse/marketing_mix_model_product

cd marketing_mix_model_product/
mkdir venv
mkdir MODEL_SAVINGS
mkdir OUTPUT_DF
mkdir BUSINESS_OUTPUT/RESPONSE_CURVE_PLOTS/
sudo apt-get install python3.10
sudo apt-get update
sudo apt install python3-pip
sudo apt install python3.10-venv
python3 -m venv venv
source venv/bin/activate
pip install pandas
pip install numpy
pip install datetime
pip install pyyaml
pip install matplotlib
pip install seaborn
pip install sklearn
pip install openpyxl
pip install scikit-learn
gcc --version
python3 -m pip install pystan
