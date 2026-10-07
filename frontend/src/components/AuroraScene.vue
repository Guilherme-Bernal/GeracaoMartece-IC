<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as THREE from 'three'

const props = defineProps({ evento: Object })
const container = ref(null)

let renderer, scene, camera, globo, oval, animId

function intensidadeDoEvento(ev) {
  if (!ev) return 0.3
  const valores = ev.dst_observado.filter(v => v !== null)
  const picoNegativo = Math.min(...valores)
  const normalizado = Math.min(1, Math.max(0.15, Math.abs(picoNegativo) / 500))
  return normalizado
}

function montarCena() {
  const largura = container.value.clientWidth
  const altura = container.value.clientHeight

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, largura / altura, 0.1, 100)
  camera.position.set(0, 1.6, 5)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(largura, altura)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.value.appendChild(renderer.domElement)

  const luz = new THREE.PointLight(0xffffff, 2)
  luz.position.set(5, 5, 5)
  scene.add(luz)
  scene.add(new THREE.AmbientLight(0x334466, 1.2))

  globo = new THREE.Mesh(
    new THREE.SphereGeometry(1.4, 48, 48),
    new THREE.MeshStandardMaterial({ color: 0x14213d, roughness: 0.85, metalness: 0.1 })
  )
  scene.add(globo)

  oval = new THREE.Mesh(
    new THREE.TorusGeometry(1.0, 0.1, 16, 100),
    new THREE.MeshBasicMaterial({ color: 0x6ee7b7, transparent: true, opacity: 0.85 })
  )
  oval.rotation.x = Math.PI / 2
  oval.position.y = 1.15
  scene.add(oval)

  animar()
}

function animar() {
  animId = requestAnimationFrame(animar)
  globo.rotation.y += 0.0025
  oval.rotation.z += 0.0015
  renderer.render(scene, camera)
}

function atualizarIntensidade() {
  if (!oval) return
  const k = intensidadeDoEvento(props.evento)
  oval.scale.setScalar(0.8 + k * 0.6)
  oval.material.opacity = 0.35 + k * 0.6
  const corBase = new THREE.Color(0x6ee7b7)
  const corForte = new THREE.Color(0xc4b5fd)
  oval.material.color.copy(corBase).lerp(corForte, k)
}

onMounted(() => {
  montarCena()
  atualizarIntensidade()
})

watch(() => props.evento, atualizarIntensidade)

onBeforeUnmount(() => {
  cancelAnimationFrame(animId)
  renderer?.dispose()
})
</script>

<template>
  <div class="cena-wrap">
    <div ref="container" class="cena"></div>
    <p class="legenda" v-if="evento">
      Ovalo auroral ilustrativo - intensidade e abertura reagem ao pico de Dst de
      <strong>{{ evento.nome }}</strong>.
    </p>
  </div>
</template>

<style scoped>
.cena-wrap {
  background: #121a2e; border: 1px solid rgba(232,236,245,0.1);
  border-radius: 14px; padding: 16px; display: flex; flex-direction: column; gap: 10px;
}
.cena { width: 100%; height: 320px; }
.legenda { font-size: 12.5px; color: #8b93ab; margin: 0; }
</style>
