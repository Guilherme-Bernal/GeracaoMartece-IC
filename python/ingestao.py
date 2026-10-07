import numpy as np
import pandas as pd
import pyspedas
from pyspedas.tplot_tools import get_data

from acoplamento import akasofu_epsilon, newell_coupling
from calibracao import calibrar_global


def tvar_to_series(nome):
    """Converte uma tplot variable do pyspedas numa pandas Series indexada por tempo."""
    dados = get_data(nome)
    tempo = pd.to_datetime(dados.times, unit='s')
    valores = np.asarray(dados.y, dtype=float)
    return pd.Series(valores, index=tempo)


def rodar_pipeline_tempestade(nome_evento, trange, inicio_tempestade, fim_tempestade,
                               dt=60.0, bounds_log=None):
    """Roda o pipeline completo (ingestao -> tratamento -> acoplamento ->
    calibracao) para um evento de tempestade geomagnetica, usando dados OMNI."""
    if bounds_log is None:
        bounds_log = [(np.log10(3600), np.log10(8 * 3600)), (-12, -2)]

    print(f"=== {nome_evento} ===")
    var_names_evt = pyspedas.omni.data(trange=trange, datatype='1min', time_clip=True)

    by_evt = tvar_to_series('BY_GSM')
    bz_evt = tvar_to_series('BZ_GSM')
    v_evt = tvar_to_series('flow_speed')
    dst_evt = tvar_to_series('SYM_H') if 'SYM_H' in var_names_evt else tvar_to_series('DST1800')

    df_evt = pd.DataFrame({'By': by_evt, 'Bz': bz_evt, 'V': v_evt, 'Dst': dst_evt}).sort_index()
    df_evt = df_evt[~df_evt.index.duplicated(keep='first')]

    for col in ['By', 'Bz', 'V']:
        df_evt[col] = df_evt[col].interpolate(method='linear', limit=10, limit_area='inside')
    for col in ['By', 'Bz', 'V', 'Dst']:
        df_evt[col] = df_evt[col].ffill().bfill()

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
        'nome': nome_evento, 'df': df_evt,
        'tau_akasofu': tau_ak, 'escala_akasofu': esc_ak, 'rmse_akasofu': rmse_ak,
        'tau_newell': tau_nw, 'escala_newell': esc_nw, 'rmse_newell': rmse_nw,
    }
