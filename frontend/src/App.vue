<script setup>
import { ref, computed, onMounted } from 'vue'
import AuroraScene from './components/AuroraScene.vue'
import ResultsPanel from './components/ResultsPanel.vue'

const eventos = ref([])
const eventoAtivoId = ref(null)
const carregando = ref(true)
const erro = ref(null)

async function carregar() {
  try {
    const resp = await fetch('./resultados.json')
    if (!resp.ok) throw new Error('Falha ao buscar resultados')
    const dados = await resp.json()
    eventos.value = dados.eventos
    eventoAtivoId.value = dados.eventos[0]?.id ?? null
  } catch (e) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
}

onMounted(carregar)

function eventoAtivo() {
  return eventos.value.find(ev => ev.id === eventoAtivoId.value)
}

const stats = computed(() => {
  if (!eventos.value.length) return null
  const ae = eventos.value.flatMap(ev => [ev.ae_r2_akasofu, ev.ae_r2_newell]).filter(v => v !== null && v !== undefined)
  const rmseTeste = eventos.value.flatMap(ev => [ev.rmse_teste_akasofu, ev.rmse_teste_newell])
  return {
    numEventos: eventos.value.length,
    aeMin: Math.min(...ae).toFixed(2),
    aeMax: Math.max(...ae).toFixed(2),
    rmseMedio: (rmseTeste.reduce((a, b) => a + b, 0) / rmseTeste.length).toFixed(1),
    comOvalo: eventos.value.filter(ev => ev.kp_max !== null).length,
  }
})
</script>

