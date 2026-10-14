<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({ evento: Object })
const canvas = ref(null)
let chart

function formatarData(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function montarGrafico() {
  if (!props.evento) return
  const ev = props.evento
  const labels = ev.timestamps.map(t => t.slice(5, 16).replace('T', ' '))

  if (chart) chart.destroy()
  chart = new Chart(canvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Dst observado', data: ev.dst_observado, borderColor: '#f87171', borderWidth: 1.5, pointRadius: 0 },
        { label: 'Akasofu', data: ev.dst_akasofu, borderColor: '#60a5fa', borderWidth: 1.5, pointRadius: 0 },
        { label: 'Newell', data: ev.dst_newell, borderColor: '#4ade80', borderWidth: 1.5, pointRadius: 0 },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { maxTicksLimit: 6, color: '#8b93ab' }, grid: { color: 'rgba(232,236,245,0.06)' } },
        y: { ticks: { color: '#8b93ab' }, grid: { color: 'rgba(232,236,245,0.06)' }, title: { display: true, text: 'Dst (nT)', color: '#8b93ab' } },
      },
      plugins: { legend: { labels: { color: '#e8ecf5' } } },
    },
  })
}

onMounted(montarGrafico)
watch(() => props.evento, montarGrafico)
onBeforeUnmount(() => chart?.destroy())
</script>

<template>
  <div class="painel" v-if="evento">
    <div class="grafico"><canvas ref="canvas"></canvas></div>

    <p class="corte" v-if="evento.corte_treino_teste">
      <strong>Calibrado</strong> (treino) até {{ formatarData(evento.corte_treino_teste) }};
      <strong>fora da amostra</strong> (holdout/teste) a partir daí. Os parâmetros (tau, escala)
      usam só o período de treino; a diferença visual após o corte é o erro de previsão real.
    </p>

    <div class="metricas-grid">
      <div class="bloco">
        <h4>Dst — RMSE (nT)</h4>
        <table>
          <thead><tr><th></th><th>Treino</th><th>Teste</th></tr></thead>
          <tbody>
            <tr><td>Akasofu</td><td>{{ evento.rmse_treino_akasofu.toFixed(2) }}</td><td class="destaque">{{ evento.rmse_teste_akasofu.toFixed(2) }}</td></tr>
            <tr><td>Newell</td><td>{{ evento.rmse_treino_newell.toFixed(2) }}</td><td class="destaque">{{ evento.rmse_teste_newell.toFixed(2) }}</td></tr>
          </tbody>
        </table>
      </div>

      <div class="bloco">
        <h4>Previsão de AE (R² holdout, pooled)</h4>
        <table>
          <tbody>
            <tr><td>Akasofu</td><td :class="{ destaque: evento.ae_r2_akasofu > 0 }">{{ evento.ae_r2_akasofu ?? '-' }}</td></tr>
            <tr><td>Newell</td><td :class="{ destaque: evento.ae_r2_newell > 0 }">{{ evento.ae_r2_newell ?? '-' }}</td></tr>
          </tbody>
        </table>
      </div>

      <div class="bloco" v-if="evento.kp_max !== null">
        <h4>Ovalo auroral</h4>
        <table>
          <tbody>
            <tr><td>Kp máximo</td><td>{{ evento.kp_max }}</td></tr>
            <tr><td>Latitude estimada</td><td>{{ evento.latitude_oval }}°</td></tr>
          </tbody>
        </table>
      </div>
      <div class="bloco indisponivel" v-else>
        <h4>Ovalo auroral</h4>
        <p>Indisponível (sem cache local do Kp horário para este ano).</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.painel {
  background: #121a2e; border: 1px solid rgba(232,236,245,0.1);
  border-radius: 14px; padding: 16px; display: flex; flex-direction: column; gap: 14px;
}
.grafico { height: 280px; position: relative; }
.corte { font-size: 12px; color: #8b93ab; line-height: 1.5; margin: 0; }
.metricas-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.bloco { background: #0a0e1a; border-radius: 10px; padding: 10px 12px; }
.bloco h4 { font-size: 11px; color: #8b93ab; text-transform: uppercase; letter-spacing: .05em; margin: 0 0 8px; }
.bloco table { width: 100%; border-collapse: collapse; font-size: 13px; }
.bloco td { padding: 3px 0; }
.bloco td.destaque { color: #4ade80; font-family: 'IBM Plex Mono', monospace; }
.bloco.indisponivel p { font-size: 12px; color: #5b6376; margin: 0; }
</style>

