# You might need to pip install kagglehub if you get a kagglehub module can't be found error.
import kagglehub
import os
import re
import json

# Download latest version
path = kagglehub.dataset_download("rashikrahmanpritom/plant-disease-recognition-dataset")

print("Path to dataset files:", path)


def recursive(path, dirName):
  if os.path.isfile(f'{path}/{os.listdir(path)[0]}'):
    dirs.append(dirName)
    return
  for d in os.listdir(path):
    recursive(f'{path}/{d}', d)

dirs = []

for d in os.listdir(path):
    recursive(f'{path}/{d}', d)

#print(dirs)

plant_name_plant_disease_pairs = {}
for pair in dirs:
  plant_name_plant_disease_pairs[pair] = re.split(r'[^a-zA-Z0-9]+', pair)

# The output json file should be in the same directory/folder as the one which you're running this python file in.
with open('plant_name_plant_disease.json', 'w') as out:
  json.dump(plant_name_plant_disease_pairs, out)
