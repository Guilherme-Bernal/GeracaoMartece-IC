import numpy as np


def simular_burton_rk4(Q_array, dst0, tau, escala, dt=60.0):
    """Integra a equacao de Burton et al. (1975) via RK4 de passo fixo.

    dDst/dt = Q(t) - Dst/tau

    O sinal negativo em Qi/Qi1 e intencional: a injecao de energia do vento
    solar reduz o Dst (o torna mais negativo durante tempestades), e as
    funcoes de acoplamento (Akasofu, Newell) retornam magnitudes positivas.
    """
    n = len(Q_array)
    dst = np.empty(n)
    dst[0] = dst0
    for i in range(n - 1):
        Qi = -Q_array[i] * escala
        Qi1 = -Q_array[i + 1] * escala
        y = dst[i]
        k1 = Qi - y / tau
        k2 = Qi - (y + 0.5 * dt * k1) / tau
        k3 = Qi - (y + 0.5 * dt * k2) / tau
        k4 = Qi1 - (y + dt * k3) / tau
        dst[i + 1] = y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    return dst
