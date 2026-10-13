import numpy as np
import pandas as pd
from ingestao import detectar_janela_tempestade


def test_detecta_janela_em_tempestade_sintetica():
    tempo = pd.date_range("2024-01-01", periods=300, freq="1min")
    dst = np.full(300, -5.0)
    for i in range(300):
        if i < 100:
            dst[i] = -5.0
        elif i < 150:
            dst[i] = -5.0 - (i - 100) * 3.0
        else:
            dst[i] = min(-150.0 + (i - 150) * 2.0, -5.0)
    df = pd.DataFrame({"Dst": dst}, index=tempo)

    inicio, fim = detectar_janela_tempestade(df)
    assert inicio < tempo[150]
    assert fim > tempo[150]
    assert df.loc[inicio, "Dst"] >= -20.0
