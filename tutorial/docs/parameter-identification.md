# Parameter Identification

The parameter identification part of Circulatory_Autogen is designed to allow calibration of a model to experimental or clinical data. It implements an optimisation method to find the best fit parameters that give a minimal (local minima) error difference between the model output and the ground truth observables (experimental or clinical data or user specified). The creation of below two configuration files is necessary: 

- **params_for_id**
- **param id observables**

Those files should be added to the `[project_dir]/resources` directory. Proper names of the files are **[file_prefix]_params_for_id.csv** and **[file_prefix]_obs_data.json**, respectively.

## Creating params_for_id file

This file defines which parameters (constants and initial_states) within your model that you will vary in the parameter id process and their allowed ranges (prior distribution). Following is an example of the `params_for_id.csv` file.

![params_for_id.csv](images/params-for-id.png)

The entries in the file are detailed as follows:

- **vessel_name**: the name of the vessel/module the parameter is in
- **param_name**: the name of the parameter in the cellml module (not including the "vessel_name" suffix that is included in the `[file_prefix]_parameters.csv` file).
- **param_type**: **"state"** or **"const"**; whether the parameter is the initial value of a state or a const. 
- **min**: The minimimum of the range of possible values (min of the uniform distribution).
- **max**: The maximum of the range of possible values (max of the uniform distribution).
- **name_for_plotting**: The name (latex format) that will be used when automatically potting comparisons with observables and predictions.

!!! Note
    **param_type** will be deprecated. All should be **"const"**. Initial values that need to identified should be defined as constants within the cellml module.

!!! info
    In the future we plan on including other types of priors rather than just uniform.

## Creating param id observables file

This file defines the ground truth observables that will be used in the cost function for the parameter id optimisation algorithm. It also defines the measurement standard deviation, and weighting for each observable.

File path of the obs_data.json file should be defined as **param_id_obs_path** in `[project_dir]/user_run_files/user_inputs.yaml`.

Examples of `obs_data.json` file are shown in below figures for constant, series, and frequency data types, respectively. 

![obs_data.json for constant](images/obs-data-constant.png)
![obs_data.json for  series](images/obs-data-series.png)
![obs_data.json for frequency](images/obs-data-frequency.png)

The entries in the `obs_data.json` file are:

- **variable**: `[vessel_name]/[variable_name]`, where variable name is the variable name in the cellml module and `module_config.json` file.
- **data_type**: The format of the data. This can be *"constant"*, *"series"*, or *"frequency"* as shown above.
- **unit**: The unit which should be the same as the unit in the variable in the model.
- **name_for_plotting**: The name that will be in the automated plots comparing observable data to model output. (latex format)
- **weight**: The weighting to put on this observables entry in the cost function. Default should be 1.0
- **std**: The standard deviation which is used in the cost function. The cost function is the relative absolute error (AE) or mean squared error (MRE), each normalised by the std.
- **obs_type**: The operation that will be done on the model output series before it being applied to calculate the cost function, (min, max, mean, etc). 
- **value**: The value of the ground truth, either a scalar for constant data_type, or a list of values for series or frequency data_types.
- **sample_rate**: not needed or set to "null" for constant and frequency data_types. It defines the sample rate of the observable series values.
- **operation**: This will make *obs_type* obsolete. This defines the operation that will be done on the operands/variable. The possible operations to be done on model outputs are defined in `[project_dir]/src/param_id/operation_funcs.py` and in `[project_dir]/operation_funcs_user/operation_funcs_user.py` for user defined operations.
- **operands**: The above defined "operation" can take in multiple variables. If operands is defined, then the "variable" entry will be a placeholder name for the calculated variable and the operands will define the model variables that are used to calculate the final variable that will be compared to the observable value entry/s.

!!! warning
    **obs_type**: This has been deprecated in favor of the **operation** entry.


## Parameter Identification Settings

To run the parameter identification we need to set a few entries in the `[project_dir]/user_run_files/user_inputs.yaml file`:

- **param_id_method**: this defins the optimisation method we use. Currently this can only be genetic_algorithm, but more methods are being implemented. Eventually we aim to use CVODES to allow for gradient based optimisation methods.
- **pre_time**: this is the amount of time the simulation is run to get to steady state before comparing to the observables from `obs_data.json`
- **sim_time**: The amount of time used to compare simulation output and observable data. This should be equal to the length of a series observable entry divided by the "sample_rate". If not, only up to the minimum length of observable data and modelled data will be compared. 
- **maximum_step**: The maximum time step for the CVODE solver
- **dt**: The output time step (This hasn’t been tested well for anything but 0.01 s currently)
- **param_id_obs_path**: the path to the `obs_data.json` file described above.
- **ga_options**:
	- **cost_type**: "AE" or "MSE" for absolute error or mean squared error.
	- **num_calls_to_function**: How many forward simulations of pre_time+sim_time will be run in the optimisation algorithm.