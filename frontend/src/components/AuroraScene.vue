<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue"
import * as THREE from "three"
import { t, nomeEvento } from "../i18n.js"

const props = defineProps({ evento: Object })
const container = ref(null)

let renderer, scene, camera, globo, oval, cortinaGrupo, ventoPoints, ventoGeo, ventoPos, ventoVel, estrelas, animId

function intensidadeDoEvento(ev) {
  if (!ev) return 0.3
  const valores = ev.dst_observado.filter(v => v !== null)
  const picoNegativo = Math.min(...valores)
  return Math.min(1, Math.max(0.15, Math.abs(picoNegativo) / 500))
}

function criarEstrelas() {
  const n = 500
  const pos = new Float32Array(n * 3)
  for (let i = 0; i < n; i++) {
    const r = 14 + Math.random() * 10
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)
    pos[i * 3] = r * Math.sin(phi) * Math.cos(theta)
    pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
    pos[i * 3 + 2] = r * Math.cos(phi)
  }
  const geo = new THREE.BufferGeometry()
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3))
  const mat = new THREE.PointsMaterial({ color: 0x8893b8, size: 0.04, transparent: true, opacity: 0.65 })
  estrelas = new THREE.Points(geo, mat)
  scene.add(estrelas)
}

function resetParticulaVento(i) {
  ventoPos[i * 3] = -9 - Math.random() * 5
  ventoPos[i * 3 + 1] = (Math.random() - 0.5) * 3.2
  ventoPos[i * 3 + 2] = (Math.random() - 0.5) * 3.2
  ventoVel[i] = 0.025 + Math.random() * 0.02
}

function criarVentoSolar() {
  const n = 260
  ventoPos = new Float32Array(n * 3)
  ventoVel = new Float32Array(n)
  for (let i = 0; i < n; i++) resetParticulaVento(i)
  ventoGeo = new THREE.BufferGeometry()
  ventoGeo.setAttribute("position", new THREE.BufferAttribute(ventoPos, 3))
  const mat = new THREE.PointsMaterial({ color: 0x9b8cff, size: 0.05, transparent: true, opacity: 0.85 })
  ventoPoints = new THREE.Points(ventoGeo, mat)
  scene.add(ventoPoints)
}

function animarVento(intensidade) {
  const n = ventoVel.length
  for (let i = 0; i < n; i++) {
    ventoPos[i * 3] += ventoVel[i] * (0.7 + intensidade * 2.2)
    if (ventoPos[i * 3] > -1.3) resetParticulaVento(i)
  }
  ventoGeo.attributes.position.needsUpdate = true
}

function criarCortinaAuroral() {
  const grupo = new THREE.Group()
  const n = 36
  for (let i = 0; i < n; i++) {
    const ang = (i / n) * Math.PI * 2
    const geo = new THREE.PlaneGeometry(0.05, 0.32)
    const mat = new THREE.MeshBasicMaterial({ color: 0x3ddc84, transparent: true, opacity: 0.4, side: THREE.DoubleSide })
    const faixa = new THREE.Mesh(geo, mat)
    faixa.position.set(Math.cos(ang) * 1.0, Math.sin(ang) * 1.0, 0.16)
    faixa.rotation.z = ang
    faixa.rotation.x = Math.PI / 2
    grupo.add(faixa)
  }
  oval.add(grupo)
  cortinaGrupo = grupo
}

function montarCena() {
  const largura = container.value.clientWidth
  const altura = container.value.clientHeight

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, largura / altura, 0.1, 100)
  camera.position.set(0, 1.4, 5.2)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(largura, altura)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.value.appendChild(renderer.domElement)

  const luz = new THREE.PointLight(0xffffff, 2)
  luz.position.set(5, 5, 5)
  scene.add(luz)
  scene.add(new THREE.AmbientLight(0x334466, 1.1))

  criarEstrelas()
  criarVentoSolar()

  globo = new THREE.Mesh(
    new THREE.SphereGeometry(1.4, 48, 48),
    new THREE.MeshStandardMaterial({ color: 0x14213d, roughness: 0.85, metalness: 0.1 })
  )
  scene.add(globo)

  oval = new THREE.Mesh(
    new THREE.TorusGeometry(1.0, 0.07, 16, 100),
    new THREE.MeshBasicMaterial({ color: 0x3ddc84, transparent: true, opacity: 0.8 })
  )
  oval.rotation.x = Math.PI / 2
  oval.position.y = 1.15
  scene.add(oval)
  criarCortinaAuroral()

  animar()
}

function animar() {
  animId = requestAnimationFrame(animar)
  globo.rotation.y += 0.0022
  oval.rotation.z += 0.0012
  animarVento(intensidadeDoEvento(props.evento))
  renderer.render(scene, camera)
}

function atualizarIntensidade() {
  if (!oval) return
  const k = intensidadeDoEvento(props.evento)
  oval.scale.setScalar(0.8 + k * 0.6)
  oval.material.opacity = 0.35 + k * 0.6

  const corBase = new THREE.Color(0x3ddc84)
  const corForte = new THREE.Color(0x9b8cff)
  const corAtual = corBase.clone().lerp(corForte, k)
  oval.material.color.copy(corAtual)

  if (cortinaGrupo) {
    cortinaGrupo.children.forEach(faixa => {
      faixa.material.color.copy(corAtual)
      faixa.material.opacity = 0.25 + k * 0.5
      faixa.scale.y = 0.6 + k * 1.1
    })
  }
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
      {{ t("cenaLegendaPre") }} <strong>{{ nomeEvento(evento) }}</strong>{{ t("cenaLegendaPos") }}
    </p>
  </div>
</template>

<style scoped>
.cena-wrap {
  background: #10172b; border: 1px solid rgba(231,236,246,0.08);
  border-radius: 4px; padding: 16px; display: flex; flex-direction: column; gap: 10px;
}
.cena { width: 100%; height: 340px; }
.legenda { font-size: 12.5px; color: #8a93ab; line-height: 1.6; margin: 0; }
.legenda strong { color: #c3c9db; font-weight: 600; }
</style>
