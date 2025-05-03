import pyomo.environ as pyo
from pyomo.opt import SolverFactory

import numpy as np
import matplotlib.pyplot as plt

from problem3setup import load, fixed_costs_tech, variable_costs_tech, min_load_tech, max_load_tech

emission_by_tech = {
    'coal': 1.5,
    'gas': 0.2,
    'nuclear': 0,
    'biomass': 0,
}
emission_price = 60

### Define model

model = pyo.ConcreteModel()

model.T = pyo.RangeSet(0, len(load) - 1)  # Time periods
model.tech = pyo.Set(initialize=fixed_costs_tech.keys())  # Set of Technologies
model.tech_on = pyo.Var(model.T, model.tech, within=pyo.Binary) # Binary variable to describe whether variable is on or off
model.emission = pyo.Var(model.T, within=pyo.NonNegativeReals) # CO2 emissions per hour

### Bounds

def tech_load_bounds(model, time, tech):  # bounds for production per technology
    return (min_load_tech[tech], max_load_tech[tech])
model.tech_load = pyo.Var(model.T, model.tech, bounds=tech_load_bounds, initialize=0)

### Constraints

def load_rule(model, time, t): # Set load sum to required load
    return sum([model.tech_load[time, tech] for tech in model.tech]) == load[time]
model.load_constraint = pyo.Constraint(model.T, model.tech, rule=load_rule)

def on_off_rule(model, time, tech): # Set binary variable
    return model.tech_load[time, tech] <= max_load_tech[tech] * model.tech_on[time, tech]
model.on_off_constraint = pyo.Constraint(model.T, model.tech, rule=on_off_rule)

def emission_rule(mode, time): # Constraint to set total emissions
    return sum(
        [emission_by_tech[tech]*model.tech_load[time,tech] for tech in model.tech]
    ) == model.emission[time]
model.emission_constraint = pyo.Constraint(model.T, rule=emission_rule)

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
    emission_cost = sum(
        [model.emission[time]*emission_price for time in model.T]
    )
    return fixed_costs + variable_costs + emission_cost

model.obj = pyo.Objective(rule=objective_function, sense=pyo.minimize)

### Solve the model
solver = SolverFactory('glpk')
results = solver.solve(model, tee=True)

### Display results

print("\n")

model.display()

b = np.array([0.0 for i in model.T])
for bars in [np.array([model.tech_load[time, tech].value for time in model.T]) for tech in model.tech]:
    plt.bar([i for i in range(24)], bars, bottom = b)
    b += bars

plt.xlabel('Time (hours)')
plt.ylabel('Load (MW)')
plt.title('Load distribution w/ emission costs')
plt.xticks([i for i in range(0,24,6)])
plt.legend(model.tech)
plt.grid()
plt.show()

plt.bar([i for i in model.T], [model.emission[time].value for time in model.T])
plt.xlabel('Time (hours)')
plt.ylabel('CO2 (Tons)')
plt.title('CO2 Emissions')
plt.xticks([i for i in range(0,24,6)])
plt.grid()
plt.show()

### Sensitivity analysis

emission_prices = [i for i in range(10, 131, 20)]

objective_costs_sa = []
emissions_sa = []
for price in emission_prices:
    emission_price = price
    model.obj = pyo.Objective(rule=objective_function, sense=pyo.minimize)
    results = solver.solve(model, tee=True)

    objective_costs_sa.append(model.obj())
    emissions_sa.append(sum([model.emission[time].value for time in model.T]))

width = 4
offset = 2

fig, ax1 = plt.subplots()
ax1.bar([time - width/2 - offset/2 for time in emission_prices], objective_costs_sa, width=width, color='blue', label='Total cost')

ax2 = ax1.twinx()

ax2.bar([time + offset/2 + width/2 for time in emission_prices], emissions_sa, color='red', width=width, label='Total emissions')
ax1.set_ylabel('Cost (EUR)', color='blue')
ax2.set_ylabel('Total emissions (tons)', color='red')
ax1.tick_params(axis='y', labelcolor='blue')
ax2.tick_params(axis='y', labelcolor='red')

plt.xlabel('Emission price (EUR/ton)')
plt.title('Sensitivity Analysis of Emission Price')
plt.xticks(emission_prices)
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
fig.tight_layout()
plt.show()

print("CO2 emissions", sum([model.emission[time].value for time in model.T]))