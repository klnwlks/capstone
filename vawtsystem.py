import matplotlib.pyplot as plt
import numpy as np
import csv
import math

BETZ = 0.35
GENEFF = 0.85
CVTEFF = 0.98
TSR = 2 # small widnd turbines
RATIO = 1.75 # see sources

def w2area(wind, power, DENSITY):
  print('AT WIND SPEED: ' + str(wind) + 'M/S')
  area = (2*power / (wind**3 * BETZ * DENSITY))
  diameter = math.sqrt(area / (RATIO))
  height = diameter * RATIO

  # given power
  # mechanical power btw
  power = 0.5 * DENSITY * BETZ * wind**3 * (diameter * height)


  print('AREA: ' + str(area))
  print('DIAMETER: ' + str(diameter))
  print('HEIGHT: ' + str(height))
  return diameter, height

def gearratio(WINDSPEED, LOWEST, HIGHEST, DIAM, GENERATORRATEDSPEED):
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

  # formula for gear ratio = GENSPEE / ROTATIONAL SPEED OF TURBINE
  HIGHESTGR = RPMRAD / HIGHESTROTATIONALSPEED
  LOWESTGR = RPMRAD / LOWESTROTATIONALSPEED
  AVERAGEGR = RPMRAD / RATEDROTATIONALSPEED
  print('------------------------------------------')
  print(f"UPPER BOUND: {HIGHESTGR} \nLOWEST: {LOWESTGR} \nAVERAGE: {AVERAGEGR}")
  
  return HIGHESTGR, LOWESTGR, AVERAGEGR
  
def shifterDriver(power, rpm, speed, dimensions, config, wv, gr):
  theta = 0

  # upper and lower gear ratios, given from vawtgearratio
  lower = config['lowerbound']
  upper = config['upperbound']
  gearRatio = (lower + upper) / 2

  # ideal rpm
  ideal = config['genv']
  rotationalspeed = rpm * 2 * np.pi /60
  # currenttsr = rotationalspeed * (dimensions['diam'] / 2 ) / wv
  try:
    gearRatio = gr
  except:
    gearRatio = (lower + upper) / 2
  
  # calculates ideal gear ratio to upkeep ideal tsr of 2
  # idealgr = gearRatio * IDEALTSR / currenttsr

  # calculates for optimum rpm
  idealgr = np.ceil(gearRatio * ideal / (rpm * gearRatio))
  # if difference between the two gear ratios are greater than 1, shift 
  # ensures that it doesnt shift all the time and yadda yadda
  if (abs(idealgr - gearRatio) > 1):
    # shift the gear
    # insert magic formula that determines theta by difference of the two gear ratios
    theta = 0

    # linear map
    def mapfunc(x, xmin, xmax):
      if xmax == xmin:
        return 45
      if x > xmax:
        return 90
      return 90 * ((x - xmin) / (xmax - xmin))

    # make sure it doesnt go beyond radius or the gear ratio bounds
    # get theta based on a linearly mapped values between lower and upper
    # for example, 45deg is the median value
    theta = mapfunc(gearRatio, upper, lower)

    # translate theta change back to gear ratio
    # i mean, if a radius value maps to a theta value, cant we just linmap it again?
    # of course, theres also the option of just returning the idgr

    if idealgr > lower:
      gearRatio = lower
    elif idealgr < upper:
      gearRatio = upper
    else: 
      gearRatio = idealgr

  # print(f'SHIFTED TO {gearRatio}, expected rpm {gearRatio * rpm}, ideal {idealgr} expected ideal {idealgr * rpm}')

  torque = power / speed

  genspeed = speed / gearRatio
  gentorque = torque * gearRatio * GENEFF

  # this is what we want
  genpower = gentorque * genspeed

  return {
    'power': genpower, # electrical power generated,
    'rpm': rpm * gearRatio,
    'ratio': gearRatio
  }

