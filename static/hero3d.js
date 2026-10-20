import * as THREE from "https://esm.sh/three@0.170.0";
import { GLTFLoader } from "https://esm.sh/three@0.170.0/examples/jsm/loaders/GLTFLoader.js";

const PURPLE = 0x9872ff;

function makeProceduralReel() {
  const reel = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.CylinderGeometry(1.13, 1.13, .27, 80, 1, false),
    new THREE.MeshStandardMaterial({
      color: 0x292638, metalness: .88, roughness: .25,
      emissive: 0x170d30, emissiveIntensity: .32,
    }),
  );
  body.rotation.x = Math.PI / 2;
  reel.add(body);

  const faceShape = new THREE.Shape();
  faceShape.absarc(0, 0, 1.08, 0, Math.PI * 2, false);
  for (let i = 0; i < 6; i += 1) {
    const angle = (i / 6) * Math.PI * 2 + Math.PI / 6;
    const hole = new THREE.Path();
    hole.absarc(Math.cos(angle) * .63, Math.sin(angle) * .63, .165, 0, Math.PI * 2, true);
    faceShape.holes.push(hole);
  }
  const face = new THREE.Mesh(
    new THREE.ExtrudeGeometry(faceShape, { depth: .07, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: .025, bevelThickness: .025 }),
    new THREE.MeshStandardMaterial({ color: 0xaba5bd, metalness: .82, roughness: .3, emissive: 0x241249, emissiveIntensity: .32 }),
  );
  face.position.z = .16;
  reel.add(face);

  const rim = new THREE.Mesh(
    new THREE.TorusGeometry(1.09, .025, 10, 96),
    new THREE.MeshStandardMaterial({ color: PURPLE, metalness: .64, roughness: .2, emissive: PURPLE, emissiveIntensity: .72 }),
  );
  rim.position.z = .25;
  reel.add(rim);

  for (let i = 0; i < 6; i += 1) {
    const angle = (i / 6) * Math.PI * 2 + Math.PI / 6;
    const x = Math.cos(angle) * .63;
    const y = Math.sin(angle) * .63;
    const lip = new THREE.Mesh(
      new THREE.TorusGeometry(.165, .018, 8, 32),
      new THREE.MeshStandardMaterial({ color: 0xd5d0e4, metalness: .8, roughness: .23 }),
    );
    lip.position.set(x, y, .235);
    reel.add(lip);
  }
  const hub = new THREE.Mesh(
    new THREE.CylinderGeometry(.3, .3, .09, 48),
    new THREE.MeshStandardMaterial({ color: 0xd7caff, metalness: .8, roughness: .2, emissive: PURPLE, emissiveIntensity: .3 }),
  );
  hub.rotation.x = Math.PI / 2;
  hub.position.z = .28;
  reel.add(hub);
  const spindle = new THREE.Mesh(
    new THREE.CylinderGeometry(.095, .095, .11, 32),
    new THREE.MeshStandardMaterial({ color: 0x292531, metalness: .85, roughness: .2 }),
  );
  spindle.rotation.x = Math.PI / 2;
  spindle.position.z = .35;
  reel.add(spindle);
  return reel;
}

