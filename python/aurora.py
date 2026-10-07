import numpy as np
import pandas as pd
import pyspedas

from ingestao import tvar_to_series


def _ajustar_r2(x, y, dt, lag_amostras, espaco_log):
    """Calcula o R^2 da regressao linear entre x e y (com lag aplicado),
    opcionalmente em escala log-log (lei de potencia)."""
    if lag_amostras == 0:
        xs, ys = x, y
    else:
        xs, ys = x[:-lag_amostras], y[lag_amostras:]

    if len(xs) < 10:
        return None

    if espaco_log:
        validos = np.isfinite(xs) & np.isfinite(ys) & (xs > 0) & (ys > 0)
    else:
        validos = np.isfinite(xs) & np.isfinite(ys)

    if validos.sum() < 10:
        return None

    xv, yv = xs[validos], ys[validos]
    if espaco_log:
        xv, yv = np.log10(xv), np.log10(yv)

    coef = np.polyfit(xv, yv, 1)
    pred = np.polyval(coef, xv)
    ss_res = np.sum((yv - pred) ** 2)
    ss_tot = np.sum((yv - np.mean(yv)) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else -np.inf


def _melhor_lag_r2(coupling_arr, ae_arr, dt, lag_max_min=60, passo_min=5, espaco_log=False):
    """Testa deslocamentos temporais (lag) entre a funcao de acoplamento e o AE,
    retornando o lag (em minutos) que maximiza o R^2. Com espaco_log=True, ajusta
    em escala log-log (lei de potencia), como no metodo original de Newell et al.
    (2007) -- mais robusto a eventos com grande dinamica de valores (tempestades
    extremas)."""
    passo_amostras = max(1, round(passo_min * 60 / dt))
    lag_max_amostras = round(lag_max_min * 60 / dt)

    melhor_lag_min = 0
    melhor_r2 = -np.inf

    for lag_amostras in range(0, lag_max_amostras + 1, passo_amostras):
        r2 = _ajustar_r2(coupling_arr, ae_arr, dt, lag_amostras, espaco_log)
        if r2 is not None and r2 > melhor_r2:
            melhor_r2 = r2
            melhor_lag_min = lag_amostras * dt / 60.0

    return melhor_lag_min, melhor_r2


def analisar_ae(df, Q_akasofu, Q_newell, mask, dt, nome_evento):
    """Correlaciona Akasofu e Newell com o indice AE (eletrojato auroral),
    proxy direto de atividade auroral -- diferente do Dst (corrente de anel).
    Testa ajuste linear e log-log (lei de potencia) lado a lado: eventos
    extremos (indices saturados, ex: Kp=9.0) tendem a quebrar a relacao
    linear, e o log-log pode recuperar parte da correlacao nesses casos."""
    if 'AE' not in df.columns:
        print(f"[{nome_evento}] AE_INDEX nao disponivel para este evento -- pulando.")
        return None

    ae = df['AE'].ffill().bfill().values

    Q_ak_mask = Q_akasofu[mask]
    Q_nw_mask = Q_newell[mask]
    ae_mask = ae[mask]

    lag_ak_lin, r2_ak_lin = _melhor_lag_r2(Q_ak_mask, ae_mask, dt, espaco_log=False)
    lag_nw_lin, r2_nw_lin = _melhor_lag_r2(Q_nw_mask, ae_mask, dt, espaco_log=False)
    lag_ak_log, r2_ak_log = _melhor_lag_r2(Q_ak_mask, ae_mask, dt, espaco_log=True)
    lag_nw_log, r2_nw_log = _melhor_lag_r2(Q_nw_mask, ae_mask, dt, espaco_log=True)

    print(f"=== {nome_evento} -- correlacao com AE ===")
    print(f"Akasofu linear : lag={lag_ak_lin:.0f}min  R^2={r2_ak_lin:.3f}")
    print(f"Akasofu log-log: lag={lag_ak_log:.0f}min  R^2={r2_ak_log:.3f}")
    print(f"Newell  linear : lag={lag_nw_lin:.0f}min  R^2={r2_nw_lin:.3f}")
    print(f"Newell  log-log: lag={lag_nw_log:.0f}min  R^2={r2_nw_log:.3f}")
    print()

    return {
        'nome': nome_evento,
        'lag_akasofu_min': lag_ak_lin, 'r2_akasofu_ae': r2_ak_lin,
        'lag_newell_min': lag_nw_lin, 'r2_newell_ae': r2_nw_lin,
        'lag_akasofu_loglog_min': lag_ak_log, 'r2_akasofu_ae_loglog': r2_ak_log,
        'lag_newell_loglog_min': lag_nw_log, 'r2_newell_ae_loglog': r2_nw_log,
    }


def estimar_oval_auroral(kp):
    """Latitude geomagnetica aproximada da borda equatorial do ovalo auroral,
    em funcao do Kp (aprox. empirica, estilo Starkov 1994 / Holzworth & Meng 1975)."""
    return 64.6 - 2.14 * np.asarray(kp, dtype=float)


def obter_kp_horario(trange):
    """Busca o indice Kp (resolucao horaria) do OMNI. Kp no OMNI vem *10
    (ex: 37 = Kp 3.7), por isso a divisao."""
    var_names = pyspedas.omni.data(trange=trange, datatype='hourly', time_clip=True)
    candidatos = ['KP', 'Kp_index', 'KP1800']
    nome_var = next((c for c in candidatos if c in var_names), None)
    if nome_var is None:
        raise ValueError(f"Variavel de Kp nao encontrada. Disponiveis: {var_names}")
    return tvar_to_series(nome_var) / 10.0


def analisar_oval(trange, inicio_tempestade, fim_tempestade, nome_evento):
    """Kp maximo durante a tempestade + latitude estimada da borda do ovalo auroral."""
    kp = obter_kp_horario(trange)
    mask = (kp.index >= inicio_tempestade) & (kp.index <= fim_tempestade)
    kp_max = kp[mask].max()
    lat_min = estimar_oval_auroral(kp_max)

    print(f"=== {nome_evento} -- ovalo auroral ===")
    print(f"Kp maximo durante a tempestade: {kp_max:.1f}")
    print(f"Latitude geomagnetica estimada da borda equatorial: {lat_min:.1f} graus")
    print()

    return {'nome': nome_evento, 'kp_max': kp_max, 'latitude_oval_min': lat_min}
