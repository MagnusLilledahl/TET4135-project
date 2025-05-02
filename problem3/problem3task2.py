import pyomo.environ as pyo
from pyomo.opt import SolverFactory

import numpy as np
import matplotlib.pyplot as plt

from problem3setup import load, fixed_costs_tech, variable_costs_tech, min_load_tech, max_load_tech

max_batery_load = 100  # MWh
max_battery_discharge = 25  # grid side
max_battery_charge = 25  # grid side
battery_efficiency = 0.95  # Efficiency of the battery

### Define model

model = pyo.ConcreteModel()

model.T = pyo.RangeSet(0, len(load) - 1)  # Time periods
model.tech = pyo.Set(initialize=fixed_costs_tech.keys())  # Technologies
model.tech_on = pyo.Var(model.T, model.tech, within=pyo.Binary)

### Bounds

def tech_load_bounds(model, time, tech):
    return (min_load_tech[tech], max_load_tech[tech])
model.tech_load = pyo.Var(model.T, model.tech, bounds=tech_load_bounds, initialize=0)

def battery_load_bounds(model, time):
    return (0, max_batery_load)
model.battery_load = pyo.Var(model.T, bounds=battery_load_bounds, initialize=0)

def battery_charge_bounds(model, time):
    return (0, max_battery_charge)
model.battery_charge = pyo.Var(model.T, bounds=battery_charge_bounds, initialize=0)

def battery_discharge_bounds(model, time):
    return (0, max_battery_discharge)
model.battery_discharge = pyo.Var(model.T, bounds=battery_discharge_bounds, initialize=0)

### Constraints

def load_rule(model, time, t):
    return (sum(
        [model.tech_load[time, tech] for tech in model.tech])
        + model.battery_discharge[time]
        - model.battery_charge[time]
        == load[time])
model.load_constraint = pyo.Constraint(model.T, model.tech, rule=load_rule)

def on_off_rule(model, time, tech):
    return model.tech_load[time, tech] <= max_load_tech[tech] * model.tech_on[time, tech]
model.on_off_constraint = pyo.Constraint(model.T, model.tech, rule=on_off_rule)

def battery_load_rule(model, time):
    return (model.battery_load[time]
            == model.battery_load[(time - 1) % 24]
            + battery_efficiency * model.battery_charge[(time - 1) % 24]
            - 1/battery_efficiency * model.battery_discharge[(time - 1) % 24]
    )
model.battery_load_rule = pyo.Constraint(model.T, rule=battery_load_rule)

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

### Plotting results

fig, ax1 = plt.subplots()

width = 0.25
offset = 0.05

ax1.set_xlabel('Time (hours)')
ax1.set_ylabel('Load (MW)')
b = np.array([0.0 for i in model.T])
for bars, tech in [(np.array([(model.tech_load[time, tech].value) for time in model.T]), tech) for tech in model.tech]:
    ax1.bar([i for i in range(24)], bars, bottom = b, width=width, label=str(tech).capitalize())
    b += bars
ax1.tick_params(axis='y')
ax1.title.set_text('Production by technology and Battery Discharge/Charge')
ax1.bar(
    [time + width + offset for time in model.T],
    [-model.battery_charge[time].value + model.battery_discharge[time].value for time in model.T],
    bottom=b,
    width=width,
    label='Battery Charge/Discharge'
)
for time in model.T:
    ax1.plot([time - width*0.5, time + width * 1.5 + offset], [b[time]]*2, color='grey', linewidth=1, linestyle='--')
    ax1.plot([time + width*0.5 + offset, time + width*2.5 + offset*2], [load[time]]*2, color='grey', linewidth=1, linestyle='--')
ax1.bar(
    [time + width*2 + offset*2 for time in model.T],
    [load[time] for time in model.T],
    width=width,
    label='Delivered load'
)
ax1.legend(loc='upper left')
ax1.set_xticks([i for i in range(24)])
ax1.set_xticklabels([str(i) if i % 2 == 0 else '' for i in range(24)])

ax2 = ax1.twinx()

color = (0,0,0)
ax2.plot([time for time in model.T], [model.battery_load[time].value for time in model.T], color=color, label='Battery Load')
ax2.plot([time for time in model.T], [100 for time in model.T], color='red', linestyle='--', label='Max Battery Capacity')
ax2.set_ylim(ax1.get_ylim())
ax2.set_yticks([])
ax2.legend()

fig.tight_layout()
plt.show()