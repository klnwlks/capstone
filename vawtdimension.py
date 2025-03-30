import matplotlib
import math

DENSITY = 1
BETZ = 0.35 # rough average of vawt limit
TSR = 2 # small vawt scale for darries
SOLIDITY = 0.2 # optimal for small vawts with small windspeeds
RATIO = 1.75 # see sources
BLADERATIO = 7 # see sources, blade len / diameter
NBLADES = 3
# given that a small scale vawt will want to average
# at 100 rpm, and given our tsr, well assume diameter of 2m

# use equation 0.5 * density * swept area (diameter * height)

# avg wind speed, desired power output
def w2area(wind, power):
  print('AT WIND SPEED: ' + str(wind) + 'M/S')
  area = (2*power / (wind**3 * BETZ * DENSITY))
  diameter = math.sqrt(area / (RATIO))
  height = diameter * RATIO

  # given power
  # mechanical power btw
  power = 0.5 * DENSITY * BETZ * wind**3 * (diameter * height)

  # chord length
  cho = (3 * SOLIDITY / diameter)
  # chord thickness = cholen * 0.15
  chothick = cho * 0.15

  print('AREA: ' + str(area))
  print('POWER: ' + str(power))
  print('DIAMETER: ' + str(diameter))
  print('HEIGHT: ' + str(height))
  print('CHORD LEN:' + str(cho))
  print('CHORD THICKNESS:' + str(chothick))

w = float(input('WIND SPEED: '))
p = int(input('DESIRED POWER: '))
w2area(w, p)