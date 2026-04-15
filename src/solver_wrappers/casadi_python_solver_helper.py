import importlib.util
import numpy as np
import copy
import sys
import casadi as ca
DEBUG = False


class SimulationHelper:
    """
    CasADi-based solver for libCellML-generated Python modules.

    Matches the key interface of the OpenCOR SimulationHelper:
    - run()
    - update_times(dt, start_time, sim_time, pre_time)
    - get_results / get_all_results / get_all_variable_names
    - get_init_param_vals / set_param_vals
    """

    def __init__(self, model_path, dt, sim_time, solver_info=None, pre_time=0.0):
        self.model_path = model_path
        self.dt = dt
        self.pre_time = pre_time
        self.sim_time = sim_time
        self.solver_info = solver_info or {}
        solver_method = self.solver_info.get('method')
        self.solve_ivp_method = solver_method
        self._load_model()
        self.update_times(dt, 0.0, sim_time, pre_time)
        self._init_state()

    def set_protocol_info(self, protocol_info):
        """Store protocol metadata for a common helper API."""
        self.protocol_info = protocol_info

    # ---- setup helpers ----
    def _load_model(self):
        spec = importlib.util.spec_from_file_location("generated_model", self.model_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.model = module

        self.STATE_COUNT = module.STATE_COUNT
        self.VARIABLE_INFO = module.VARIABLE_INFO
        self.STATE_INFO = module.STATE_INFO

        # maps
        self.state_name_to_idx = {info["name"]: idx for idx, info in enumerate(self.STATE_INFO)}
        self.var_name_to_idx = {info["name"]: idx for idx, info in enumerate(self.VARIABLE_INFO)}
        # inverse maps for lookup once we've resolved indices
        self.state_idx_to_name = {idx: info["name"] for idx, info in enumerate(self.STATE_INFO)}
        self.var_idx_to_name = {idx: info["name"] for idx, info in enumerate(self.VARIABLE_INFO)}

        # identify constants and algebraics
        self.constant_indices = [i for i, info in enumerate(self.VARIABLE_INFO) if info["type"].name in ["CONSTANT", "COMPUTED_CONSTANT"]]
        self.algebraic_indices = [i for i, info in enumerate(self.VARIABLE_INFO) if info["type"].name == "ALGEBRAIC"]

    def _init_state(self):
        self.states = self.model.create_states_array()
        self.rates = self.model.create_states_array()
        self.variables = self.model.create_variables_array()

        self.states_symb = self._compute_states_symb()
        self.variables_all_symb = self._compute_all_variables_symb()
        self.variables_all_symb, self.rates_symb = self._compute_rates_symb()

        self._patch_math_functions()

        self.model.initialise_variables(self.states, self.rates, self.variables)
        self.model.compute_computed_constants(self.variables)
        self._store_constants_defaults()
        self._store_variable_defaults()

    def _store_constants_defaults(self):
        self.default_constants = [self.variables[i] for i in self.constant_indices]
        self.default_state_inits = [s for s in self.states]

    def _store_variable_defaults(self):
        self.variables_symb = ca.vertcat(
            *[self.variables_all_symb[i] for i in self.constant_indices]
        )
        self.variables = np.array(
            [self.variables[i] for i in self.constant_indices],
            dtype=float,
        )

    def _compute_states_symb(self):
        states = self.states.copy()
        for i, info in enumerate(self.model.STATE_INFO):
            states[i] = ca.SX.sym(info["name"])
        self.states = states
        return ca.vertcat(*states)

    def _compute_all_variables_symb(self):
        variables = self.variables.copy()
        for i, info in enumerate(self.model.VARIABLE_INFO):
            variables[i] = ca.SX.sym(info["name"])
        self.variables = variables
        return ca.vertcat(*variables)

    def _compute_rates_symb(self):
        self.model.compute_rates(self.start_time, self.states, self.rates, self.variables)
        return ca.vertcat(*self.variables), ca.vertcat(*self.rates)
    
    def _patch_math_functions(self):
        cellml_math_map = {
            "log": ca.log,
            "exp": ca.exp,
            "sin": ca.sin,
            "cos": ca.cos,
            "tan": ca.tan,
            "sqrt": ca.sqrt,
        }
        for name, func in cellml_math_map.items():
            setattr(self.model, name, func)

    # ---- name resolution helpers ----
    def _resolve_name(self, name: str):
        """
        Resolve parameter/variable names that may contain prefixes (e.g., 'global/').
        Tries exact, then last path element, then slash-to-underscore form.
        """
        name = str(name).strip()
        candidates = [name]
        if "/" in name:
            parts = name.split("/")
            last = parts[-1]
            first = parts[0]
            candidates.append(last)
            candidates.append(name.replace("/", "_"))
            candidates.append(f"{first}_{last}")
            candidates.append(f"{last}_{first}")
            candidates.append(f"{first}{last}")
            candidates.append(name.replace("/", ""))  # drop slash
        # also try stripping any 'global_' prefix
        candidates += [c.replace("global_", "") for c in list(candidates)]
        for cand in candidates:
            if cand in self.state_name_to_idx:
                return ("state", self.state_name_to_idx[cand])
            if cand in self.var_name_to_idx:
                return ("var", self.var_name_to_idx[cand])
        return (None, None)

    # ---- timing helpers ----
    def update_times(self, dt, start_time, sim_time, pre_time):
        self.dt = dt
        self.pre_time = pre_time
        self.sim_time = sim_time
        self.start_time = start_time
        self.stop_time = start_time + pre_time + sim_time
        self.pre_steps = int(pre_time/dt)
        self.n_steps = int(sim_time/dt)
        self.t_eval = np.arange(start_time, self.stop_time + dt/2, dt)
        # stored portion excludes pre_time
        self.tSim = self.t_eval[self.pre_steps:]

    # ---- parameter helpers ----
    def get_init_param_vals(self, param_names):
        vals = []
        for name_or_list in param_names:
            if not isinstance(name_or_list, list):
                name_or_list = [name_or_list]
            sub = []
            for name in name_or_list:
                kind, idx = self._resolve_name(name)
                if kind == "state":
                    sub.append(self.states[idx])
                elif kind == "var":
                    sub.append(self.variables[idx])
                else:
                    raise ValueError(f"parameter name {name} not found in states or variables")
            vals.append(sub if len(sub) > 1 else sub[0])
        return vals

    def set_param_vals(self, param_names, param_vals):
        for idx, name_or_list in enumerate(param_names):
            vals = param_vals[idx]

            def _to_list(x):
                if isinstance(x, (list, tuple)):
                    return list(x)
                try:
                    import numpy as _np
                    if isinstance(x, _np.ndarray):
                        return x.tolist()
                except Exception:
                    pass
                return [x]

            name_or_list = _to_list(name_or_list)
            vals = _to_list(vals)

            for name, val in zip(name_or_list, vals):
                kind, idx_res = self._resolve_name(name)
                if kind == "state":
                    self.states[idx_res] = val
                elif kind == "var":
                    self.variables[idx_res] = val
                else:
                    raise ValueError(f"parameter name {name} not found in states or variables")
        self.model.compute_computed_constants(self.variables)

    # ---- simulation ----
    def run(self):
        ode = {
            "x": self.states_symb,
            "p": self.variables_symb,
            "ode": self.rates_symb,
        }

        self.F = ca.integrator("F", self.solve_ivp_method, ode, 0, self.dt)
        self.F_map = self.F.mapaccum(self.n_steps)

        res = self.F_map(x0=self.states_symb, p=self.variables_symb)
        self.state_traj_symb = ca.horzcat(self.states_symb, res["xf"])
        
        return True

    # ---- results ----
    def get_all_variable_names(self):
        return list(self.state_name_to_idx.keys()) + list(self.var_name_to_idx.keys())

    def _extract(self, name):
        if name == 'time':
            return self.tSim
        if name in self.state_name_to_idx:
            data = self.state_traj_symb[self.state_name_to_idx[name], :]
            return data[self.pre_steps:]
        if name in self.var_name_to_idx:
            data = self.var_traj[name]
            return data[self.pre_steps:]
        # attempt to resolve common alternative namings (e.g., "a/b" vs "a_b")
        kind, idx_res = self._resolve_name(name)
        if kind == "state":
            resolved_name = self.state_idx_to_name[idx_res]
            data = self.state_traj_symb[idx_res, :]
            return data[self.pre_steps:]
        if kind == "var":
            resolved_name = self.var_idx_to_name[idx_res]
            data = self.var_traj[resolved_name]
            return data[self.pre_steps:]
        raise ValueError(f"variable {name} not found")

    def get_results(self, variables_list_of_lists, flatten=False):
        if type(variables_list_of_lists[0]) is not list:
            variables_list_of_lists = [[entry] for entry in variables_list_of_lists]
        results = []
        for variables_list in variables_list_of_lists:
            row = [self._extract(name) for name in variables_list]
            results.append(row)
        if flatten:
            results = [item for sublist in results for item in sublist]
        return results

    def get_all_results(self, flatten=False):
        return self.get_results(self.get_all_variable_names(), flatten=flatten)

    def _create_param_subset(self, param_names, param_vals = None):
        param_names = [x[0] for x in param_names]
        params = []
        for s in param_names:
            left, right = s.split("/")
            params.append(f"{right}_{left}")

        const_symb = [self.variables_all_symb[i] for i in self.constant_indices]
        const_names = [s.name() for s in const_symb]

        name_to_symb = dict(zip(const_names, const_symb))
        name_to_init = dict(zip(const_names, self.variables))

        variables_symb_subset = ca.vertcat(*[
            name_to_symb[name] for name in params
        ])

        if param_vals is not None:
            param_vals = np.asarray(param_vals, dtype=float)

            for name, val in zip(params, param_vals):
                idx = const_names.index(name)
                self.variables[idx] = val

            variables_subset = param_vals
        else:
            variables_subset = np.array(
                [
                    name_to_init[name] for name in params
                ],
                dtype=float
            )

        self.variables_symb_subset = variables_symb_subset
        self.variables_subset = variables_subset

    # ---- reset helpers ----
    def reset_and_clear(self, only_one_exp=-1):
        self._init_state()

    def reset_states(self):
        self.states = copy.copy(self.default_state_inits)
        self.model.compute_computed_constants(self.variables)

    def close_simulation(self):
        # no-op for scipy solver
        pass

