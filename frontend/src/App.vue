<script setup>
import { ref, computed, onMounted } from "vue"
import AuroraScene from "./components/AuroraScene.vue"
import ResultsPanel from "./components/ResultsPanel.vue"
import { locale, toggleLocale, t, nomeEvento } from "./i18n.js"
import ConceptsGlossary from "./components/ConceptsGlossary.vue"

const eventos = ref([])
const eventoAtivoId = ref(null)
const carregando = ref(true)
const erro = ref(null)

async function carregar() {
  try {
    const resp = await fetch("/resultados.json")
    if (!resp.ok) throw new Error("Falha ao buscar resultados")
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
      <p class="kicker">{{ t("kicker") }}</p>
      <div class="header-top">
        <h1>{{ t("titulo") }}</h1>
        <button
          class="lang-toggle"
          @click="toggleLocale"
          :aria-label="locale === 'pt' ? 'Switch to English' : 'Mudar para português'"
        >
          {{ locale === "pt" ? "EN" : "PT" }}
        </button>
      </div>
      <p class="subtitulo">{{ t("subtitulo") }}</p>
    </header>

    <div v-if="carregando" class="estado">{{ t("carregando") }}</div>
    <div v-else-if="erro" class="estado erro">
      {{ t("erroPrefixo") }} ({{ erro }}). {{ t("erroSufixo") }}
    </div>

    <template v-else>
      <section class="resumo" v-if="stats">
        <div class="metrica-resumo">
          <span class="numero">{{ stats.numEventos }}</span>
          <span class="legenda">{{ t("resumoNumEventos") }}</span>
        </div>
        <div class="metrica-resumo">
          <span class="numero">{{ stats.rmseMedio }} nT</span>
          <span class="legenda">{{ t("resumoRmseMedio") }}</span>
        </div>
        <div class="metrica-resumo">
          <span class="numero">{{ stats.aeMin }} {{ t("intervaloA") }} {{ stats.aeMax }}</span>
          <span class="legenda">{{ t("resumoAe") }}</span>
        </div>
        <div class="metrica-resumo">
          <span class="numero">{{ stats.comOvalo }}/{{ stats.numEventos }}</span>
          <span class="legenda">{{ t("resumoOvalo") }}</span>
        </div>
      </section>

      <nav class="tabs">
        <button
          v-for="ev in eventos"
          :key="ev.id"
          :class="{ ativo: ev.id === eventoAtivoId }"
          @click="eventoAtivoId = ev.id"
        >
          {{ nomeEvento(ev) }}
        </button>
      </nav>

      <main class="layout">
        <AuroraScene :evento="eventoAtivo()" />
        <ResultsPanel :evento="eventoAtivo()" />
      </main>

      <section class="achados">
        <h2>{{ t("achadosTitulo") }}</h2>

        <article class="achado achado-neutro">
          <h3>{{ t("achado1Titulo") }}</h3>
          <p>{{ t("achado1Texto") }}</p>
        </article>

        <article class="achado achado-fisica">
          <h3>{{ t("achado2Titulo") }}</h3>
          <p>{{ t("achado2Texto") }}</p>
        </article>

        <article class="achado achado-metodo">
          <h3>{{ t("achado3Titulo") }}</h3>
          <p>{{ t("achado3Texto") }}</p>
        </article>

        <article class="achado achado-misto">
          <h3>{{ t("achado4Titulo") }}</h3>
          <p>{{ t("achado4Texto") }}</p>
        </article>
      </section>

      <ConceptsGlossary />

      <footer class="metodologia">
        <p>
          {{ t("metodologia") }}
          <a href="https://github.com/Guilherme-Bernal/GeracaoMartece-IC" target="_blank" rel="noopener">{{ t("repositorio") }}</a>.
        </p>
        <div class="badges">
          <a class="badge" href="https://github.com/Guilherme-Bernal/GeracaoMartece-IC" target="_blank" rel="noopener">
            <span class="dot dot-github"></span>GitHub
          </a>
          <span class="badge"><span class="dot dot-license"></span>{{ t("licencaBadge") }}</span>
          <span class="badge"><span class="dot dot-deploy"></span>{{ t("deployBadge") }}</span>
        </div>
      </footer>
    </template>
  </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap");

.app {
  max-width: 1080px;
  margin: 0 auto;
  padding: 48px 24px 72px;
  font-family: "Inter", system-ui, sans-serif;
  color: #e7ecf6;
  background: radial-gradient(ellipse 1200px 500px at 50% -10%, rgba(61,220,132,0.07), transparent 60%), #0a0e1a;
}
.kicker {
  font-family: "IBM Plex Mono", monospace; font-size: 12px; color: #3ddc84;
  letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 10px;
}
.header-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
header h1 {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 34px;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
}
.lang-toggle {
  background: transparent; border: 1px solid rgba(231,236,246,0.22); color: #c3c9db;
  padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 12.5px;
  font-family: "IBM Plex Mono", monospace; letter-spacing: 0.04em;
  transition: border-color 0.15s, color 0.15s; flex-shrink: 0;
}
.lang-toggle:hover { border-color: #3ddc84; color: #3ddc84; }
.subtitulo { color: #8a93ab; margin: 10px 0 0; max-width: 62ch; line-height: 1.6; font-size: 15px; }

.estado { margin-top: 40px; color: #8a93ab; }
.estado.erro { color: #ef6461; }

.resumo {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 14px; margin-top: 36px;
}
.metrica-resumo {
  padding: 20px 22px; display: flex; flex-direction: column; gap: 6px;
  background: linear-gradient(180deg, rgba(231,236,246,0.045), rgba(231,236,246,0.01));
  border: 1px solid rgba(231,236,246,0.1);
  border-radius: 10px;
  transition: border-color 0.18s, transform 0.18s;
}
.metrica-resumo:hover { border-color: rgba(61,220,132,0.4); transform: translateY(-2px); }
.metrica-resumo .numero { font-family: "IBM Plex Mono", monospace; font-size: 22px; color: #3ddc84; }
.metrica-resumo .legenda { font-size: 12.5px; color: #8a93ab; line-height: 1.4; }

.tabs { display: flex; gap: 8px; margin-top: 28px; flex-wrap: wrap; }
.tabs button {
  background: transparent; border: 1px solid rgba(231,236,246,0.14);
  color: #c3c9db; padding: 9px 18px; border-radius: 999px;
  cursor: pointer; font-size: 13.5px; font-family: "Inter", sans-serif;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}
.tabs button.ativo { border-color: #3ddc84; color: #3ddc84; background: rgba(61,220,132,0.1); }
.tabs button:hover:not(.ativo) { border-color: rgba(231,236,246,0.32); }

.layout {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;
}
@media (max-width: 760px) { .layout { grid-template-columns: 1fr; } }

.achados { margin-top: 52px; display: flex; flex-direction: column; gap: 4px; }
.achados h2 {
  font-family: "Source Serif 4", Georgia, serif; font-size: 22px; font-weight: 600;
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
.metodologia code { font-family: "IBM Plex Mono", monospace; color: #c3c9db; }

.badges { display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap; }
.badge {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 6px 13px; border-radius: 999px;
  border: 1px solid rgba(231,236,246,0.14);
  background: rgba(231,236,246,0.03);
  color: #8a93ab; font-size: 12px; font-family: "IBM Plex Mono", monospace;
  text-decoration: none; transition: border-color 0.15s, color 0.15s;
}
a.badge:hover { border-color: #3ddc84; color: #3ddc84; }
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-github { background: #c3c9db; }
.dot-license { background: #9b8cff; }
.dot-deploy { background: #3ddc84; }
</style>