function drawPosterTexture(movie) {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 700;
  const ctx = canvas.getContext("2d");
  const hue = (Number(movie.movieId) * 47) % 360;
  const base = ctx.createLinearGradient(0, 0, 512, 700);
  base.addColorStop(0, `hsl(${hue} 62% 32%)`);
  base.addColorStop(.65, `hsl(${(hue + 38) % 360} 54% 18%)`);
  base.addColorStop(1, "#08080d");
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, 512, 700);

  const glow = ctx.createRadialGradient(370, 165, 8, 370, 165, 260);
  glow.addColorStop(0, "rgba(255,255,255,.30)");
  glow.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, 512, 700);
  ctx.strokeStyle = "rgba(255,255,255,.2)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(392, 184, 116, 0, Math.PI * 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(392, 184, 151, 0, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = "rgba(255,255,255,.76)";
  ctx.font = "800 22px Arial";
  ctx.letterSpacing = "4px";
  ctx.fillText(String(movie.primaryGenre || "CINEMA").toUpperCase(), 34, 56);
  ctx.fillStyle = "#fff";
  ctx.font = "800 52px Arial";
  const words = String(movie.cleanTitle || movie.title).split(/\s+/);
  let line = "";
  let y = 500;
  for (const word of words) {
    const next = `${line}${word} `;
    if (ctx.measureText(next).width > 430 && line) {
      ctx.fillText(line.trim(), 34, y);
      line = `${word} `;
      y += 58;
    } else {
      line = next;
    }
  }
  if (line) ctx.fillText(line.trim(), 34, y);
  ctx.fillStyle = "rgba(255,255,255,.7)";
  ctx.font = "600 22px Arial";
  ctx.fillText(`${movie.year || "MOVIE"}  ·  CINESUGGEST`, 34, 654);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function loadPosterTexture(movie) {
  if (!movie.posterUrl) return Promise.resolve(drawPosterTexture(movie));
  return new Promise((resolve) => {
    const loader = new THREE.TextureLoader();
    loader.setCrossOrigin("anonymous");
    loader.load(
      movie.posterUrl,
      (texture) => {
        texture.colorSpace = THREE.SRGBColorSpace;
        const image = texture.image;
        const canvas = document.createElement("canvas");
        canvas.width = 512;
        canvas.height = 700;
        const ctx = canvas.getContext("2d");
        const ratio = Math.min(512 / image.width, 700 / image.height);
        const width = image.width * ratio;
        const height = image.height * ratio;
        ctx.fillStyle = "#101018";
        ctx.fillRect(0, 0, 512, 700);
        ctx.drawImage(image, (512 - width) / 2, (700 - height) / 2, width, height);
        texture.dispose();
        const poster = new THREE.CanvasTexture(canvas);
        poster.colorSpace = THREE.SRGBColorSpace;
        resolve(poster);
      },
      undefined,
      () => resolve(drawPosterTexture(movie)),
    );
  });
}

