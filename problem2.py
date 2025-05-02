
from math import sqrt
import numpy as np

# Energy_prices
c_peak = 325e-6 # NOK/W
c_off_peak = 210e-6

# Old demand
p_max_old = 3.25e6 #W
p_min_old = 1.25e6
t_on_peak = 6
t_off_peak = 18

# Grid parameters
U = 10e3 # V
L  = 8 # km

# Line types
class line:
  def __init__(self, area,  rho, I_max, cost):
    self.area = area
    self.rho = rho
    self.I_max = I_max
    self.cost = cost

linetypes  = {"FeAl25" : line(25, 18, 255, 0) }
linetypes["FeAl75"] = line(60,  18, 424, 750e3)
linetypes["FeAl90"] = line(90, 18, 485, 900e3)

# Utility functions
def annuity(r,n):
  return r / (1-(1+r)**(-n))

def max_power(U,I_max):
  return sqrt(3) * U * I_max

def resistance(rho, L, A):
  return rho*L/A

def loss(R,U,P):
  return R * P**2 / U**2

def loss_type(line, L, U, P):
  rho = line.rho
  A = line.area
  R = resistance(rho,L, A)
  return loss(R,U,P)

# --- Assignment 4 (Task 0) ---
print("\n ---Task 0---")

# - Problem 1 - 
print(" - Problem 1 -")

# New charging parameters
new_chargers = 52 
charger_load = 55e3  

new_load = new_chargers * charger_load

p_max_new = p_max_old + new_load
p_min_new = p_min_old

I_max = linetypes["FeAl25"].I_max
rho = linetypes["FeAl25"].rho
#A = linetypes["FeAl25"].area
#R = resistance(rho, L, A)
line_max = max_power(U, I_max)

print(f"The new power demand is {p_max_new:.3}")
print(f"The maximum capacity is {line_max:.3}")
if p_max_new > line_max:
  print(" -> The new power demand exceeds capacity")

# - Problem 2 -
print("\n - Problem 2 -")

# yearly cost due to loss
loss75 = 365*( loss_type(linetypes["FeAl75"], L, U, p_max_new)*6*c_peak
         + loss_type(linetypes["FeAl75"], L, U, p_min_new)*18*c_off_peak )

loss90 = 365*( loss_type(linetypes["FeAl90"], L, U, p_max_new)*6*c_peak
         + loss_type(linetypes["FeAl90"], L, U, p_min_new)*18*c_off_peak )

e = annuity(0.085, 20)

invcost75 = e* linetypes["FeAl75"].cost 
invcost90 = e* linetypes["FeAl90"].cost 

total_cost75 = invcost75+loss75
total_cost90 = invcost90+loss90
print(f"The total marginal cost for FeAl75 is {total_cost75:.3}")
print(f"The total marginal cost for FeAl90 is {total_cost90:.3}")
if total_cost75 > total_cost90:
  print("-> The FeAl90 line is the least costly option")
else:
  print("-> The FeAl75 line is the least costly option")

# - Problem 3 -
print("\n - Problem 3 -")

# Let investment cost be given by I = alpha * A + beta

# Calculate alpha
I1 = 750000
I2 = 900000
A1 = 60
A2 = 90

alpha = (I1-I2) / (A1-A2)
beta = I1 - alpha*A1

print("Assuming a liner cost function I = alpha*A + beta, the coefficients are")
print(f"alpha = {alpha:.3}")
print(f"beta = {beta:.3}")

# Task 1 (V2G)
print("\n --- Task 1 (V2G) ---")

print(" a)")
# Battery loss coefficients
etaC = 0.94
etaD = 0.92

# Charging and discharging times
tC = t_off_peak
tD = t_on_peak

def gamma(etaC, etaD, tC, tD):
  return 1/(etaC*etaD)*tD/tC

def v2g_average_power(p_max, p_min, g):
  delta_P_C =  (p_max-p_min)*g/(1+g)
  return p_min + delta_P_C

def battery_capacity(p_max, p_min, g, tC):
  delta_P_C =  (p_max-p_min)*g/(1+g)
  return delta_P_C*tC

g = gamma(etaC, etaD, tC, tD)
P = v2g_average_power(p_max_old, p_min_old, g)
E = battery_capacity(p_max_old, p_min_old, g, tC)

