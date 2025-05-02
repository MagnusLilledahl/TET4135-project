import numpy as np
import matplotlib.pyplot as plt


fixed_costs_tech = {
    'coal': 200,
    'gas': 500,
    'nuclear': 800,
    'biomass': 1000,
}

variable_costs_tech = {
    'coal': 60,
    'gas': 100,
    'nuclear': 120,
    'biomass': 150,
}

min_load_tech = {
    'coal': 0,
    'gas': 0,
    'nuclear': 0,
    'biomass': 0,
}

max_load_tech = {
    'coal': 120,
    'gas': 30,
    'nuclear': 50,
    'biomass': 30,
}

load = [30, 20, 20, 30, 50, 80, 100, 140, 120, 100, 90, 80, 70, 80, 120, 160, 220, 200, 180, 160, 120, 100, 80, 40]

def plot_load_demand(load):
    plt.figure(figsize=(10, 5))
    plt.plot([i for i in range(24)], load, label='Load')
    plt.xlabel('Time (hours)')
    plt.ylabel('Load (MW)')
    plt.title('Required Load over time')
    plt.grid()
    plt.show()

