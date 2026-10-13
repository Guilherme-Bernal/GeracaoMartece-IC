import numpy as np

from aurora import _ajustar_r2


def _melhor_lag_treino(Q_treino, ae_treino, dt, lag_max_min=60, passo_min=5):
    """Busca o lag (em amostras) que maximiza o R^2 log-log, usando SO o
    treino -- nunca o teste -- para depois aplicar o mesmo lag no teste sem
    vazamento de informacao."""
    passo_amostras = max(1, round(passo_min * 60 / dt))
    lag_max_amostras = round(lag_max_min * 60 / dt)

    melhor_lag_amostras = 0
    melhor_r2 = -np.inf
    for lag_amostras in range(0, lag_max_amostras + 1, passo_amostras):
        r2 = _ajustar_r2(Q_treino, ae_treino, dt, lag_amostras, espaco_log=True)
        if r2 is not None and r2 > melhor_r2:
            melhor_r2 = r2
            melhor_lag_amostras = lag_amostras
    return melhor_lag_amostras


def ajustar_coeficientes_ae(Q_array, ae_array, mask, lag_amostras=0):
    """Ajusta os coeficientes (a, b) da lei de potencia AE = 10^a * Q^b
    usando so os dados de treino, com o coupling defasado por lag_amostras
    (Q[t] prevendo AE[t+lag]) para compensar a inercia do eletrojato auroral."""
    Q_treino = Q_array[mask]
    ae_treino = ae_array[mask]
    if lag_amostras == 0:
        x, y = Q_treino, ae_treino
    else:
        x, y = Q_treino[:-lag_amostras], ae_treino[lag_amostras:]

    validos = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    if validos.sum() < 10:
        return None
    coef = np.polyfit(np.log10(x[validos]), np.log10(y[validos]), 1)
    b, a = coef[0], coef[1]
    return a, b


def prever_ae(Q_array, a, b, teto=None):
    """Projeta o AE a partir da funcao de acoplamento: AE = 10^a * Q^b.
    `teto`, se informado, limita a previsao a um valor fisicamente plausivel
    -- evita que a extrapolacao da lei de potencia, fora do dominio de Q
    usado no ajuste, exploda para valores astronomicos."""
    Q_clip = np.clip(Q_array, 1e-30, None)
    pred = (10 ** a) * (Q_clip ** b)
    if teto is not None:
        pred = np.clip(pred, 0, teto)
    return pred


