import numpy as np
from acoplamento import akasofu_epsilon, newell_coupling


def test_akasofu_sem_nan_para_clock_angle_extremo():
    v = np.array([400.0, 400.0, 400.0])
    by = np.array([0.0, 5.0, -5.0])
    bz = np.array([5.0, 0.0, 0.0])
    q = akasofu_epsilon(v, by, bz)
    assert np.all(np.isfinite(q))


def test_newell_sem_nan_para_clock_angle_extremo():
    v = np.array([400.0, 400.0, 400.0])
    by = np.array([0.0, 5.0, -5.0])
    bz = np.array([5.0, 0.0, 0.0])
    q = newell_coupling(v, by, bz)
    assert np.all(np.isfinite(q))


def test_acoplamento_nao_negativo():
    v = np.array([400.0])
    by = np.array([3.0])
    bz = np.array([-7.0])
    assert akasofu_epsilon(v, by, bz)[0] >= 0
    assert newell_coupling(v, by, bz)[0] >= 0


def test_newell_cresce_com_vento_mais_rapido():
    v = np.array([300.0, 600.0])
    by = np.array([0.0, 0.0])
    bz = np.array([-10.0, -10.0])
    q = newell_coupling(v, by, bz)
    assert q[1] > q[0]
