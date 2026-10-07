import numpy as np


def ajustar_coeficientes_ae(Q_array, ae_array, mask):
    """Ajusta os coeficientes (a, b) da lei de potencia AE = 10^a * Q^b
    usando so os dados de treino."""
    x, y = Q_array[mask], ae_array[mask]
    validos = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    if validos.sum() < 10:
        return None
    coef = np.polyfit(np.log10(x[validos]), np.log10(y[validos]), 1)
    b, a = coef[0], coef[1]
    return a, b


def prever_ae(Q_array, a, b):
    """Projeta o AE a partir da funcao de acoplamento: AE = 10^a * Q^b."""
    Q_clip = np.clip(Q_array, 1e-30, None)
    return (10 ** a) * (Q_clip ** b)


def r2_score(y_obs, y_pred):
    validos = np.isfinite(y_obs) & np.isfinite(y_pred)
    y_obs, y_pred = y_obs[validos], y_pred[validos]
    if len(y_obs) < 2:
        return float('nan')
    ss_res = np.sum((y_obs - y_pred) ** 2)
    ss_tot = np.sum((y_obs - np.mean(y_obs)) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')


def avaliar_previsao_ae(df, Q_akasofu, Q_newell, mask_treino, mask_teste, nome_evento):
    """Ajusta a lei de potencia Q->AE usando so o treino, e avalia a previsao
    (R^2) no trecho de teste (holdout) -- nunca visto durante o ajuste."""
    if 'AE' not in df.columns:
        print(f"[{nome_evento}] AE_INDEX nao disponivel -- pulando previsao de AE.")
        return None

    ae = df['AE'].ffill().bfill().values
    resultado = {'nome': nome_evento}

    for nome_func, Q_arr in [('akasofu', Q_akasofu), ('newell', Q_newell)]:
        coef = ajustar_coeficientes_ae(Q_arr, ae, mask_treino)
        if coef is None:
            continue
        a, b = coef
        ae_previsto = prever_ae(Q_arr[mask_teste], a, b)
        r2_holdout = r2_score(ae[mask_teste], ae_previsto)
        resultado[f'r2_teste_{nome_func}'] = r2_holdout
        print(f"{nome_func.capitalize():8s}: AE previsto no holdout -- R^2={r2_holdout:.3f}")

    print()
    return resultado