function makeRibbon(curve) {
  const segments = 240;
  const halfWidth = .34;
  const positions = [];
  const uvs = [];
  const indices = [];
  for (let i = 0; i <= segments; i += 1) {
    const t = i / segments;
    const point = curve.getPointAt(t);
    const tangent = curve.getTangentAt(t).normalize();
    const side = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();
    if (side.lengthSq() < .01) side.set(1, 0, 0);
    positions.push(
      point.x - side.x * halfWidth, point.y - side.y * halfWidth, point.z - side.z * halfWidth,
      point.x + side.x * halfWidth, point.y + side.y * halfWidth, point.z + side.z * halfWidth,
    );
    uvs.push(0, t * 18, 1, t * 18);
    if (i < segments) {
      const index = i * 2;
      indices.push(index, index + 1, index + 2, index + 1, index + 3, index + 2);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return new THREE.Mesh(
    geometry,
    new THREE.MeshStandardMaterial({ color: 0x17131f, metalness: .2, roughness: .48, side: THREE.DoubleSide, transparent: true, opacity: .78 }),
  );
}

export async function createCinemaScene(root, movies, setProgress) {
  const canvasHost = root.querySelector(".cine-journey__canvas");
  const canvas = document.createElement("canvas");
  canvasHost.appendChild(canvas);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x08080d);
  scene.fog = new THREE.FogExp2(0x08080d, .032);

  const camera = new THREE.PerspectiveCamera(36, 1, .1, 120);
  camera.position.set(0, .2, 9.4);
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: false, antialias: !window.matchMedia("(max-width: 760px)").matches, powerPreference: "high-performance" });
  const mobile = window.matchMedia("(max-width: 760px)").matches;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.18;
  renderer.shadowMap.enabled = !mobile;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setClearColor(0x08080d, 1);

  scene.add(new THREE.HemisphereLight(0xd8d0ff, 0x100d1a, 1.45));
  const keyLight = new THREE.DirectionalLight(0xfff3e6, 2.7);
  keyLight.position.set(-3, 5, 7);
  keyLight.castShadow = !mobile;
  scene.add(keyLight);
  const rim = new THREE.PointLight(PURPLE, 95, 18, 2);
  rim.position.set(3, 1.8, -1.5);
  scene.add(rim);
  const fill = new THREE.PointLight(0x5842ae, 28, 14, 2);
  fill.position.set(-4, -1, 2);
  scene.add(fill);

  const reelPivot = new THREE.Group();
  reelPivot.position.set(1.85, 0, 0);
  scene.add(reelPivot);
  let reelModel = makeProceduralReel();
  reelPivot.add(reelModel);
  try {
    const modelUrl = root.dataset.reelModel;
    if (modelUrl) {
      const gltf = await new GLTFLoader().loadAsync(modelUrl, (event) => {
        if (event.total) setProgress(20 + Math.min(55, (event.loaded / event.total) * 55));
      });
      reelPivot.remove(reelModel);
      gltf.scene.traverse((object) => {
        if (object.isMesh) {
          object.castShadow = !mobile;
          object.receiveShadow = !mobile;
          const materials = Array.isArray(object.material) ? object.material : [object.material];
          materials.forEach((material) => {
            if (material) material.metalness = Math.max(material.metalness || 0, .55);
          });
        }
      });
      reelModel = gltf.scene;
      reelPivot.add(reelModel);
    }
  } catch (error) {
    if (error?.name !== "NetworkError") console.info("Using procedural reel; optional /assets/reel.glb was not loaded.");
  }

  const spiral = new THREE.CatmullRomCurve3([
    new THREE.Vector3(1.5, -.05, .1),
    new THREE.Vector3(3.15, -.75, -.4),
    new THREE.Vector3(4.3, .65, -.9),
    new THREE.Vector3(5.5, -.68, -1.6),
    new THREE.Vector3(6.45, .3, -2.35),
    new THREE.Vector3(7.05, -.1, -3.2),
  ]);
  const ribbon = makeRibbon(spiral);
  ribbon.scale.setScalar(.001);
  scene.add(ribbon);

  const posters = new THREE.Group();
  scene.add(posters);
  const uniqueMovies = movies.slice(0, 12);
  for (let i = 0; i < uniqueMovies.length; i += 1) {
    const movie = uniqueMovies[i];
    const posterTexture = await loadPosterTexture(movie);
    setProgress(78 + ((i + 1) / Math.max(1, uniqueMovies.length)) * 18);
    const card = new THREE.Group();
    const artwork = new THREE.Group();
    const backing = new THREE.Mesh(
      new THREE.BoxGeometry(.93, 1.3, .055),
      new THREE.MeshStandardMaterial({ color: 0x211a32, metalness: .22, roughness: .45, emissive: 0x120b23, emissiveIntensity: .45 }),
    );
    artwork.add(backing);
    const image = new THREE.Mesh(
      new THREE.PlaneGeometry(.86, 1.19),
      new THREE.MeshBasicMaterial({ map: posterTexture, side: THREE.DoubleSide }),
    );
    image.position.z = .032;
    artwork.add(image);
    card.add(artwork);
    card.userData.movie = movie;
    card.userData.artwork = artwork;
    const curvePosition = spiral.getPointAt((i + .5) / uniqueMovies.length);
    card.position.copy(curvePosition);
    card.position.y += .52;
    card.scale.setScalar(.001);
    posters.add(card);
  }

  const particleCount = mobile ? 42 : 120;
  const particleGeometry = new THREE.SphereGeometry(.018, 6, 6);
  const particleMaterial = new THREE.MeshBasicMaterial({ color: 0xb6a1ff, transparent: true, opacity: .64 });
  const dust = new THREE.InstancedMesh(particleGeometry, particleMaterial, particleCount);
  const dummy = new THREE.Object3D();
  const particleSeeds = [];
  for (let i = 0; i < particleCount; i += 1) {
    const seed = { x: (Math.random() - .5) * 15, y: (Math.random() - .5) * 8, z: -Math.random() * 12, phase: Math.random() * Math.PI * 2 };
    particleSeeds.push(seed);
    dummy.position.set(seed.x, seed.y, seed.z);
    dummy.updateMatrix();
    dust.setMatrixAt(i, dummy.matrix);
  }
  scene.add(dust);

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2(2, 2);
  const mouse = new THREE.Vector2();
  let hovered = null;
  let disposed = false;
  let frame = 0;
  const start = performance.now();
  function resize() {
    const rect = canvasHost.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    renderer.setSize(rect.width, rect.height, false);
    camera.aspect = rect.width / rect.height;
    camera.updateProjectionMatrix();
  }
  function onPointerMove(event) {
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    mouse.set(pointer.x, pointer.y);
  }
  function onPointerLeave() {
    pointer.set(2, 2);
    if (hovered) hovered.userData.artwork.scale.setScalar(1);
    hovered = null;
    canvas.style.cursor = "default";
  }
  function openDetails(movie) {
    const dialog = root.querySelector(".cine-journey__modal");
    dialog.querySelector("[data-detail-title]").textContent = movie.cleanTitle || movie.title;
    dialog.querySelector("[data-detail-meta]").textContent = [movie.year, movie.genres].filter(Boolean).join(" · ");
    dialog.showModal();
  }
  function onClick() {
    if (hovered?.userData.movie) openDetails(hovered.userData.movie);
  }
  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("pointerleave", onPointerLeave);
  canvas.addEventListener("click", onClick);
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvasHost);
  window.addEventListener("resize", resize);
  resize();

  function render(now) {
    if (disposed) return;
    frame = requestAnimationFrame(render);
    const elapsed = (now - start) / 1000;
    reelPivot.rotation.y = Math.sin(elapsed * .28) * .11 + mouse.x * .12;
    reelPivot.rotation.x = Math.cos(elapsed * .24) * .055 - mouse.y * .09;
    reelPivot.position.y = Math.sin(elapsed * .7) * .08;
    for (let i = 0; i < particleCount; i += 1) {
      const seed = particleSeeds[i];
      dummy.position.set(seed.x + Math.sin(elapsed * .16 + seed.phase) * .15, seed.y + Math.sin(elapsed * .28 + seed.phase) * .22, seed.z);
      dummy.updateMatrix();
      dust.setMatrixAt(i, dummy.matrix);
    }
    dust.instanceMatrix.needsUpdate = true;
    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObjects(posters.children, true);
    const nextHover = hits.length ? hits[0].object.parent.parent : null;
    if (nextHover !== hovered) {
      if (hovered) hovered.userData.artwork.scale.setScalar(1);
      hovered = nextHover;
    }
    if (hovered) hovered.userData.artwork.scale.lerp(new THREE.Vector3(1.12, 1.12, 1.12), .16);
    canvas.style.cursor = hovered ? "pointer" : "default";
    renderer.render(scene, camera);
  }
  render(performance.now());
  setProgress(100);

  function dispose() {
    if (disposed) return;
    disposed = true;
    cancelAnimationFrame(frame);
    resizeObserver.disconnect();
    window.removeEventListener("resize", resize);
    canvas.removeEventListener("pointermove", onPointerMove);
    canvas.removeEventListener("pointerleave", onPointerLeave);
    canvas.removeEventListener("click", onClick);
    scene.traverse((object) => {
      object.geometry?.dispose();
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      materials.forEach((material) => {
        if (!material) return;
        Object.values(material).forEach((value) => {
          if (value?.isTexture) value.dispose();
        });
        material.dispose();
      });
    });
    renderer.dispose();
    renderer.forceContextLoss();
    canvas.remove();
  }
  return { scene, camera, reelPivot, ribbon, posters, dispose };
}
