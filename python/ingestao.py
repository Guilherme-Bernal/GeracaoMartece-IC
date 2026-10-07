import numpy as np
import pandas as pd
import pyspedas
from pyspedas.tplot_tools import get_data

from acoplamento import akasofu_epsilon, newell_coupling
from calibracao import calibrar_global
from solver import simular_burton_rk4


def tvar_to_series(nome):
    """Converte uma tplot variable do pyspedas numa pandas Series indexada por tempo."""
    dados = get_data(nome)
    tempo = pd.to_datetime(dados.times, unit='s')
    valores = np.asarray(dados.y, dtype=float)
    return pd.Series(valores, index=tempo)


def _ingerir_evento(trange):
    """Busca e trata (gaps, AE opcional) os dados OMNI de um evento. Usado
    tanto por rodar_pipeline_tempestade quanto por rodar_pipeline_com_holdout."""
    var_names_evt = pyspedas.omni.data(trange=trange, datatype='1min', time_clip=True)

    by_evt = tvar_to_series('BY_GSM')
    bz_evt = tvar_to_series('BZ_GSM')
    v_evt = tvar_to_series('flow_speed')
    dst_evt = tvar_to_series('SYM_H') if 'SYM_H' in var_names_evt else tvar_to_series('DST1800')

    colunas = {'By': by_evt, 'Bz': bz_evt, 'V': v_evt, 'Dst': dst_evt}
    candidatos_ae = ['AE_INDEX', 'AE']
    nome_ae = next((c for c in candidatos_ae if c in var_names_evt), None)
    tem_ae = nome_ae is not None
    if tem_ae:
        colunas['AE'] = tvar_to_series(nome_ae)

    df_evt = pd.DataFrame(colunas).sort_index()
    df_evt = df_evt[~df_evt.index.duplicated(keep='first')]

    cols_interp = ['By', 'Bz', 'V'] + (['AE'] if tem_ae else [])
    for col in cols_interp:
        df_evt[col] = df_evt[col].interpolate(method='linear', limit=10, limit_area='inside')
    cols_fill = cols_interp + ['Dst']
    for col in cols_fill:
        df_evt[col] = df_evt[col].ffill().bfill()

    return df_evt, tem_ae


def rodar_pipeline_tempestade(nome_evento, trange, inicio_tempestade, fim_tempestade,
                               dt=60.0, bounds_log=None):
    """Roda o pipeline completo (ingestao -> tratamento -> acoplamento ->
    calibracao) para um evento de tempestade geomagnetica, usando dados OMNI."""
    if bounds_log is None:
        bounds_log = [(np.log10(3600), np.log10(8 * 3600)), (-12, -2)]

    print(f"=== {nome_evento} ===")
    df_evt, tem_ae = _ingerir_evento(trange)

    Q_ak_evt = akasofu_epsilon(df_evt['V'].values, df_evt['By'].values, df_evt['Bz'].values)
    Q_nw_evt = newell_coupling(df_evt['V'].values, df_evt['By'].values, df_evt['Bz'].values)

    dst0_evt = df_evt['Dst'].iloc[0]
    mask_evt = (df_evt.index >= inicio_tempestade) & (df_evt.index <= fim_tempestade)

    tau_ak, esc_ak, rmse_ak = calibrar_global(
        akasofu_epsilon, Q_ak_evt, dst0_evt, df_evt['Dst'].values, mask_evt, dt, bounds_log
    )
    tau_nw, esc_nw, rmse_nw = calibrar_global(
        newell_coupling, Q_nw_evt, dst0_evt, df_evt['Dst'].values, mask_evt, dt, bounds_log
    )

    print(f"Akasofu : tau={tau_ak:.1f}s  escala={esc_ak:.3e}  RMSE={rmse_ak:.4f}")
    print(f"Newell  : tau={tau_nw:.1f}s  escala={esc_nw:.3e}  RMSE={rmse_nw:.4f}")
    print()

    return {
        'nome': nome_evento, 'df': df_evt, 'mask': mask_evt, 'dt': dt,
        'Q_akasofu': Q_ak_evt, 'Q_newell': Q_nw_evt, 'tem_ae': tem_ae,
        'tau_akasofu': tau_ak, 'escala_akasofu': esc_ak, 'rmse_akasofu': rmse_ak,
        'tau_newell': tau_nw, 'escala_newell': esc_nw, 'rmse_newell': rmse_nw,
    }


def rodar_pipeline_com_holdout(nome_evento, trange, inicio_tempestade, fim_tempestade,
                                fracao_treino=0.6, dt=60.0, bounds_log=None):
    """Como rodar_pipeline_tempestade, mas calibra tau/escala usando so a
    primeira fracao_treino da janela de tempestade, e avalia o RMSE na parte
    restante (holdout) -- uma previsao genuina fora da amostra, nao so um
    ajuste retrospectivo."""
    if bounds_log is None:
        bounds_log = [(np.log10(3600), np.log10(8 * 3600)), (-12, -2)]

    print(f"=== {nome_evento} (com holdout) ===")
    df_evt, tem_ae = _ingerir_evento(trange)

    Q_ak_evt = akasofu_epsilon(df_evt['V'].values, df_evt['By'].values, df_evt['Bz'].values)
    Q_nw_evt = newell_coupling(df_evt['V'].values, df_evt['By'].values, df_evt['Bz'].values)
    dst0_evt = df_evt['Dst'].iloc[0]

    duracao = fim_tempestade - inicio_tempestade
    corte = inicio_tempestade + duracao * fracao_treino
    mask_treino = (df_evt.index >= inicio_tempestade) & (df_evt.index < corte)
    mask_teste = (df_evt.index >= corte) & (df_evt.index <= fim_tempestade)

    resultado = {
        'nome': nome_evento, 'df': df_evt, 'dt': dt, 'tem_ae': tem_ae,
        'mask_treino': mask_treino, 'mask_teste': mask_teste,
        'Q_akasofu': Q_ak_evt, 'Q_newell': Q_nw_evt, 'dst0': dst0_evt,
    }

    for nome_func, func, Q_arr in [('akasofu', akasofu_epsilon, Q_ak_evt), ('newell', newell_coupling, Q_nw_evt)]:
        tau, escala, rmse_treino = calibrar_global(
            func, Q_arr, dst0_evt, df_evt['Dst'].values, mask_treino, dt, bounds_log
        )
        sim = simular_burton_rk4(Q_arr, dst0_evt, tau, escala, dt)
        rmse_teste = np.sqrt(np.mean((sim[mask_teste] - df_evt['Dst'].values[mask_teste]) ** 2))

        resultado[f'tau_{nome_func}'] = tau
        resultado[f'escala_{nome_func}'] = escala
        resultado[f'rmse_treino_{nome_func}'] = rmse_treino
        resultado[f'rmse_teste_{nome_func}'] = rmse_teste

        print(f"{nome_func.capitalize():8s}: tau={tau:.1f}s escala={escala:.3e} "
              f"| RMSE treino={rmse_treino:.2f} | RMSE teste (holdout)={rmse_teste:.2f}")

    print()
    return resultado