def simulate(windList, dimensions, config):
  # waahahh
  # hi
  # metrics to calculate
  # - power
  # - rpm at that moment
  # - torque 

  angularvelo = 0
  netpowarr = []
  epowerarr = []
  opowerarr = []
  ratioarr = []
  rpmarr = []
  kwharr = []
  effarr = []

  kwh = 0
  opower = 0 
  ratio = (config['lowerbound'] + config['upperbound']) / 2
  for i in range(len(windList)):
    # power is power from wind - power from inertia
    if (windList[i] == 0):
      windList[i] = 0.1
    rpm = (TSR * windList[i] * 60) / (2 * np.pi * dimensions['diam'] /2)
    # rpm = 100
    torque = 0.5 * config['density'] * (dimensions['diam'] * dimensions['hei']) * windList[i]**3 
    power = torque * BETZ

    if (power > POWER * 5):
      power = POWER
    # delta angular velo / delta time
    angularvelo = rpm / 60 * 2 * np.pi

    epower = shifterDriver(power , rpm, angularvelo, dimensions, config, windList[i], ratio)

    netpowarr.append(power)
    epowerarr.append(epower['power'])
    ratioarr.append(epower['ratio'])
    rpmarr.append(epower['rpm'])
    ratio = epower['ratio']
    eff = epower['rpm'] / config['genv']
    if (eff > 1): 
      eff = config['genv'] / epower['rpm']
    effarr.append(eff)
    opower = eff * epower['power']
    opowerarr.append(opower)
    kwh += (opower * 0.25) / 1000 # nrel specific

    if i % 4 == 0: # also nrel specif
      kwharr.append(kwh)
      kwh = 0

  metrics = {
    'pow': netpowarr,
    'opow': opowerarr,
    'ratio': ratioarr,
    'genrpm': rpmarr,
    'kwh': kwharr,
    'eff': effarr
  }

  verification = {
    'pow': netpowarr[0],
    'opow': opowerarr[0],
    'ratio': ratioarr[0],
    'genrpm': rpmarr[0],
    'kwh': kwharr[0],
    'eff': effarr[0]
  }

  print(verification)
  visualize(windList, metrics)

def visualize(wind, metrics):
  # time series
  x = list(range(len(wind)))
  ax, fig = plt.subplots(4, 1)

  print('-- RESULTS ')
  print(f'MEAN WINDSPEED: {np.mean(wind)}')
 

  print(f'MEAN POWER FROM TURBINE {np.mean(metrics['pow'])}')
  print(f'MEAN ELECTRIC POWER: {np.mean(metrics['opow'])}')
  print(f'MEAN RPM: {np.mean(metrics['genrpm'])}')
  print(f'MEAN RATIO: {np.mean(metrics['ratio'])}')
  print(f'MEAN KWH GENERATION: {np.mean(metrics['kwh'])}')
  print(f'MEAN EFFICIENCY: {np.mean(metrics['eff'])}')


  fig[0].plot(x, wind, label='TIME VS WIND')
  fig[0].set(xlabel= 'DATAPOINTS')
  fig[0].set(ylabel='WIND VELOCITY IN m/s')
  fig[0].legend()

  fig[1].plot(x, metrics['opow'], label='TIME VS POWER GENERATION')
  fig[1].set(xlabel='DATAPOINTS')
  fig[1].set(ylabel='WATTS')
  fig[1].legend()

  fig[2].plot(x, metrics['genrpm'], label='TIME VS RPM')
  fig[2].set(xlabel='DATAPOINTS')
  fig[2].set(ylabel='RPM')
  fig[2].legend()

  fig[3].plot(x, metrics['ratio'], label='GEAR RATIO')
  fig[3].set(xlabel='DATAPOINTS')
  fig[3].set(ylabel='GEAR RATIO')
  fig[3].legend()

  plt.tight_layout()
  plt.show()



filename = input('FILENAME: ')
print('READING FILE FOR DATA')

data = [] # get file 
wind = 0
high = low = 0
# this is for nrel
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

print(f'standard dev: {np.std(data)}')
print(f'variance: {np.var(data)}')
 
DENSITY = float(input('WIND DENSITY: '))
POWER = float(input('DESIRED POWER: '))
GENV = int(input('GENERATOR SPEED: '))
diam, hei = w2area(wind, POWER, DENSITY)

upper, lower, ave = gearratio(wind, low, high, diam, GENV)

dimen = {
  'diam': diam, 
  'hei': hei,
}

conf = {
  'density': DENSITY,
  'genv': GENV,
  'lowerbound': lower,
  'upperbound': upper,
}

simulate(data, dimen, conf)

print('SRG RESULTS ----------------------')

conf['lowerbound'] = ave
conf['upperbound'] = ave
simulate(data, dimen, conf)