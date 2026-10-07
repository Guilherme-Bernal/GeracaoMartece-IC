<script setup>
import { ref, onMounted } from 'vue'
import AuroraScene from './components/AuroraScene.vue'
import ResultsPanel from './components/ResultsPanel.vue'

const eventos = ref([])
const eventoAtivoId = ref(null)
const carregando = ref(true)
const erro = ref(null)

async function carregar() {
  try {
    const resp = await fetch('http://localhost:8000/api/resultados')
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
</script>

<template>
  <div class="app">
    <header>
      <h1>Acoplamento Solar-Magnetosfera</h1>
      <p class="subtitulo">Newell vs. Akasofu - previsao do indice Dst</p>
    </header>

    <div v-if="carregando" class="estado">Carregando resultados...</div>
    <div v-else-if="erro" class="estado erro">
      Nao foi possivel conectar a API ({{ erro }}). Confirma que o backend esta rodando em
      <code>http://localhost:8000</code>.
    </div>

    <template v-else>
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
    </template>
  </div>
</template>

<style scoped>
.app {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 20px 64px;
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
  color: #e8ecf5;
}
header h1 { font-size: 28px; margin: 0; }
.subtitulo { color: #8b93ab; margin: 6px 0 0; }
.estado { margin-top: 40px; color: #8b93ab; }
.estado.erro { color: #f87171; }
.tabs { display: flex; gap: 10px; margin-top: 28px; flex-wrap: wrap; }
.tabs button {
  background: #121a2e; border: 1px solid rgba(232,236,245,0.1);
  color: #e8ecf5; padding: 10px 16px; border-radius: 10px;
  cursor: pointer; font-size: 14px;
}
.tabs button.ativo { border-color: #6ee7b7; color: #6ee7b7; }
.layout {
  display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px;
}
@media (max-width: 760px) { .layout { grid-template-columns: 1fr; } }
</style>
