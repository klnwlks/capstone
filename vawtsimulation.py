import matplotlib.pyplot as plt
import numpy as np
import csv

BETZ = 0.35
GENEFF = 0.85
CVTEFF = 0.85
IDEALTSR = 2 # small widnd turbines
# tsr = w*R / V

# simulate wind fluctuations
# this assumes a minute 
def createWind(wind, n):
  windList = []
  windList.append(
    wind +
    2 * np.pi * (2 * np.pi * 0 / 120) +
    1 * np.pi * (2 * np.pi * 0 / 30) +
    0.5 * np.random.randn(n)
  )

  return windList[0]

# we use a tsr based approach
# what we do is calculate tsr, make ideal gear ratio to match from tsr 
# then "tilt" the shift to know how much to shift for that
# also place a treshhold so we dont shift all the time
# calculate current gear ratio, return ideal and power output from electricity
def shifterDriver(power, rpm, speed, dimensions, config, wv, gr):
  # input radius of torroidal cvt discs
  # rinput = dimensions.input
  # routput = dimensions.output
  # torus shifter, it adjusts angle to change radius
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
    # print(f'>> SHIFTED TURBINE TO {gearRatio}, ROLLER ANGLED AT {np.ceil(theta)} DEGREE')

  # given this, i want to recalculate power at that moment
  # torque of turbine at that moment
  torque = power / speed

  # generator speed
  genspeed = speed / gearRatio
  gentorque = torque * gearRatio * GENEFF

  # this is what we want
  genpower = gentorque * genspeed

  return {
    'power': genpower, # electrical power generated,
    'ratio': gearRatio
  }

def simulate(windList, dimensions, config):
  # waahahh
  # hi
  # metrics to calculate
  # - power
  # - rpm at that moment
  # - torque 

  angularaccel = 0
  angularvelo = 0
  netpowarr = []
  epowerarr = []
  opowerarr = []
  ratioarr = []
  rpmarr = []
  kwharr = []
  srgpowarr = []

  kwh = 0
  opower = 0 
  ratio = (config['lowerbound'] + config['upperbound']) / 2
  for i in range(len(windList)):
    # power is power from wind - power from inertia
    if (windList[i] == 0):
      windList[i] = 0.1
    # inertia is defined by moment of inertia * angular accel * angular velocity
    omega = angularvelo # past angular velo
    rpm = (IDEALTSR * windList[i] * 60) / (2 * np.pi * dimensions['diam'] /2)
    # rpm = 100
    torque = 0.5 * config['density'] * (dimensions['diam'] * dimensions['hei']) * windList[i]**3 
    power = torque * BETZ
    # delta angular velo / delta time
    angularvelo = rpm / 60 * 2 * np.pi

    # DELTA V / DELTA S
    angularaccel = (angularvelo - omega) / 900 # 15 MINUTE CONFIGURATION
    powofinertia = config['inertia'] * angularaccel * angularvelo

    netpow = power - powofinertia
    epower = shifterDriver(netpow, rpm, angularvelo, dimensions, config, windList[i], ratio)

    netpowarr.append(netpow)
    epowerarr.append(epower['power'])
    ratioarr.append(epower['ratio'])
    rpmarr.append(epower['ratio'] * rpm)
    ratio = epower['ratio']
    opower = ( (epower['ratio'] * rpm) / (config['genv'])
                      *  epower['power'])
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
    'kwh': kwharr
  }
  visualize(windList, metrics)


def visualize(wind, metrics):
  # time series
  x = list(range(len(wind)))
  ax, fig = plt.subplots(4, 1)

  print('-- RESULTS ')
  print(f'MEAN POWER FROM TURBINE {np.mean(metrics['pow'])}')
  print(f'MEAN WINDSPEED: {np.mean(wind)}')
  print(f'MEAN ELECTRIC POWER: {np.mean(metrics['opow'])}')
  print(f'MEAN RPM: {np.mean(metrics['genrpm'])}')
  print(f'MEAN RATIO: {np.mean(metrics['ratio'])}')
  print(f'MEAN KWH GENERATION: {np.mean(metrics['kwh'])}')


  fig[0].plot(x, wind, label='TIME VS WIND')
  fig[0].legend()

  fig[1].plot(x, metrics['opow'], label='TIME VS POWER GENERATION')
  fig[1].legend()

  fig[2].plot(x, metrics['genrpm'], label='TIME VS RPM')
  fig[2].legend()

  fig[3].plot(x, metrics['ratio'], label='GEAR RATIO')
  fig[3].legend()

  plt.tight_layout()
  plt.show()

def main():
  # only if no provided wind data
  print('>> WINDSPEED ----------------')
  filename = input('FILENAME: ')
  print('READING FILE FOR DATA')

  data = [] # get file 
  # this is for nrel
  try:
    with open(filename, mode='r', newline='') as file:
      reader = csv.reader(file)
      for _ in range(2):
        next(reader)
      
      for row in reader:
        data.append(float(row[5]))
    
    print('READ FILE')

  except: 
    data = 0
    if (data is None or data == 0):
      print('FILE UNABLE TO BE READ, DEFAULTING.')
      w = int(input('WINDSPEED: '))
      d = int(input('NUMBER OF DATAPOINTS: '))
      data = createWind(w, d)

  print('>> DIMENSIONS ---------------')
  diameter = float(input('TURBINE DIAMETER: '))
  height = float(input('TURBINE HEIGHT: '))
  dimen = {
    'diam': diameter, 
    'hei': height,
  }

  print('>> CONFIG -------------------')
  den = float(input('AIR DENSITY: '))
  genspeed = int(input('GENERATOR RATED RPM: '))
  inertia = float(input('MOMENT OF INERTIA OF TURBINE: '))
  lower = float(input('LOWER GEAR RATIO: '))
  upper = float(input('UPPER GEAR RATIO: '))

  conf = {
    'density': den,
    'genv': genspeed,
    'lowerbound': lower,
    'upperbound': upper,
    'inertia': inertia,
  }
  simulate(data, dimen, conf)

if __name__ == '__main__':
  main()