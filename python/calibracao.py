import numpy as np
from scipy.optimize import differential_evolution

from solver import simular_burton_rk4


def erro_rmse_rk4(log_params, Q_array, dst0, dst_obs, mask, dt=60.0):
    log_tau, log_escala = log_params
    tau = 10 ** log_tau
    escala = 10 ** log_escala
    sim = simular_burton_rk4(Q_array, dst0, tau, escala, dt)
    return np.sqrt(np.mean((sim[mask] - dst_obs[mask]) ** 2))


def calibrar_global(func_coupling, Q_array, dst0, dst_obs, mask, dt, bounds_log, seed=42):
    """Calibra tau e escala via busca global (differential_evolution).

    workers=1: cada avaliacao do RK4 e rapida (poucos ms), entao o overhead
    de multiprocessing (workers=-1) costuma custar mais do que economiza.
    """
    resultado = differential_evolution(
        erro_rmse_rk4,
        bounds=bounds_log,
        args=(Q_array, dst0, dst_obs, mask, dt),
        seed=seed,
        maxiter=200,
        tol=1e-8,
        polish=True,
        workers=1,
    )
    log_tau, log_escala = resultado.x
    tau = 10 ** log_tau
    escala = 10 ** log_escala
    return tau, escala, resultado.fun
