import pandas as pd
import os

master = pd.DataFrame([['d',2],['g',4],['v',6]])

print(master)
new = pd.DataFrame([['h',3]])
master = pd.concat([master, new],axis = 0)
print('')
print(master)