<template>
  <div class="app">
    <header>
      <h1>Acoplamento solar-magnetosfera</h1>
      <p class="subtitulo">
        Dois modelos de acoplamento vento solar, Akasofu épsilon e Newell et al. (2007),
        previstos contra o índice Dst em cinco tempestades geomagnéticas históricas, com
        validação genuína fora da amostra.
      </p>
    </header>

    <div v-if="carregando" class="estado">Carregando resultados...</div>
    <div v-else-if="erro" class="estado erro">
      Não foi possível conectar à API ({{ erro }}). Confirma que o backend está rodando em
      <code>http://localhost:8000</code>.
    </div>

    <template v-else>
      <section class="resumo" v-if="stats">
        <div class="metrica-resumo">
          <span class="numero">{{ stats.numEventos }}</span>
          <span class="legenda">tempestades com validação holdout 60/40</span>
        </div>
        <div class="metrica-resumo">
          <span class="numero">{{ stats.rmseMedio }} nT</span>
          <span class="legenda">RMSE médio do Dst fora da amostra</span>
        </div>
        <div class="metrica-resumo">
          <span class="numero">{{ stats.aeMin }} a {{ stats.aeMax }}</span>
          <span class="legenda">faixa de R² na previsão de AE (ajuste agrupado)</span>
        </div>
        <div class="metrica-resumo">
          <span class="numero">{{ stats.comOvalo }}/{{ stats.numEventos }}</span>
          <span class="legenda">eventos com latitude do ovalo auroral calculada</span>
        </div>
      </section>

      <nav class="tabs">
        <button
          v-for="ev in eventos"
          :key="ev.id"
          :class="{ ativo: ev.id === eventoAtivoId }"
          @click="eventoAtivoId = ev.id"
        >
          {{ ev.nome }}
        </button>
      </nav>

      <main class="layout">
        <AuroraScene :evento="eventoAtivo()" />
        <ResultsPanel :evento="eventoAtivo()" />
      </main>

      <section class="achados">
        <h2>O que os cinco eventos mostram</h2>

        <article class="achado achado-neutro">
          <h3>Akasofu e Newell não têm um vencedor fixo</h3>
          <p>
            As duas funções convertem velocidade do vento solar e campo magnético interplanetário
            em uma taxa de energia injetada na magnetosfera; essa taxa entra na equação de Burton
            et al. (1975) para simular o Dst. No ajuste retrospectivo sobre os dois primeiros
            eventos, Newell teve erro menor que Akasofu (Gannon: 41,03 contra 49,41 nT; St.
            Patrick's: 21,78 contra 25,30 nT). Mas no holdout genuíno, calibrando só nos primeiros
            60% da janela e testando nos 40% finais nunca vistos pelo ajuste, essa ordem se inverte
            no Halloween Storm: Akasofu erra 151 nT contra 302 nT de Newell. A conclusão correta não
            é "Newell é melhor"; é que a função mais adequada depende do regime físico da
            tempestade, algo que só aparece ao testar vários eventos com holdout real.
          </p>
        </article>

        <article class="achado achado-fisica">
          <h3>AE e o ovalo auroral revelam uma saturação física, não um erro de dado</h3>
          <p>
            O Dst mede a corrente de anel, não a aurora em si; o índice AE (eletrojato auroral) é
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
            mais extremos, e é isso que o resumo acima está mostrando.
          </p>
        </article>

        <article class="achado achado-metodo">
          <h3>Um experimento controlado contra overfitting</h3>
          <p>
            O solver usa um parâmetro de tempo de decaimento, tau, que originalmente era buscado
            entre 1h e 8h. Alargar esse limite para 24h deu ao otimizador mais liberdade, e o ajuste
            de treino melhorou, como qualquer modelo mais flexível melhora nos dados que já viu.
            Mas o erro no holdout piorou em todos os eventos testados com essa mudança: no Halloween
            Storm, o RMSE de teste do Akasofu subiu de 151 para 290 nT; no evento de agosto de 2011,
            o RMSE de teste do Newell subiu de 8,2 para 29,8 nT. Essa é a assinatura clássica de
            overfitting, um modelo que parece melhor e generaliza pior, e é a razão prática para
            manter o limite de 8h mesmo quando a otimização tenta empurrar tau para cima.
          </p>
        </article>

        <article class="achado achado-misto">
          <h3>Detectar a janela de tempestade automaticamente: ajuda e atrapalha</h3>
          <p>
            Implementamos uma detecção automática do início e do fim de cada tempestade a partir
            do próprio Dst observado: o ponto de mínimo marca o pico, o início é o último instante
            de quietude antes dele, e o fim é quando o Dst recupera metade do déficit do pico. Nos
            cinco eventos, as janelas automáticas ficaram dentro de uma a três horas das escolhidas
            manualmente, mas o efeito no holdout foi desigual. Corrigiu o Halloween Storm, onde a
            janela manual era imprecisa (RMSE de teste do Newell caiu de 302 para 143 nT), e também
            ajudou St. Patrick's e agosto de 2011. Em compensação, piorou set/2017 ao encurtar
            demais a janela de teste, deixando poucos pontos para medir o erro (RMSE de 8,2 para
            26,6 nT). Por isso as janelas manuais seguem como resultado oficial; a detecção
            automática seria confiável como padrão só com uma duração mínima de teste garantida.
          </p>
        </article>
      </section>

      <footer class="metodologia">
        <p>
          Validação em cinco tempestades históricas: Gannon (maio/2024), St. Patrick's Day
          (março/2015), Halloween Storm (outubro/2003), set/2017 e ago/2011. Dados OMNI (NASA
          GSFC/SPDF), calibração por busca global (<code>differential_evolution</code>) usando
          60% da janela de tempestade como treino, erro medido nos 40% finais nunca vistos pelo
          ajuste. Uma suíte de testes automatizados (<code>pytest</code>) cobre o solver RK4 contra
          uma solução analítica, as funções de acoplamento e o ajuste de previsão de AE. Código
          completo e reprodutível no
          <a href="https://github.com/Guilherme-Bernal/GeracaoMartece-IC" target="_blank" rel="noopener">repositório</a>.
        </p>
      </footer>
    </template>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

.app {
  max-width: 1080px;
  margin: 0 auto;
  padding: 48px 24px 72px;
  font-family: 'Inter', system-ui, sans-serif;
  color: #e7ecf6;
  background: #0a0e1a;
}
header h1 {
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 34px;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
}
.subtitulo { color: #8a93ab; margin: 10px 0 0; max-width: 62ch; line-height: 1.6; font-size: 15px; }

.estado { margin-top: 40px; color: #8a93ab; }
.estado.erro { color: #ef6461; }

.resumo {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0; margin-top: 36px;
  border-top: 1px solid rgba(231,236,246,0.12);
  border-bottom: 1px solid rgba(231,236,246,0.12);
}
.metrica-resumo {
  padding: 18px 20px; display: flex; flex-direction: column; gap: 6px;
  border-left: 1px solid rgba(231,236,246,0.12);
}
.metrica-resumo:first-child { border-left: none; }
.metrica-resumo .numero { font-family: 'IBM Plex Mono', monospace; font-size: 22px; color: #3ddc84; }
.metrica-resumo .legenda { font-size: 12.5px; color: #8a93ab; line-height: 1.4; }

.tabs { display: flex; gap: 8px; margin-top: 28px; flex-wrap: wrap; }
.tabs button {
  background: transparent; border: 1px solid rgba(231,236,246,0.14);
  color: #c3c9db; padding: 9px 16px; border-radius: 4px;
  cursor: pointer; font-size: 13.5px; font-family: 'Inter', sans-serif;
  transition: border-color 0.15s, color 0.15s;
}
.tabs button.ativo { border-color: #3ddc84; color: #3ddc84; }
.tabs button:hover:not(.ativo) { border-color: rgba(231,236,246,0.32); }

.layout {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;
}
@media (max-width: 760px) { .layout { grid-template-columns: 1fr; } }

.achados { margin-top: 52px; display: flex; flex-direction: column; gap: 4px; }
.achados h2 {
  font-family: 'Source Serif 4', Georgia, serif; font-size: 22px; font-weight: 600;
  margin: 0 0 20px;
}
.achado {
  padding: 18px 0 22px 20px; border-left: 2px solid rgba(231,236,246,0.14);
  border-top: 1px solid rgba(231,236,246,0.08);
}
.achado:first-of-type { border-top: none; }
.achado-fisica { border-left-color: #3ddc84; }
.achado-metodo { border-left-color: #9b8cff; }
.achado-misto { border-left-color: #e8b04b; }
.achado h3 { font-size: 15.5px; font-weight: 600; margin: 0 0 10px; color: #e7ecf6; }
.achado p { font-size: 14px; line-height: 1.7; color: #b5bccf; margin: 0; max-width: 72ch; }

.metodologia {
  margin-top: 44px; padding-top: 20px; border-top: 1px solid rgba(231,236,246,0.12);
}
.metodologia p { font-size: 12.5px; color: #8a93ab; line-height: 1.7; margin: 0; }
.metodologia a { color: #3ddc84; }
.metodologia code { font-family: 'IBM Plex Mono', monospace; color: #c3c9db; }
</style>

