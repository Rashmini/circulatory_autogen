import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import pandas as pd
from protocol_funcs import run_protocols

file_path = "/home/rnar144/Documents/implementation/circulatory_autogen/generated_models/glucose_dynamics_glucose_dynamics_obs_data/glucose_dynamics.cellml"

variable_list = ['glucose_system/G','glucose_system/I','glucose_system/Q','glucose_system/I_original','glucose_system/Q_original']

t, y = run_protocols(file_path, variable_list)

y_G = y[0][0]
#y_I = y[0][1]*1000000000/6
#y_Q = y[0][2]*1000000000/6
y_I = y[0][3]
y_Q = y[0][4]

data = {
    't': t[0],
    'G': y_G,
    'I': y_I,
    'Q': y_Q
}

df = pd.DataFrame(data)

# Write model data to CSV
csv_file_name = '/home/rnar144/Documents/implementation/circulatory_autogen/simulation_results/glucose_dynamics_param_id/output_cellml.csv'
df.to_csv(csv_file_name, index=False)

# Get experimental data
filename = '/home/rnar144/Downloads/alex_model/Insulin-Modelling/Data/OGTTLui/OGTTLuiMaster.csv'

row_index = 7

data = pd.read_csv(filename, header=1)

tp_columns = ['TP1', 'TP2', 'TP3', 'TP4', 'TP5', 'TP6', 'TP7', 'TP8']
i_columns = ['I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8']
g_columns = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8']

tp_values = data.loc[row_index, tp_columns].to_numpy()*60
i_values = data.loc[row_index, i_columns].to_numpy()/6
g_values = data.loc[row_index, g_columns].to_numpy()

# Create subplots
# fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

plt.figure(figsize=(8, 4))
plt.plot(t[0], y_G, label='G_m')
plt.plot(tp_values, g_values, marker='^', label='G_e')
plt.ylabel('G [mmol_per_l]')
plt.legend()
plt.grid(True)

# Plot G data
# axs[0].plot(t[0], y_G, label='G_m')
# axs[0].plot(tp_values, g_values, marker='^', label='G_e')
# axs[0].set_ylabel('G [mmol_per_l]')
# axs[0].legend()
# axs[0].grid(True)

# Plot I data
# axs[1].plot(t[0], y_I, label='I_m')
# axs[1].plot(tp_values, i_values, marker='s', label='I_e')
# axs[1].set_xlabel('Time (s)')
# axs[1].set_ylabel('I [mU_per_l]')
# axs[1].legend()
# axs[1].grid(True)

# Adjust layout
plt.tight_layout()

plt.savefig("/home/rnar144/Documents/implementation/circulatory_autogen/simulation_results/glucose_dynamics_param_id/plot_param_id.png")
plt.clf()
