<script setup>
import { ref } from "vue"
import { locale, glossarioMeta, glossario } from "../i18n.js"

const categoriaAtiva = ref(glossario[0].id)
const abertos = ref(new Set())

function chave(catId, idx) {
  return `${catId}-${idx}`
}

function alternar(catId, idx) {
  const k = chave(catId, idx)
  const novo = new Set(abertos.value)
  if (novo.has(k)) novo.delete(k)
  else novo.add(k)
  abertos.value = novo
}

function estaAberto(catId, idx) {
  return abertos.value.has(chave(catId, idx))
}
</script>

<template>
  <section class="glossario">
    <h2>{{ glossarioMeta.titulo[locale] }}</h2>
    <p class="glossario-sub">{{ glossarioMeta.subtitulo[locale] }}</p>

    <nav class="glossario-tabs">
      <button
        v-for="cat in glossario"
        :key="cat.id"
        :class="{ ativo: cat.id === categoriaAtiva }"
        @click="categoriaAtiva = cat.id"
      >
        {{ cat.label[locale] }}
      </button>
    </nav>

    <div class="acordeao">
      <template v-for="cat in glossario" :key="cat.id">
        <div v-if="cat.id === categoriaAtiva">
          <div class="item" v-for="(item, idx) in cat.itens" :key="idx">
            <button class="item-cabecalho" @click="alternar(cat.id, idx)">
              <span>{{ item.titulo[locale] }}</span>
              <span class="seta" :class="{ aberto: estaAberto(cat.id, idx) }">+</span>
            </button>
            <p class="item-corpo" v-if="estaAberto(cat.id, idx)">{{ item.texto[locale] }}</p>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.glossario { margin-top: 52px; }
.glossario h2 {
  font-family: "Source Serif 4", Georgia, serif; font-size: 22px; font-weight: 600;
  margin: 0 0 8px;
}
.glossario-sub { font-size: 13px; color: #8a93ab; margin: 0 0 18px; }

.glossario-tabs { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.glossario-tabs button {
  background: transparent; border: 1px solid rgba(231,236,246,0.14);
  color: #c3c9db; padding: 7px 14px; border-radius: 4px;
  cursor: pointer; font-size: 12.5px; font-family: "Inter", sans-serif;
  transition: border-color 0.15s, color 0.15s;
}
.glossario-tabs button.ativo { border-color: #9b8cff; color: #9b8cff; }
.glossario-tabs button:hover:not(.ativo) { border-color: rgba(231,236,246,0.32); }

.acordeao { border-top: 1px solid rgba(231,236,246,0.1); }
.item { border-bottom: 1px solid rgba(231,236,246,0.1); }
.item-cabecalho {
  width: 100%; background: transparent; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 2px; color: #e7ecf6; font-size: 13.5px; font-family: "Inter", sans-serif;
  text-align: left;
}
.item-cabecalho:hover { color: #3ddc84; }
.seta {
  font-family: "IBM Plex Mono", monospace; color: #8a93ab; transition: transform 0.15s;
  flex-shrink: 0; margin-left: 12px;
}
.seta.aberto { transform: rotate(45deg); color: #3ddc84; }
.item-corpo {
  font-size: 13px; line-height: 1.7; color: #b5bccf; margin: 0 0 14px; max-width: 72ch;
}
</style>
