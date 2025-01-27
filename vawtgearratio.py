import math

GENERATOREFF = 0.85 # find source for this number
GENERATORRATEDSPEED = 1500 # IDEAL RPM
TSR = 4
BETZ = 0.35
DENSITY = 1.225 # METER
TRADIUS = 1.64 # METER
HEIGHT = 5.17 # METER

def gearratio(WINDSPEED):
  print(f"DIAGNOSTICS AT AVERAGE WINDSPEED {WINDSPEED}M/S")
  LOWEST = WINDSPEED - 2
  HIGHEST = WINDSPEED + 20 # arbitrary values but for goodness sake

  print('------------------------------------------')
  print(f"LOWEST WIND SPEED: {LOWEST} \nHIGHEST: {HIGHEST}")

  # conv to rads 
  RPMRAD = (GENERATORRATEDSPEED * 2 * math.pi) / 60
  LOWESTROTATIONALSPEED = (TSR * LOWEST) / TRADIUS
  HIGHESTROTATIONALSPEED = (TSR * HIGHEST) / TRADIUS
  RATEDROTATIONALSPEED = (TSR * WINDSPEED) / TRADIUS

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
  



wind = int(input("AVERAGE WINDSPEED OF AREA: "))
gearratio(wind)
