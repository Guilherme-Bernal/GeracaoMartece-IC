import numpy as np
from solver import simular_burton_rk4


def test_decaimento_livre_sem_forcante():
    n = 1000
    dt = 60.0
    tau = 3600.0
    dst0 = -100.0
    q = np.zeros(n)
    sim = simular_burton_rk4(q, dst0, tau, escala=1e-7, dt=dt)
    t_final = (n - 1) * dt
    esperado = dst0 * np.exp(-t_final / tau)
    assert abs(sim[-1] - esperado) < 1.0


def test_solver_preserva_tamanho_do_array():
    rng = np.random.default_rng(1)
    q = rng.random(500) * 1e-7
    sim = simular_burton_rk4(q, -50.0, 7200.0, 1e-7, 60.0)
    assert len(sim) == len(q)


def test_solver_sem_nan_para_entrada_valida():
    rng = np.random.default_rng(2)
    q = rng.random(500) * 1e-7
    sim = simular_burton_rk4(q, -50.0, 7200.0, 1e-7, 60.0)
    assert np.all(np.isfinite(sim))
