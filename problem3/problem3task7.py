import pyomo.environ as pyo
from pyomo.opt import SolverFactory

import numpy as np
import matplotlib.pyplot as plt

from problem3setup import load

fixed_costs_tech = {
    'coal': 200,
    'gas': 500,
    'wind1': 800,
    'solar': 1000,
    'wind2': 800,
}

variable_costs_tech = {
    'coal': 65,
    'gas': 120,
    'wind1': 40,
    'wind2': 40,
    'solar': 35,
}

wind1_prod = [32, 51, 19, 25, 19, 4, 2, 1, 0, 0, 0, 0, 2, 4, 9, 1, 41, 32, 14, 14, 19, 32, 32, 41]
wind2_prod = [0, 1, 0, 4, 7, 13, 21, 25, 31, 32, 41, 40, 31, 20, 14, 21, 26, 29, 42, 43, 45, 41, 40, 29]
solar_prod = [0, 0, 0, 0, 2, 5, 8, 10, 12, 15, 18, 22, 25, 28, 30, 30, 30, 25, 20, 15, 10, 5, 0, 0]

min_load_tech = {
    'coal': 0,
    'gas': 0,
    'wind1': 0,
    'wind2': 0,
    'solar': 0,
}

max_load_tech = {
    'coal': [120] * 24,
    'gas': [30] * 24,
    'wind1': wind1_prod,
    'wind2': wind2_prod,
    'solar': solar_prod,
}

### Define model

model = pyo.ConcreteModel()

model.T = pyo.RangeSet(0, len(load) - 1)  # Time periods
model.tech = pyo.Set(initialize=fixed_costs_tech.keys())  # Technologies
model.tech_on = pyo.Var(model.T, model.tech, within=pyo.Binary)

### Bounds

def tech_load_bounds(model, time, tech):
    return (min_load_tech[tech], max_load_tech[tech][time])
model.tech_load = pyo.Var(model.T, model.tech, bounds=tech_load_bounds, initialize=0)

### Constraints

def load_rule(model, time, t):
    return sum([model.tech_load[time, tech] for tech in model.tech]) == load[time]
model.load_constraint = pyo.Constraint(model.T, model.tech, rule=load_rule)

def on_off_rule(model, time, tech):
    return model.tech_load[time, tech] <= max_load_tech[tech][time] * model.tech_on[time, tech]
model.on_off_constraint = pyo.Constraint(model.T, model.tech, rule=on_off_rule)

### Objective function

def objective_function(model):
    fixed_costs = sum(
        [sum([fixed_costs_tech[tech] * model.tech_on[time, tech] 
        for time in model.T])
        for tech in model.tech]
    )
    variable_costs = sum(
        [sum([variable_costs_tech[tech] * model.tech_load[time, tech] 
        for time in model.T])
        for tech in model.tech]
    )
    return fixed_costs + variable_costs

model.obj = pyo.Objective(rule=objective_function, sense=pyo.minimize)

### Solve the model
solver = SolverFactory('glpk')
results = solver.solve(model, tee=True)

print("\n")

model.display()

b = np.array([0.0 for i in model.T])
for bars,tech in [(np.array([model.tech_load[time, tech].value for time in model.T]), tech) for tech in model.tech]:
    plt.bar([i for i in range(24)], bars, bottom = b, label=str(tech).capitalize())
    b += bars
plt.xlabel('Time (hours)')
plt.ylabel('Load (MW)')
plt.title('Load distribution')
plt.xticks([i for i in range(0,24,6)])
plt.legend()
plt.grid()
plt.show()


width = 0.35
offset = 0.05


plt.bar([time - (width + offset)/2 for time in model.T], wind1_prod, width=width, color='tab:green', label='Wind 1 max production')
plt.bar([time + (width + offset)/2 for time in model.T], wind2_prod, width=width, color='tab:purple', label='Wind 2 max production')
plt.xlabel('Time (hours)')
plt.ylabel('Load (MW)')
plt.title('Maximal production of wind power plants')
plt.xticks([i for i in range(0, 24, 6)])
plt.grid()
plt.legend()
plt.show()