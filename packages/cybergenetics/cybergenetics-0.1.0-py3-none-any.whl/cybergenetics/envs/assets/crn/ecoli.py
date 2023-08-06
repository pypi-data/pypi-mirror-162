# Configuration file for CRN Environment

# -- Import modules ------------------------------------------------------------------------------
import numpy as np

# -- Specify ODE for the physical simulation -----------------------------------------------------

# Parameters of the parametric ODE
d_r = 0.0956
d_p = 0.0214
k_m = 0.0116
b_r = 0.0965

# Initial state of the parametric ODE: x(0)
init_state = np.array([1.0, 1.0, 1.0])


# Define the RHS of the parametric ODE: dx/dt = f(x(t), u(t))
def ode(x: np.ndarray, u: float) -> np.ndarray:
    u = np.array([1, 5.134 / (1 + 5.411 * np.exp(-0.0698 * u)) + 0.1992 - 1])
    A_c = np.array([[-d_r, 0.0, 0.0], [d_p + k_m, -d_p - k_m, 0.0], [0.0, d_p, -d_p]])
    B_c = np.array([[d_r, b_r], [0.0, 0.0], [0.0, 0.0]])
    dxdt = A_c @ x + B_c @ u
    return dxdt


# -- Specify the target and reward in the task ---------------------------------------------------

# Define the target, i.e. the reference computation functioon
# def reference_func(t: np.ndarray) -> np.ndarray:
#     return

# Define the reward computation function
# def reward_func(
#     achieved: Union[float, np.ndarray],
#     desired: Union[float, np.ndarray],
#     tolerance: float,
# ) -> float:
#     return

# -- Environment configuration -------------------------------------------------------------------
configs = {
    'environment': {
        'discrete': False,
        'render_mode': 'dashboard',
        'physics': {
            'ode': ode,
            'init_state': init_state,
            'integrator': 'RK45',
            'n_sub_timesteps': 20,
            'system_noise': 0.0,
            'actuation_error': 0.0,
            'actuation_noise': None,
            'state_min': 0.0,
            'state_max': np.inf,
            'state_info': {
                'color': ['tab:red', 'tab:purple', 'tab:green'],
                'label': ['R', 'P', 'G'],
                'xlim': [-1, 601],
                'ylim': [0.8, 2.2],
            },
            'control_min': 0.0,
            'control_max': 20.0,     # control signal u: intensity (%) ranging from 0.0% to 20.0%
            'control_info': {
                'color': 'tab:blue',
                'label': 'I (%)',
                'xlim': [-1, 601],
                'ylim': [-0.5, 20.5],
            },
        },
        'task': {
            'tracking': 'const',
            'scale': 1.8,
            'sampling_rate': 5,     # per min
            'observability': -1,     # only signal 'G' can be observed
            'reward': 'in_tolerance',
            'reward_kwargs': {},
            'reward_info': {
                'color': 'tab:orange',
                'label': 'in_tolerance',
                'xlim': [-1, 601],
                'ylim': [-0.05, 1.1],
            },
            'tolerance': 0.05,
            'observation_error': 0.0,
            'observation_noise': None,
        },
    },
    'wrappers': {
        'max_episode_steps': 6 * 10,     # 5 hours
        'full_observation': False,
        'time_aware': False,
        'timestep_aware': False,
        'reference_aware': False,
        'tolerance_aware': False,
        'tolerance_recall_aware': False,
        'recall_steps': 3,
        'tolerance': 're',
        'action_aware': False,
        'rescale_action': False,
        'action_min': 0.0,
        'action_max': 1.0,
        'track_episode': False,
        'record_episode': False,
        'fixed_episode_steps': 6 * 10,
    },
}
