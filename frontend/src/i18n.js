import { ref } from "vue"

export const locale = ref("pt")

export function toggleLocale() {
  locale.value = locale.value === "pt" ? "en" : "pt"
}

export function formatarNumero(valor, casas = 2) {
  if (valor === null || valor === undefined) return "-"
  const loc = locale.value === "pt" ? "pt-BR" : "en-US"
  return Number(valor).toLocaleString(loc, { minimumFractionDigits: casas, maximumFractionDigits: casas })
}

const messages = {
  pt: {
    kicker: "Iniciação Científica · Geração Marte",
    titulo: "Acoplamento solar-magnetosfera",
    subtitulo: `Dois modelos de acoplamento vento solar, Akasofu épsilon e Newell et al. (2007),
      previstos contra o índice Dst em cinco tempestades geomagnéticas históricas, com
      validação genuína fora da amostra.`,
    carregando: "Carregando resultados...",
    erroPrefixo: "Não foi possível carregar os resultados",
    erroSufixo: "Confirma que o arquivo resultados.json está disponível.",
    resumoNumEventos: "tempestades com validação holdout 60/40",
    resumoRmseMedio: "RMSE médio do Dst fora da amostra",
    intervaloA: "a",
    resumoAe: "faixa de R² na previsão de AE (ajuste agrupado)",
    resumoOvalo: "eventos com latitude do ovalo auroral calculada",
    achadosTitulo: "O que os cinco eventos mostram",
    achado1Titulo: "Akasofu e Newell não têm um vencedor fixo",
    achado1Texto: `As duas funções convertem velocidade do vento solar e campo magnético interplanetário
      em uma taxa de energia injetada na magnetosfera; essa taxa entra na equação de Burton
      et al. (1975) para simular o Dst. No ajuste retrospectivo sobre os dois primeiros
      eventos, Newell teve erro menor que Akasofu (Gannon: 41,03 contra 49,41 nT; St.
      Patrick's: 21,78 contra 25,30 nT). Mas no holdout genuíno, calibrando só nos primeiros
      60% da janela e testando nos 40% finais nunca vistos pelo ajuste, essa ordem se inverte
      no Halloween Storm: Akasofu erra 151 nT contra 302 nT de Newell. A conclusão correta não
      é "Newell é melhor"; é que a função mais adequada depende do regime físico da
      tempestade, algo que só aparece ao testar vários eventos com holdout real.`,
    achado2Titulo: "AE e o ovalo auroral revelam uma saturação física, não um erro de dado",
    achado2Texto: `O Dst mede a corrente de anel, não a aurora em si; o índice AE (eletrojato auroral) é
      o proxy mais direto. A correlação entre a função de acoplamento e o AE caiu para
      praticamente zero no evento mais extremo (Gannon, R² ≈ 0,01) usando regressão linear.
      Isso bate com dois sinais independentes de saturação: o Kp bateu no teto da escala
      (9,0) e a latitude do ovalo auroral estimada chegou a ~45°, uma condição em que a
      relação padrão entre acoplamento e AE, calibrada para tempestades moderadas, deixa de
      valer. Trocar a regressão linear por log-log recuperou parte da correlação (Gannon:
      0,01 para 0,26). Para a previsão genuína fora da amostra, corrigimos também o atraso
      temporal entre o acoplamento e a resposta do eletrojato, e agrupamos o treino dos cinco
      eventos num único ajuste em vez de recalibrar do zero por tempestade; isso melhorou o
      R² de holdout em quatro dos cinco eventos. Ainda assim, a maioria continua negativa:
      a relação instantânea entre acoplamento e AE tem um limite físico real nos eventos
      mais extremos, e é isso que o resumo acima está mostrando.`,
    achado3Titulo: "Um experimento controlado contra overfitting",
    achado3Texto: `O solver usa um parâmetro de tempo de decaimento, tau, que originalmente era buscado
      entre 1h e 8h. Alargar esse limite para 24h deu ao otimizador mais liberdade, e o ajuste
      de treino melhorou, como qualquer modelo mais flexível melhora nos dados que já viu.
      Mas o erro no holdout piorou em todos os eventos testados com essa mudança: no Halloween
      Storm, o RMSE de teste do Akasofu subiu de 151 para 290 nT; no evento de agosto de 2011,
      o RMSE de teste do Newell subiu de 8,2 para 29,8 nT. Essa é a assinatura clássica de
      overfitting, um modelo que parece melhor e generaliza pior, e é a razão prática para
      manter o limite de 8h mesmo quando a otimização tenta empurrar tau para cima.`,
    achado4Titulo: "Detectar a janela de tempestade automaticamente: ajuda e atrapalha",
    achado4Texto: `Implementamos uma detecção automática do início e do fim de cada tempestade a partir
      do próprio Dst observado: o ponto de mínimo marca o pico, o início é o último instante
      de quietude antes dele, e o fim é quando o Dst recupera metade do déficit do pico. Nos
      cinco eventos, as janelas automáticas ficaram dentro de uma a três horas das escolhidas
      manualmente, mas o efeito no holdout foi desigual. Corrigiu o Halloween Storm, onde a
      janela manual era imprecisa (RMSE de teste do Newell caiu de 302 para 143 nT), e também
      ajudou St. Patrick's e agosto de 2011. Em compensação, piorou set/2017 ao encurtar
      demais a janela de teste, deixando poucos pontos para medir o erro (RMSE de 8,2 para
      26,6 nT). Por isso as janelas manuais seguem como resultado oficial; a detecção
      automática seria confiável como padrão só com uma duração mínima de teste garantida.`,
    metodologia: `Validação em cinco tempestades históricas: Gannon (maio/2024), St. Patrick's Day
      (março/2015), Halloween Storm (outubro/2003), set/2017 e ago/2011. Dados OMNI (NASA
      GSFC/SPDF), calibração por busca global (differential_evolution) usando
      60% da janela de tempestade como treino, erro medido nos 40% finais nunca vistos pelo
      ajuste. Uma suíte de testes automatizados (pytest) cobre o solver RK4 contra
      uma solução analítica, as funções de acoplamento e o ajuste de previsão de AE. Código
      completo e reprodutível no`,
    repositorio: "repositório",
    licencaBadge: "Licença: GPLv3",
    deployBadge: "Deploy: Vercel",
    dstObservado: "Dst observado",
    dstAxis: "Dst (nT)",
    calibradoLabel: "Calibrado",
    calibradoTexto1: "(treino) até",
    foraAmostraLabel: "fora da amostra",
    foraAmostraTexto: `(holdout/teste) a partir daí. Os parâmetros (tau, escala)
      usam só o período de treino; a diferença visual após o corte é o erro de previsão real.`,
    rmseTitulo: "Dst — RMSE (nT)",
    treino: "Treino",
    teste: "Teste",
    aeTitulo: "Previsão de AE (R² holdout, pooled)",
    ovaloTitulo: "Ovalo auroral",
    kpMaximo: "Kp máximo",
    latitudeEstimada: "Latitude estimada",
    ovaloIndisponivel: "Indisponível (sem cache local do Kp horário para este ano).",
    cenaLegendaPre: `Vento solar simulado (partículas violeta) chegando à magnetosfera; o ovalo e as
      cortinas reagem ao pico de Dst de`,
    cenaLegendaPos: ", a mesma intensidade que alimenta a calibração do modelo ao lado.",
  },
  en: {
    kicker: "Undergraduate Research · Geração Marte",
    titulo: "Solar wind–magnetosphere coupling",
    subtitulo: `Two solar wind coupling functions, Akasofu epsilon and Newell et al. (2007),
      tested against the Dst index across five historical geomagnetic storms, with genuine
      out-of-sample validation.`,
    carregando: "Loading results...",
    erroPrefixo: "Could not load the results",
    erroSufixo: "Make sure the resultados.json file is available.",
    resumoNumEventos: "storms with genuine 60/40 holdout validation",
    resumoRmseMedio: "average out-of-sample Dst RMSE",
    intervaloA: "to",
    resumoAe: "R² range for AE prediction (pooled fit)",
    resumoOvalo: "events with computed auroral oval latitude",
    achadosTitulo: "What the five events show",
    achado1Titulo: "Akasofu and Newell have no fixed winner",
    achado1Texto: `Both functions convert solar wind speed and interplanetary magnetic field into a
      rate of energy injected into the magnetosphere; that rate feeds the Burton et al.
      (1975) equation used to simulate Dst. In the retrospective fit on the first two events,
      Newell had a smaller error than Akasofu (Gannon: 41.03 vs 49.41 nT; St. Patrick's:
      21.78 vs 25.30 nT). But under genuine holdout, calibrating only on the first 60% of the
      window and testing on the final 40% never seen by the fit, that order flips in the
      Halloween Storm: Akasofu errs by 151 nT against Newell's 302 nT. The right conclusion
      isn't "Newell is better"; it's that the best-suited function depends on the storm's
      physical regime, something that only shows up when testing several events with real
      holdout.`,
    achado2Titulo: "AE and the auroral oval reveal a physical saturation, not a data error",
    achado2Texto: `Dst measures the ring current, not the aurora itself; the AE index (auroral
      electrojet) is the more direct proxy. The correlation between the coupling function and
      AE dropped to practically zero in the most extreme event (Gannon, R² ≈ 0.01) under
      linear regression. That matches two independent saturation signals: Kp hit the scale's
      ceiling (9.0) and the estimated auroral oval latitude reached ~45°, a regime where the
      standard coupling-to-AE relationship, calibrated for moderate storms, stops holding.
      Switching from linear to log-log regression recovered part of the correlation (Gannon:
      0.01 to 0.26). For the genuine out-of-sample forecast we also corrected the time lag
      between coupling and the electrojet's response, and pooled the training of all five
      events into a single fit instead of recalibrating from scratch per storm; that improved
      the holdout R² in four of the five events. Even so, most remain negative: the
      instantaneous coupling-to-AE relationship has a real physical ceiling in the most
      extreme events, and that's what the summary above is showing.`,
    achado3Titulo: "A controlled experiment against overfitting",
    achado3Texto: `The solver uses a decay time parameter, tau, originally searched between 1h and 8h.
      Widening that bound to 24h gave the optimizer more freedom, and the training fit
      improved, as any more flexible model does on data it has already seen. But holdout
      error got worse in every event tested with that change: in the Halloween Storm,
      Akasofu's test RMSE rose from 151 to 290 nT; in the August 2011 event, Newell's test
      RMSE rose from 8.2 to 29.8 nT. That's the classic signature of overfitting — a model
      that looks better and generalizes worse — and it's the practical reason for keeping the
      8h bound even when the optimizer keeps pushing tau upward.`,
    achado4Titulo: "Automatically detecting the storm window: helps and hurts",
    achado4Texto: `We implemented automatic detection of each storm's start and end directly from the
      observed Dst: the minimum point marks the peak, the start is the last quiet instant
      before it, and the end is when Dst recovers half of the peak deficit. Across the five
      events, the automatic windows landed within one to three hours of the manually chosen
      ones, but the effect on holdout was mixed. It fixed the Halloween Storm, where the
      manual window was imprecise (Newell's test RMSE dropped from 302 to 143 nT), and it
      also helped St. Patrick's and August 2011. On the other hand, it hurt September 2017 by
      shortening the test window too much, leaving too few points to measure the error (RMSE
      from 8.2 to 26.6 nT). That's why the manual windows remain the official result;
      automatic detection would only be reliable as a default with a guaranteed minimum test
      duration.`,
    metodologia: `Validation across five historical storms: Gannon (May 2024), St. Patrick's Day
      (March 2015), Halloween Storm (October 2003), Sep 2017 and Aug 2011. OMNI data (NASA
      GSFC/SPDF), calibration by global search (differential_evolution) using
      60% of the storm window as training, error measured on the final 40% never seen by the
      fit. An automated test suite (pytest) covers the RK4 solver against an
      analytical solution, the coupling functions, and the AE prediction fit. Full,
      reproducible code in the`,
    repositorio: "repository",
    licencaBadge: "License: GPLv3",
    deployBadge: "Deploy: Vercel",
    dstObservado: "Observed Dst",
    dstAxis: "Dst (nT)",
    calibradoLabel: "Calibrated",
    calibradoTexto1: "(training) up to",
    foraAmostraLabel: "out-of-sample",
    foraAmostraTexto: `(holdout/test) from that point on. The parameters (tau, scale) use only
      the training period; the visual difference after the cutoff is the real forecast error.`,
    rmseTitulo: "Dst — RMSE (nT)",
    treino: "Train",
    teste: "Test",
    aeTitulo: "AE prediction (pooled holdout R²)",
    ovaloTitulo: "Auroral oval",
    kpMaximo: "Max Kp",
    latitudeEstimada: "Estimated latitude",
    ovaloIndisponivel: "Unavailable (no local hourly Kp cache for this year).",
    cenaLegendaPre: `Simulated solar wind (violet particles) reaching the magnetosphere; the oval and
      curtains react to the Dst peak of`,
    cenaLegendaPos: ", the same intensity that feeds the model calibration alongside it.",
  },
}

