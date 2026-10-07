import sys
import json
sys.path.insert(0, "../python")

import pandas as pd
from ingestao import rodar_pipeline_tempestade
from solver import simular_burton_rk4
from acoplamento import akasofu_epsilon, newell_coupling

eventos_config = [
    {
        "id": "gannon",
        "nome": "Gannon (mai/2024)",
        "trange": ["2024-05-10", "2024-05-12"],
        "inicio": "2024-05-10 16:00",
        "fim": "2024-05-11 12:00",
    },
    {
        "id": "stpatrick",
        "nome": "St. Patrick's Day (mar/2015)",
        "trange": ["2015-03-17", "2015-03-19"],
        "inicio": "2015-03-17 04:00",
        "fim": "2015-03-18 00:00",
    },
]

resultados = []
for cfg in eventos_config:
    r = rodar_pipeline_tempestade(
        nome_evento=cfg["nome"],
        trange=cfg["trange"],
        inicio_tempestade=pd.Timestamp(cfg["inicio"]),
        fim_tempestade=pd.Timestamp(cfg["fim"]),
    )
    df = r["df"]
    dt = 60.0
    dst0 = df["Dst"].iloc[0]

    Q_ak = akasofu_epsilon(df["V"].values, df["By"].values, df["Bz"].values)
    Q_nw = newell_coupling(df["V"].values, df["By"].values, df["Bz"].values)

    sim_ak = simular_burton_rk4(Q_ak, dst0, r["tau_akasofu"], r["escala_akasofu"], dt)
    sim_nw = simular_burton_rk4(Q_nw, dst0, r["tau_newell"], r["escala_newell"], dt)

    resultados.append({
        "id": cfg["id"],
        "nome": cfg["nome"],
        "timestamps": [t.isoformat() for t in df.index],
        "dst_observado": [None if pd.isna(x) else round(float(x), 2) for x in df["Dst"].values],
        "dst_akasofu": [round(float(x), 2) for x in sim_ak],
        "dst_newell": [round(float(x), 2) for x in sim_nw],
        "tau_akasofu": r["tau_akasofu"],
        "escala_akasofu": r["escala_akasofu"],
        "rmse_akasofu": r["rmse_akasofu"],
        "tau_newell": r["tau_newell"],
        "escala_newell": r["escala_newell"],
        "rmse_newell": r["rmse_newell"],
    })

with open("resultados.json", "w", encoding="utf-8") as f:
    json.dump({"eventos": resultados}, f)

print("resultados.json gerado com sucesso.")
