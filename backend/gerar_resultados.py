import sys
import json
sys.path.insert(0, "../python")

import numpy as np
import pandas as pd
from ingestao import rodar_pipeline_com_holdout
from solver import simular_burton_rk4
from previsao import avaliar_previsao_ae_pooled
from aurora import analisar_oval

eventos_config = [
    {"id": "gannon", "nome": "Gannon (mai/2024)", "trange": ["2024-05-10", "2024-05-12"],
     "inicio": "2024-05-10 16:00", "fim": "2024-05-11 12:00"},
    {"id": "stpatrick", "nome": "St. Patrick's Day (mar/2015)", "trange": ["2015-03-17", "2015-03-19"],
     "inicio": "2015-03-17 04:00", "fim": "2015-03-18 00:00"},
    {"id": "halloween", "nome": "Halloween Storm (out/2003)", "trange": ["2003-10-29", "2003-10-31"],
     "inicio": "2003-10-29 06:00", "fim": "2003-10-30 12:00"},
    {"id": "set2017", "nome": "Tempestade set/2017", "trange": ["2017-09-07", "2017-09-09"],
     "inicio": "2017-09-07 23:00", "fim": "2017-09-08 14:00"},
    {"id": "ago2011", "nome": "Tempestade ago/2011", "trange": ["2011-08-05", "2011-08-07"],
     "inicio": "2011-08-05 18:00", "fim": "2011-08-06 12:00"},
]

resultados_holdout = []
for cfg in eventos_config:
    r = rodar_pipeline_com_holdout(
        nome_evento=cfg["nome"],
        trange=cfg["trange"],
        inicio_tempestade=pd.Timestamp(cfg["inicio"]),
        fim_tempestade=pd.Timestamp(cfg["fim"]),
    )
    r["id"] = cfg["id"]
    r["trange"] = cfg["trange"]
    r["inicio_tempestade"] = pd.Timestamp(cfg["inicio"])
    r["fim_tempestade"] = pd.Timestamp(cfg["fim"])
    resultados_holdout.append(r)

tabela_ae = avaliar_previsao_ae_pooled(resultados_holdout, dt=60.0)

eventos_saida = []
for r in resultados_holdout:
    df = r["df"]
    dt = r["dt"]
    dst0 = r["dst0"]

    sim_ak = simular_burton_rk4(r["Q_akasofu"], dst0, r["tau_akasofu"], r["escala_akasofu"], dt)
    sim_nw = simular_burton_rk4(r["Q_newell"], dst0, r["tau_newell"], r["escala_newell"], dt)

    indices_teste = np.where(r["mask_teste"])[0]
    corte_ts = df.index[indices_teste[0]].isoformat() if len(indices_teste) else None

    linha_ae = tabela_ae[tabela_ae["nome"] == r["nome"]]
    ae_ak = linha_ae[linha_ae["funcao"] == "akasofu"]["r2_teste"]
    ae_nw = linha_ae[linha_ae["funcao"] == "newell"]["r2_teste"]

    kp_max = lat_oval = None
    try:
        res_oval = analisar_oval(r["trange"], r["inicio_tempestade"], r["fim_tempestade"], r["nome"])
        kp_max = round(float(res_oval["kp_max"]), 1)
        lat_oval = round(float(res_oval["latitude_oval_min"]), 1)
    except Exception as e:
        print(f"[{r['nome']}] ovalo auroral indisponivel: {e}")

    eventos_saida.append({
        "id": r["id"],
        "nome": r["nome"],
        "timestamps": [t.isoformat() for t in df.index],
        "dst_observado": [None if pd.isna(x) else round(float(x), 2) for x in df["Dst"].values],
        "dst_akasofu": [round(float(x), 2) for x in sim_ak],
        "dst_newell": [round(float(x), 2) for x in sim_nw],
        "corte_treino_teste": corte_ts,
        "tau_akasofu": round(float(r["tau_akasofu"]), 1), "escala_akasofu": float(r["escala_akasofu"]),
        "rmse_treino_akasofu": round(float(r["rmse_treino_akasofu"]), 2),
        "rmse_teste_akasofu": round(float(r["rmse_teste_akasofu"]), 2),
        "tau_newell": round(float(r["tau_newell"]), 1), "escala_newell": float(r["escala_newell"]),
        "rmse_treino_newell": round(float(r["rmse_treino_newell"]), 2),
        "rmse_teste_newell": round(float(r["rmse_teste_newell"]), 2),
        "ae_r2_akasofu": None if ae_ak.empty else round(float(ae_ak.iloc[0]), 3),
        "ae_r2_newell": None if ae_nw.empty else round(float(ae_nw.iloc[0]), 3),
        "kp_max": kp_max,
        "latitude_oval": lat_oval,
    })

with open("resultados.json", "w", encoding="utf-8") as f:
    json.dump({"eventos": eventos_saida}, f)

print("resultados.json gerado com sucesso (5 eventos, holdout genuino).")
