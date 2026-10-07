<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({ evento: Object })
const canvas = ref(null)
let chart

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
    <div class="metricas">
      <div class="metrica">
        <span class="rotulo">Akasofu RMSE</span>
        <span class="valor">{{ evento.rmse_akasofu.toFixed(2) }} nT</span>
      </div>
      <div class="metrica destaque">
        <span class="rotulo">Newell RMSE</span>
        <span class="valor">{{ evento.rmse_newell.toFixed(2) }} nT</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.painel {
  background: #121a2e; border: 1px solid rgba(232,236,245,0.1);
  border-radius: 14px; padding: 16px; display: flex; flex-direction: column; gap: 16px;
}
.grafico { height: 280px; position: relative; }
.metricas { display: flex; gap: 12px; }
.metrica {
  flex: 1; background: #0a0e1a; border-radius: 10px; padding: 12px 14px;
  display: flex; flex-direction: column; gap: 4px;
}
.metrica.destaque { outline: 1px solid #4ade80; }
.rotulo { font-size: 11px; color: #8b93ab; text-transform: uppercase; letter-spacing: .06em; }
.valor { font-family: 'IBM Plex Mono', monospace; font-size: 20px; }
</style>
