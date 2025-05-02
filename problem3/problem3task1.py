import pyomo.environ as pyo
from pyomo.opt import SolverFactory

import numpy as np
import matplotlib.pyplot as plt

from problem3setup import load, fixed_costs_tech, variable_costs_tech, min_load_tech, max_load_tech

### Define model

model = pyo.ConcreteModel()

model.T = pyo.RangeSet(0, len(load) - 1)  # Time periods
model.tech = pyo.Set(initialize=fixed_costs_tech.keys())  # Technologies
model.tech_on = pyo.Var(model.T, model.tech, within=pyo.Binary)

### Bounds

def tech_load_bounds(model, time, tech):
    return (min_load_tech[tech], max_load_tech[tech])
model.tech_load = pyo.Var(model.T, model.tech, bounds=tech_load_bounds, initialize=0)

### Constraints

def load_rule(model, time, t):
    return sum([model.tech_load[time, tech] for tech in model.tech]) == load[time]
model.load_constraint = pyo.Constraint(model.T, model.tech, rule=load_rule)

def on_off_rule(model, time, tech):
    return model.tech_load[time, tech] <= max_load_tech[tech] * model.tech_on[time, tech]
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
for bars in [np.array([model.tech_load[time, tech].value for time in model.T]) for tech in model.tech]:
    plt.bar([i for i in range(24)], bars, bottom = b)
    b += bars
plt.xlabel('Time (hours)')
plt.ylabel('Load (MW)')
plt.title('Load distribution')
plt.xticks([i for i in range(0,24,6)])
plt.legend(model.tech)
plt.grid()
plt.show()