export function t(key) {
  return messages[locale.value][key] ?? key
}

const nomesEventos = {
  gannon: { pt: "Gannon (mai/2024)", en: "Gannon (May 2024)" },
  stpatrick: { pt: "St. Patrick's Day (mar/2015)", en: "St. Patrick's Day (Mar 2015)" },
  halloween: { pt: "Halloween Storm (out/2003)", en: "Halloween Storm (Oct 2003)" },
  set2017: { pt: "Tempestade set/2017", en: "September 2017 Storm" },
  ago2011: { pt: "Tempestade ago/2011", en: "August 2011 Storm" },
}

export function nomeEvento(ev) {
  if (!ev) return ""
  const entrada = nomesEventos[ev.id]
  return entrada ? entrada[locale.value] : ev.nome
}

export const glossarioMeta = {
  titulo: { pt: "Conceitos e etapas do projeto", en: "Concepts and project stages" },
  subtitulo: { pt: "Clique em qualquer item pra expandir a explicação.", en: "Click any item to expand its explanation." },
}

export const glossario = [
  {
    id: "fisica",
    label: { pt: "Física", en: "Physics" },
    itens: [
      {
        titulo: { pt: "Índice Dst", en: "Dst index" },
        texto: {
          pt: "Mede a intensidade da corrente de anel, a corrente elétrica que circula ao redor da Terra durante uma tempestade geomagnética, enfraquecendo o campo magnético medido perto do equador. Quanto mais negativo, mais intensa a tempestade.",
          en: "Measures the strength of the ring current, the electric current circling Earth during a geomagnetic storm, which weakens the magnetic field measured near the equator. The more negative, the stronger the storm.",
        },
      },
      {
        titulo: { pt: "Índice AE", en: "AE index" },
        texto: {
          pt: "Mede a atividade do eletrojato auroral, as correntes elétricas na atmosfera polar alta que geram as auroras. É o proxy mais direto pra avaliar quanta energia do vento solar está chegando perto dos polos.",
          en: "Measures auroral electrojet activity, the currents in the upper polar atmosphere that generate auroras. It is the most direct proxy for how much solar wind energy is reaching the poles.",
        },
      },
      {
        titulo: { pt: "Índice Kp", en: "Kp index" },
        texto: {
          pt: "Índice global de 0 a 9 que resume a agitação geomagnética planetária a cada 3 horas. Usamos o Kp máximo de cada tempestade pra estimar até onde o ovalo auroral se expandiu.",
          en: "A global 0-9 index summarizing planetary geomagnetic disturbance every 3 hours. We use each storm's maximum Kp to estimate how far the auroral oval expanded.",
        },
      },
      {
        titulo: { pt: "Ovalo auroral", en: "Auroral oval" },
        texto: {
          pt: "Faixa ao redor dos polos magnéticos onde a aurora costuma aparecer. Em tempestades fortes ela se expande pra latitudes mais baixas, por isso auroras já foram vistas em latitudes incomuns durante eventos extremos.",
          en: "The band around the magnetic poles where auroras typically occur. In strong storms it expands toward lower latitudes, which is why auroras have been seen at unusual latitudes during extreme events.",
        },
      },
      {
        titulo: { pt: "Acoplamento vento solar-magnetosfera", en: "Solar wind-magnetosphere coupling" },
        texto: {
          pt: "Processo pelo qual energia do vento solar (plasma vindo do Sol) atravessa a magnetosfera terrestre, principalmente via reconexão magnética. As funções de acoplamento tentam estimar essa taxa de energia a partir de dados medidos no vento solar.",
          en: "The process by which energy from the solar wind (plasma streaming from the Sun) crosses Earth's magnetosphere, mainly through magnetic reconnection. Coupling functions try to estimate this energy rate from solar wind measurements.",
        },
      },
      {
        titulo: { pt: "Função de Akasofu (épsilon)", en: "Akasofu function (epsilon)" },
        texto: {
          pt: "Fórmula clássica (1981) que estima a taxa de energia acoplada a partir da velocidade do vento solar, do campo magnético interplanetário e do ângulo de orientação desse campo.",
          en: "A classic formula (1981) estimating the coupled energy rate from solar wind speed, the interplanetary magnetic field, and that field's orientation angle.",
        },
      },
      {
        titulo: { pt: "Função de Newell et al.", en: "Newell et al. function" },
        texto: {
          pt: "Versão mais recente (2007), ajustada estatisticamente contra dados reais de atividade geomagnética. Costuma captar melhor certos regimes de tempestade do que o Akasofu clássico.",
          en: "A more recent version (2007), statistically fitted against real geomagnetic activity data. It often captures certain storm regimes better than the classic Akasofu function.",
        },
      },
      {
        titulo: { pt: "Equação de Burton et al.", en: "Burton et al. equation" },
        texto: {
          pt: "Equação diferencial (1975) que descreve como o Dst evolui no tempo a partir da energia injetada e de um termo de decaimento da corrente de anel. É o modelo físico que o solver resolve numericamente.",
          en: "A differential equation (1975) describing how Dst evolves over time from injected energy and a decay term for the ring current. It is the physical model the solver integrates numerically.",
        },
      },
    ],
  },
  {
    id: "metodo",
    label: { pt: "Método", en: "Method" },
    itens: [
      {
        titulo: { pt: "Solver RK4", en: "RK4 solver" },
        texto: {
          pt: "Runge-Kutta de 4ª ordem: método numérico usado pra resolver a equação de Burton passo a passo no tempo. Foi validado contra uma solução analítica conhecida antes de rodar nos dados reais.",
          en: "4th-order Runge-Kutta: the numerical method used to step the Burton equation forward in time. Validated against a known analytical solution before running on real data.",
        },
      },
      {
        titulo: { pt: "Tau e escala", en: "Tau and scale" },
        texto: {
          pt: "Os dois parâmetros livres do modelo: tau é o tempo de decaimento da corrente de anel (quanto tempo a tempestade leva pra relaxar); escala converte a energia acoplada em variação de Dst. Ambos são ajustados pelos dados de cada tempestade.",
          en: "The model's two free parameters: tau is the ring current's decay time (how long the storm takes to relax); scale converts coupled energy into Dst change. Both are fit from each storm's data.",
        },
      },
      {
        titulo: { pt: "Calibração por busca global", en: "Global-search calibration" },
        texto: {
          pt: "Em vez de um método de gradiente que pode travar num mínimo local, usamos differential_evolution, um otimizador evolutivo que explora o espaço de parâmetros mais amplamente antes de convergir.",
          en: "Instead of a gradient method that can get stuck in a local minimum, we use differential_evolution, an evolutionary optimizer that explores the parameter space more broadly before converging.",
        },
      },
      {
        titulo: { pt: "Holdout 60/40", en: "60/40 holdout" },
        texto: {
          pt: "Os parâmetros são ajustados usando só os primeiros 60% da janela de cada tempestade; o erro reportado como teste vem dos 40% finais, nunca vistos pelo ajuste. Isso evita medir o modelo contra os próprios dados de treino.",
          en: "Parameters are fit using only the first 60% of each storm's window; the error reported as test comes from the final 40%, never seen by the fit. This avoids grading the model against its own training data.",
        },
      },
      {
        titulo: { pt: "RMSE", en: "RMSE" },
        texto: {
          pt: "Raiz do erro quadrático médio, em nT: mede o tamanho típico do erro entre o Dst previsto e o observado. Quanto menor, melhor.",
          en: "Root mean square error, in nT: measures the typical size of the error between predicted and observed Dst. Lower is better.",
        },
      },
      {
        titulo: { pt: "R² pooled", en: "Pooled R²" },
        texto: {
          pt: "Mede o quanto a relação entre acoplamento e AE, ajustada em conjunto nos cinco eventos, explica a variação observada em cada evento individual. R² negativo significa que o ajuste conjunto prevê pior do que simplesmente usar a média.",
          en: "Measures how much the coupling-to-AE relationship, fit jointly across the five events, explains the variation observed in each individual event. A negative R² means the pooled fit predicts worse than just using the average.",
        },
      },
    ],
  },
  {
    id: "pipeline",
    label: { pt: "Pipeline", en: "Pipeline" },
    itens: [
      {
        titulo: { pt: "Ingestão de dados (OMNI)", en: "Data ingestion (OMNI)" },
        texto: {
          pt: "Dados de vento solar e campo magnético interplanetário, em resolução de 1 minuto, baixados da base OMNI (NASA GSFC/SPDF) em formato CDF pra cada uma das cinco tempestades.",
          en: "Solar wind and interplanetary magnetic field data, at 1-minute resolution, downloaded from the OMNI database (NASA GSFC/SPDF) in CDF format for each of the five storms.",
        },
      },
      {
        titulo: { pt: "Solver e calibração (Python)", en: "Solver and calibration (Python)" },
        texto: {
          pt: "O núcleo numérico (RK4 + Burton), as duas funções de acoplamento e a calibração com holdout genuíno foram implementados em Python, com testes automatizados (pytest) cobrindo o solver contra uma solução analítica.",
          en: "The numerical core (RK4 + Burton), the two coupling functions, and the genuine-holdout calibration were implemented in Python, with automated tests (pytest) covering the solver against an analytical solution.",
        },
      },
      {
        titulo: { pt: "Análise de AE e ovalo auroral", en: "AE and auroral oval analysis" },
        texto: {
          pt: "Camada adicional que relaciona a função de acoplamento ao índice AE (regressão pooled com atraso temporal) e estima a latitude do ovalo auroral a partir do Kp máximo de cada tempestade.",
          en: "An additional layer relating the coupling function to the AE index (pooled regression with time lag) and estimating the auroral oval's latitude from each storm's maximum Kp.",
        },
      },
      {
        titulo: { pt: "Visualização (Vue 3 + Three.js)", en: "Visualization (Vue 3 + Three.js)" },
        texto: {
          pt: "O front consome o resultados.json gerado pelo backend e exibe: gráficos Dst observado vs. modelado (Chart.js), métricas de RMSE/R²/ovalo por evento, e uma cena 3D (Three.js) que reage à intensidade de cada tempestade.",
          en: "The front end consumes the resultados.json produced by the backend and displays: observed vs. modeled Dst charts (Chart.js), per-event RMSE/R²/oval metrics, and a 3D scene (Three.js) that reacts to each storm's intensity.",
        },
      },
    ],
  },
]