print(f"The average power is {P:.3}")
print(f"The battery capacity needed is {E:.4}")

print(" b)")

# loss V2G
type = linetypes["FeAl25"]
R = resistance(type.rho, L, type.area)

def v2g_loss_cost(linetype, etaC, etaD, tC, tD, c_peak, c_off_peak, U, L):
  g = gamma(etaC, etaD, tC, tD)
  P = v2g_average_power(p_max_old, p_min_old, g)
  R = resistance(linetype.rho, L, linetype.area)

  return 365 * loss(R, U, P) * (tD*c_peak + tC*c_off_peak)

v2glc = v2g_loss_cost(type, etaC, etaD, tC, tD, c_peak, c_off_peak, U, L)

print(f"The V2G loss cost is {v2glc:.3}")

# Function to discount payments
def fN(r,xc):
  y = [0,5,10,15]
  fN = 1
  for x in range(1,4):
    fN += annuity(r,y[x])*(1+xc)*x
  return fN

#print(fN(0.08, 0.25))

# Inital payement needed to break even
def inital_payment(alt_linecost, old_linetype, x_coeff, discount_rate, etaC, etaD, c_peak, c_off_peak, tC, tD, U, L, years):
  v2glc = v2g_loss_cost(old_linetype, etaC, etaD, tC, tD, c_peak, c_off_peak, U, L)
  return (alt_linecost - v2glc) * years / fN(discount_rate, x_coeff)

years = 20
discount_rate = 0.08
x_coeff = 0.25

P0 = inital_payment(invcost90+loss90, type, x_coeff, discount_rate, etaC, etaD, c_peak, c_off_peak, tC, tD, U, L, years)

print(f"The inital payment, P_0, must be {P0:.3} to break even")

# --- Task 3 ---
print("\n --- Task 3 (Sensitivty analysis) ---")
print(" -> results printed to file")

# x-coefficient dependence
x_coeff = np.linspace(-0.1, 0.4, 10)

P0 = np.zeros(len(x_coeff))
for i,xc in enumerate(x_coeff):
  P0[i] = inital_payment(invcost90+loss90, type, xc, discount_rate, etaC, etaD, c_peak, c_off_peak, tC, tD, U, L, years)
  
np.savetxt("P0-xcoeff.dat", np.c_[x_coeff, P0], fmt = "%.3f")

# disount rate dependence
x_coeff = 0.25
discount_rate = np.linspace(0.03, 0.12, 100)

P0 = np.zeros(len(discount_rate))
for i,dr in enumerate(discount_rate):
  P0[i] = inital_payment(invcost90+loss90, type, x_coeff, dr, etaC, etaD, c_peak, c_off_peak, tC, tD, U, L, years)
  
np.savetxt("P0-discount.dat", np.c_[discount_rate, P0], fmt = "%.3f")

# Battery loss dependence
discount_rate = 0.08
f = np.linspace(0.8, 1.2, 100) # Factor changing battery loss
P0 = np.zeros(len(f))
for i,dr in enumerate(f):
  P0[i] = inital_payment(invcost90+loss90, type, x_coeff, discount_rate, f[i]*etaC, f[i]*etaD, c_peak, c_off_peak, tC, tD, U, L, years)

np.savetxt("P0-charging.dat", np.c_[f, P0], fmt = "%.3f")

# Energy price dependence
c_peak_range = np.linspace(0.5, 1.5, 10)*c_peak
P0 = np.zeros(len(c_peak_range))
for i,cp in enumerate(c_peak_range):
  P0[i] = inital_payment(invcost90+loss90, type, x_coeff, discount_rate, etaC, etaD, cp, c_off_peak, tC, tD, U, L, years)

np.savetxt("P0-peak.dat", np.c_[c_peak_range*1e6, P0], fmt = "%.3f")

# To meet Taxi company demand of 3 MONK
x_coeff = 0.1
discount_rate = 0.03
f = 1.2
cp = 0.55*c_peak
P0 = inital_payment(invcost90+loss90, type, x_coeff, discount_rate, f*etaC, f*etaD, cp, c_off_peak, tC, tD, U, L, years)
print(P0)