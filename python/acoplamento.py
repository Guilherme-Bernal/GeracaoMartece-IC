import numpy as np


def clock_angle(by, bz):
    """Angulo de clock, sempre entre 0 e pi (nao-sinalizado) -- evita base
    negativa em potencias fracionarias (o Newell usa expoente 8/3)."""
    Bt = np.sqrt(by**2 + bz**2)
    with np.errstate(invalid='ignore', divide='ignore'):
        ratio = np.where(Bt > 0, bz / Bt, 1.0)
    ratio = np.clip(ratio, -1.0, 1.0)
    return np.arccos(ratio)


def akasofu_epsilon(v, by, bz):
    """Funcao de acoplamento de Akasofu (1981)."""
    Bt = np.sqrt(by**2 + bz**2)
    theta_c = clock_angle(by, bz)
    return v * Bt**2 * np.sin(theta_c / 2)**4


def newell_coupling(v, by, bz):
    """Funcao de acoplamento de Newell et al. (2007)."""
    Bt = np.sqrt(by**2 + bz**2)
    theta_c = clock_angle(by, bz)
    return (v**(4/3)) * (Bt**(2/3)) * np.sin(theta_c / 2)**(8/3)
