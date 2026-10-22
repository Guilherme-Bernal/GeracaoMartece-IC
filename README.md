# GeracaoMartece-IC

🌐 **[Read in English](README.en.md)**

Iniciação Científica em astrofísica computacional: modelagem do acoplamento entre o vento solar e a magnetosfera terrestre e sua relação com a ocorrência de auroras boreais.

🔗 **Site ao vivo:** https://geracao-martece-ic.vercel.app

## Sobre o projeto

Investigamos como a energia do vento solar é transferida para a magnetosfera da Terra durante tempestades geomagnéticas, usando funções de acoplamento clássicas da literatura (Akasofu, 1981; Newell et al., 2007) integradas à equação empírica de Burton et al. (1975) via Runge-Kutta de 4ª ordem.

O ponto central do trabalho é a validação estatística honesta: em vez de ajustar o modelo e medir o erro nos mesmos dados (fitting retrospectivo), calibramos cada evento apenas com os primeiros 60% da janela temporal e medimos o erro (RMSE) nos 40% finais — dados que o otimizador nunca viu. Esse protocolo de holdout genuíno foi replicado em cinco tempestades geomagnéticas históricas de intensidades bem diferentes:

- Halloween Storm (out/2003)
- Tempestade de ago/2011
- St. Patrick's Day (mar/2015)
- Tempestade de set/2017
- Gannon Storm (mai/2024)

Também avaliamos a correlação entre a taxa de acoplamento e o índice AE (eletrojato auroral) de forma agrupada (pooled) entre os cinco eventos, e estimamos a expansão do ovalo auroral em latitude a partir do Kp derivado do Dst modelado.

## Estrutura do repositório

```
geracaomartece-ic/
├── python/          # Pipeline científico: ingestão, acoplamento, solver RK4, calibração, previsão, aurora
├── backend/         # API FastAPI que serve os resultados pré-calculados (resultados.json) para o frontend
├── frontend/        # Site em Vue 3 + Three.js + Chart.js, com i18n PT/EN
├── core/            # Núcleo experimental em Rust (ode_solvers) — em desenvolvimento
├── notebooks/       # Notebooks Jupyter com o pipeline completo e exploração dos dados
└── tests/           # Testes automatizados (pytest) do pipeline Python
```

## Dados

Os dados de vento solar, campo magnético interplanetário (IMF) e índices geomagnéticos (Dst, AE, Kp) vêm da base **OMNI** (NASA GSFC/SPDF), obtidos em resolução de 1 minuto via `pyspedas`.

## Tecnologias

**Ciência e computação**
- Python — NumPy, Pandas, SciPy (`differential_evolution` para calibração global)
- Solver Runge-Kutta de 4ª ordem (passo fixo, 60s)
- pytest para testes automatizados

**Backend**
- FastAPI servindo os resultados pré-processados

**Frontend**
- Vue 3 (`<script setup>`)
- Three.js — cena 3D do ovalo auroral
- Chart.js — séries temporais de Dst
- i18n nativo (PT/EN), sem biblioteca externa
- Deploy via Vercel

## Como executar

### Backend

```powershell
cd backend
pip install fastapi uvicorn
uvicorn main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Testes

```powershell
pip install pytest
pytest tests/
```

## Autores

- Guilherme Savassa Bernal
- Luiny Beatriz dos Santos Pinto

Orientação: Clari

## Licença

Veja o arquivo [LICENSE](LICENSE).