import numpy as np
from previsao import ajustar_coeficientes_ae, prever_ae, r2_score


def _gerar_lei_de_potencia(seed, a_real=2.0, b_real=0.8, n=200):
    rng = np.random.default_rng(seed)
    q = rng.uniform(1e-5, 1e-2, size=n)
    ae = (10 ** a_real) * (q ** b_real)
    return q, ae, a_real, b_real


def test_ajuste_recupera_lei_de_potencia_sintetica():
    q, ae, a_real, b_real = _gerar_lei_de_potencia(42)
    mask = np.ones(len(q), dtype=bool)
    a, b = ajustar_coeficientes_ae(q, ae, mask)
    assert abs(a - a_real) < 0.05
    assert abs(b - b_real) < 0.05


def test_previsao_com_dados_sinteticos_tem_r2_alto():
    q, ae, _, _ = _gerar_lei_de_potencia(0)
    mask = np.zeros(len(q), dtype=bool)
    mask[:150] = True
    a, b = ajustar_coeficientes_ae(q, ae, mask)
    pred = prever_ae(q[~mask], a, b)
    r2 = r2_score(ae[~mask], pred)
    assert r2 > 0.99


def test_r2_score_perfeito():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    assert r2_score(y, y) == 1.0


def test_r2_score_pior_que_a_media_e_negativo():
    y_obs = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([100.0, -100.0, 200.0, -200.0])
    assert r2_score(y_obs, y_pred) < 0
