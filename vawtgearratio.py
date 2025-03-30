import math
import csv
import numpy as np

GENERATOREFF = 0.85 # find source for this number
GENERATORRATEDSPEED = 1600 # IDEAL RPM
TSR = 2
BETZ = 0.35
DENSITY = 1 

def gearratio(WINDSPEED, LOWEST, HIGHEST, DIAM, HEIGHT):
  print(f"DIAGNOSTICS AT AVERAGE WINDSPEED {WINDSPEED}M/S")
  TRADIUS = DIAM / 2

  print('------------------------------------------')
  print(f"LOWEST WIND SPEED: {LOWEST} \nHIGHEST: {HIGHEST}")

  # conv to rads 
  RPMRAD = (GENERATORRATEDSPEED * 2 * math.pi) / 60
  LOWESTROTATIONALSPEED = (TSR * LOWEST) / TRADIUS
  HIGHESTROTATIONALSPEED = (TSR * HIGHEST) / TRADIUS
  RATEDROTATIONALSPEED = (TSR * WINDSPEED) / TRADIUS
  print(RATEDROTATIONALSPEED)

  # wind turbine torque is mechanical power / rotational speed of turbine
  MECHPOWER = 0.5 * DENSITY * (2 * TRADIUS * HEIGHT) * WINDSPEED**3 * BETZ
  TORQUE = MECHPOWER / RATEDROTATIONALSPEED

  # formula for gear ratio = GENSPEE / ROTATIONAL SPEED OF TURBINE
  HIGHESTGR = RPMRAD / HIGHESTROTATIONALSPEED
  LOWESTGR = RPMRAD / LOWESTROTATIONALSPEED
  AVERAGEGR = RPMRAD / RATEDROTATIONALSPEED
  print('------------------------------------------')
  print(f"UPPER BOUND: {HIGHESTGR} \nLOWEST: {LOWESTGR} \nAVERAGE: {AVERAGEGR}")

  print('------------------------------------------')
  print(f"TURBINE TORQUE: {TORQUE}")

  GPOWER = MECHPOWER * GENERATOREFF 
  print('------------------------------------------')
  print(f"MECHANICAL POWER FROM TURBINE: {MECHPOWER}W \nELECTRIC POWER FROM GENERATOR: {GPOWER}W")
  


filename = input('FILENAME: ')
print('READING FILE FOR DATA')

data = [] # get file 
wind = 0
high = low = 0
# this is for nrel
try:
  with open(filename, mode='r', newline='') as file:
    reader = csv.reader(file)
    for _ in range(2):
      next(reader)
    
    for row in reader:
      data.append(float(row[5]))

    high = max(data)
    low = np.percentile(data, 5)
    wind = (low + high) / 2
    wind = sum(data) / len(data)
    # cut in
    if low < 2:
      low = 2
  
  print('READ FILE')

except: 
  data = 0
  if (data is None or data == 0):
    print('FILE UNABLE TO BE READ, DEFAULTING.')
    wind  = int(input('WINDSPEED: '))
    low = int(input('WINDSPEED: '))
    high = int(input('WINDSPEED: '))

DIAM = float(input('DIAMETER: '))
HEIGHT = float(input('HEIGHT: '))
GENSPEED = int(input('GENSPEED: '))
gearratio(wind, low, high, DIAM, HEIGHT)