def r2_score(y_obs, y_pred):
    validos = np.isfinite(y_obs) & np.isfinite(y_pred)
    y_obs, y_pred = y_obs[validos], y_pred[validos]
    if len(y_obs) < 2:
        return float('nan')
    ss_res = np.sum((y_obs - y_pred) ** 2)
    ss_tot = np.sum((y_obs - np.mean(y_obs)) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')


def avaliar_previsao_ae(df, Q_akasofu, Q_newell, mask_treino, mask_teste, nome_evento, dt=60.0):
    """Ajusta a lei de potencia Q->AE usando so o treino (com busca de lag
    feita so no treino, sem vazamento), e avalia a previsao (R^2) no trecho
    de teste (holdout) -- nunca visto durante o ajuste. A previsao e limitada
    a um teto fisico (1.5x o maior AE observado no treino) para a
    extrapolacao da lei de potencia nao dominar o erro fora do dominio
    ajustado."""
    if 'AE' not in df.columns:
        print(f"[{nome_evento}] AE_INDEX nao disponivel -- pulando previsao de AE.")
        return None

    ae = df['AE'].ffill().bfill().values
    resultado = {'nome': nome_evento}

    for nome_func, Q_arr in [('akasofu', Q_akasofu), ('newell', Q_newell)]:
        Q_treino, ae_treino = Q_arr[mask_treino], ae[mask_treino]
        lag_amostras = _melhor_lag_treino(Q_treino, ae_treino, dt)

        coef = ajustar_coeficientes_ae(Q_arr, ae, mask_treino, lag_amostras)
        if coef is None:
            continue
        a, b = coef

        teto = 1.5 * np.nanmax(ae_treino)
        Q_teste = Q_arr[mask_teste]
        ae_previsto = prever_ae(Q_teste, a, b, teto=teto)

        if lag_amostras == 0:
            ae_obs_teste = ae[mask_teste]
            ae_previsto_alinhado = ae_previsto
        else:
            ae_obs_teste = ae[mask_teste][lag_amostras:]
            ae_previsto_alinhado = ae_previsto[:-lag_amostras]

        r2_holdout = r2_score(ae_obs_teste, ae_previsto_alinhado)
        resultado[f'r2_teste_{nome_func}'] = r2_holdout
        resultado[f'lag_{nome_func}_min'] = lag_amostras * dt / 60.0
        print(f"{nome_func.capitalize():8s}: lag={lag_amostras * dt / 60.0:.0f}min "
              f"AE previsto no holdout -- R^2={r2_holdout:.3f}")

    print()
    return resultado

def _melhor_lag_pool(eventos, Q_key, dt, lag_max_min=60, passo_min=5):
    """Escolhe o lag (amostras) que maximiza o R^2 pooled (log-log) somando
    os dados de treino de TODOS os eventos -- mais robusto que escolher um
    lag por evento isolado (poucos pontos, lag instavel)."""
    passo_amostras = max(1, round(passo_min * 60 / dt))
    lag_max_amostras = round(lag_max_min * 60 / dt)

    melhor_lag = 0
    melhor_r2 = -np.inf
    for lag_amostras in range(0, lag_max_amostras + 1, passo_amostras):
        xs_all, ys_all = [], []
        for evt in eventos:
            if 'AE' not in evt['df'].columns:
                continue
            Q = evt[Q_key][evt['mask_treino']]
            ae = evt['df']['AE'].ffill().bfill().values[evt['mask_treino']]
            if lag_amostras == 0:
                x, y = Q, ae
            else:
                x, y = Q[:-lag_amostras], ae[lag_amostras:]
            validos = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
            xs_all.append(x[validos])
            ys_all.append(y[validos])
        if not xs_all:
            continue
        x_cat, y_cat = np.concatenate(xs_all), np.concatenate(ys_all)
        if len(x_cat) < 20:
            continue
        logx, logy = np.log10(x_cat), np.log10(y_cat)
        coef = np.polyfit(logx, logy, 1)
        pred = np.polyval(coef, logx)
        ss_res = np.sum((logy - pred) ** 2)
        ss_tot = np.sum((logy - np.mean(logy)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else -np.inf
        if r2 > melhor_r2:
            melhor_r2 = r2
            melhor_lag = lag_amostras
    return melhor_lag


def ajustar_coeficientes_ae_pooled(eventos, Q_key, lag_amostras):
    """Ajusta um UNICO par (a, b) usando o treino de todos os eventos
    concatenado, com o lag ja escolhido por _melhor_lag_pool."""
    xs_all, ys_all = [], []
    for evt in eventos:
        if 'AE' not in evt['df'].columns:
            continue
        Q = evt[Q_key][evt['mask_treino']]
        ae = evt['df']['AE'].ffill().bfill().values[evt['mask_treino']]
        if lag_amostras == 0:
            x, y = Q, ae
        else:
            x, y = Q[:-lag_amostras], ae[lag_amostras:]
        validos = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
        xs_all.append(x[validos])
        ys_all.append(y[validos])
    x_cat, y_cat = np.concatenate(xs_all), np.concatenate(ys_all)
    coef = np.polyfit(np.log10(x_cat), np.log10(y_cat), 1)
    b, a = coef[0], coef[1]
    return a, b


def avaliar_previsao_ae_pooled(eventos, dt=60.0):
    """Versao agrupada (pooled) da previsao de AE: ajusta um UNICO (a, b)
    por funcao de acoplamento com o treino de TODOS os eventos juntos, e
    avalia o R^2 de holdout evento por evento, no teste que o ajuste nunca
    viu. Evita o overfitting de reajustar uma lei de potencia do zero com
    poucas dezenas de pontos por tempestade isolada."""
    import pandas as pd

    resultados = []
    for Q_key, nome_func in [('Q_akasofu', 'akasofu'), ('Q_newell', 'newell')]:
        lag_amostras = _melhor_lag_pool(eventos, Q_key, dt)
        a, b = ajustar_coeficientes_ae_pooled(eventos, Q_key, lag_amostras)
        print(f"[pooled] {nome_func.capitalize()}: lag={lag_amostras * dt / 60:.0f}min  a={a:.3f}  b={b:.3f}")

        for evt in eventos:
            if 'AE' not in evt['df'].columns:
                continue
            ae = evt['df']['AE'].ffill().bfill().values
            ae_treino = ae[evt['mask_treino']]
            teto = 1.5 * np.nanmax(ae_treino)
            Q_teste = evt[Q_key][evt['mask_teste']]
            ae_previsto = prever_ae(Q_teste, a, b, teto=teto)

            if lag_amostras == 0:
                ae_obs = ae[evt['mask_teste']]
                ae_prev_alinhado = ae_previsto
            else:
                ae_obs = ae[evt['mask_teste']][lag_amostras:]
                ae_prev_alinhado = ae_previsto[:-lag_amostras]

            r2 = r2_score(ae_obs, ae_prev_alinhado)
            print(f"  {evt['nome']:30s}: R^2={r2:.3f}")
            resultados.append({'nome': evt['nome'], 'funcao': nome_func, 'r2_teste': r2, 'lag_min': lag_amostras * dt / 60})
    print()
    return pd.DataFrame(resultados)
