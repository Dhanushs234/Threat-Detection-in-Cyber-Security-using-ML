import { useEffect, useRef, useState } from "react";
import L from "leaflet";

const COUNTRY_COORDS = {
  Australia: [-25.2744, 133.7751],
  Brazil: [-14.235, -51.9253],
  Canada: [56.1304, -106.3468],
  China: [35.8617, 104.1954],
  France: [46.6034, 1.8883],
  Germany: [51.1657, 10.4515],
  India: [20.5937, 78.9629],
  Iran: [32.4279, 53.688],
  Japan: [36.2048, 138.2529],
  Netherlands: [52.1326, 5.2913],
  "North Korea": [40.3399, 127.5101],
  Romania: [45.9432, 24.9668],
  Russia: [61.524, 105.3188],
  Singapore: [1.3521, 103.8198],
  "South Korea": [35.9078, 127.7669],
  Ukraine: [48.3794, 31.1656],
  "United Kingdom": [55.3781, -3.436],
  "United States": [37.0902, -95.7129],
  Vietnam: [14.0583, 108.2772],
};

const ARC_COLORS = {
  normal: "#00ff88",
  suspicious: "#ff9800",
  attack: "#ff3b3b",
};

const COUNTRY_FILL_COLOR = "#1f2b3b";
const MAP_CENTER = [20, 0];
const FIXED_ZOOM = 2;
const VIEW_BOUNDS = [
  [-60, -180],
  [85, 180],
];
const DETECTION_CYCLE_MS = 7000;
const FADE_START_MS = 4000;
const FADE_DURATION_MS = DETECTION_CYCLE_MS - FADE_START_MS;
const MIN_TRAVEL_DURATION_MS = 1500;
const MAX_TRAVEL_DURATION_MS = 4000;
const BASE_HIGHLIGHT_OPACITY = 0.55;
const BASE_COUNTRY_STYLE = {
  color: "#e6eaf0",
  weight: 1,
  opacity: 0.9,
  dashArray: "0",
  fillColor: COUNTRY_FILL_COLOR,
  fillOpacity: 1,
};

const OCEAN_COLOR = "#223041";

export default function ThreatMap({ detection }) {
  const mapRef = useRef(null);
  const canvasRef = useRef(null);
  const activeArcRef = useRef(null);
  const layerMapRef = useRef(new Map());
  const lastActiveCountriesRef = useRef(new Set());
  const animationFrameRef = useRef(null);
  const mapReadyRef = useRef(false);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (mapRef.current) return;

    mapRef.current = L.map("threat-map", {
      zoomControl: false,
      dragging: false,
      scrollWheelZoom: false,
      doubleClickZoom: false,
      touchZoom: false,
      keyboard: false,
      attributionControl: false,
      worldCopyJump: false,
    }).setView(MAP_CENTER, FIXED_ZOOM);
    mapRef.current.setMinZoom(FIXED_ZOOM);
    mapRef.current.setMaxZoom(FIXED_ZOOM);
    mapRef.current.setMaxBounds(VIEW_BOUNDS);
    mapRef.current.options.maxBoundsViscosity = 1.0;
    mapRef.current.getContainer().style.background = OCEAN_COLOR;
    mapRef.current.invalidateSize();

    fetch(
      "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    )
      .then((res) => res.json())
      .then((geo) => {
        layerMapRef.current.clear();
        const geoLayer = L.geoJSON(geo, {
          style: BASE_COUNTRY_STYLE,
          onEachFeature: (feature, layer) => {
            const name = feature?.properties?.name;
            if (name) {
              if (layer.options) {
                layer.options.noWrap = true;
              }
              layerMapRef.current.set(name, layer);
              layer.bindTooltip(name, {
                sticky: true,
                direction: "auto",
                offset: [10, 10],
                className: "threat-map-tooltip",
              });
            }
          },
        });

        geoLayer.options.noWrap = true;
        geoLayer.eachLayer((subLayer) => {
          if (subLayer?.options) {
            subLayer.options.noWrap = true;
          }
        });

        geoLayer.addTo(mapRef.current);

        mapReadyRef.current = true;
        setMapReady(true);
        ensureAnimationLoop();
      })
      .catch(() => {
        mapReadyRef.current = false;
        setMapReady(false);
      });

    canvasRef.current = document.createElement("canvas");
    canvasRef.current.style.position = "absolute";
    canvasRef.current.style.top = 0;
    canvasRef.current.style.left = 0;
    canvasRef.current.style.zIndex = 500;
    canvasRef.current.style.pointerEvents = "none";
    mapRef.current.getPanes().overlayPane.appendChild(canvasRef.current);

    resizeCanvas();
    mapRef.current.on("move resize", resizeCanvas);

    const handleWindowResize = () => {
      if (!mapRef.current) return;
      mapRef.current.invalidateSize({ animate: false });
      resizeCanvas();
      if (activeArcRef.current) {
        ensureAnimationLoop();
      }
    };

    window.addEventListener("resize", handleWindowResize);

    return () => {
      if (mapRef.current) {
        mapRef.current.off("move resize", resizeCanvas);
      }
      window.removeEventListener("resize", handleWindowResize);
      stopAnimationLoop();
      resetActiveArc();
      mapReadyRef.current = false;
      setMapReady(false);
    };
  }, []);

  function resizeCanvas() {
    if (!mapRef.current || !canvasRef.current) return;
    const size = mapRef.current.getSize();
    const dpr = window.devicePixelRatio || 1;
    canvasRef.current.width = size.x * dpr;
    canvasRef.current.height = size.y * dpr;
    canvasRef.current.style.width = `${size.x}px`;
    canvasRef.current.style.height = `${size.y}px`;
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
  }

  function calculateTravelDuration(srcCountry, dstCountry) {
    const map = mapRef.current;
    if (!map) return MAX_TRAVEL_DURATION_MS;

    const srcCoords = COUNTRY_COORDS[srcCountry];
    const dstCoords = COUNTRY_COORDS[dstCountry];
    if (!srcCoords || !dstCoords) return MAX_TRAVEL_DURATION_MS;

    const srcPoint = map.latLngToContainerPoint(srcCoords);
    const dstPoint = map.latLngToContainerPoint(dstCoords);
    const dx = dstPoint.x - srcPoint.x;
    const dy = dstPoint.y - srcPoint.y;
    const distance = Math.hypot(dx, dy);
    const size = map.getSize();
    const maxDistance = Math.max(Math.hypot(size.x, size.y), 1);
    const distanceRatio = Math.min(distance / maxDistance, 1);

    const duration =
      MAX_TRAVEL_DURATION_MS -
      (MAX_TRAVEL_DURATION_MS - MIN_TRAVEL_DURATION_MS) * distanceRatio;

    return Math.min(
      Math.max(duration, MIN_TRAVEL_DURATION_MS),
      MAX_TRAVEL_DURATION_MS
    );
  }

  function normalizeCountryName(country) {
    if (country === "United States") {
      return "United States of America";
    }
    return country;
  }

  function applyStyleToLayer(layer, style, glowColor) {
    if (!layer) return;

    if (typeof layer.eachLayer === "function") {
      layer.eachLayer((subLayer) => applyStyleToLayer(subLayer, style, glowColor));
      return;
    }

    if (typeof layer.setStyle === "function") {
      layer.setStyle(style);
    }
    const element = layer.getElement();
    if (element) {
      if (glowColor) {
        element.style.filter = `drop-shadow(0 0 12px ${glowColor}66)`;
      } else {
        element.style.removeProperty("filter");
      }
    }
  }

  function setCountryFill(country, color, opacity, activeCountries) {
    if (!mapReadyRef.current) return;
    const normalizedCountry = normalizeCountryName(country);
    const layer = layerMapRef.current.get(normalizedCountry);
    if (!layer) return;

    const highlightStyle = {
      ...BASE_COUNTRY_STYLE,
      fillColor: color,
      fillOpacity: opacity,
    };

    applyStyleToLayer(layer, highlightStyle, color);
    activeCountries.add(normalizedCountry);
  }

  function resetCountryFill(country) {
    const normalizedCountry = normalizeCountryName(country);
    const layer = layerMapRef.current.get(normalizedCountry);
    if (!layer) return;

    applyStyleToLayer(layer, { ...BASE_COUNTRY_STYLE }, null);
  }

  function syncActiveCountries(nextActive) {
    const previous = lastActiveCountriesRef.current;
    previous.forEach((country) => {
      if (!nextActive.has(country)) {
        resetCountryFill(country);
      }
    });

    previous.clear();
    nextActive.forEach((country) => previous.add(country));
  }

  function clearActiveCountries() {
    const previous = lastActiveCountriesRef.current;
    previous.forEach((country) => resetCountryFill(country));
    previous.clear();
  }

  function clearCanvas() {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }

  function resetActiveArc() {
    activeArcRef.current = null;
    clearActiveCountries();
    clearCanvas();
  }

  function renderFrame(time) {
    const canvas = canvasRef.current;
    const map = mapRef.current;
    if (!canvas || !map) {
      return false;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return false;
    }

    const dpr = window.devicePixelRatio || 1;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.scale(dpr, dpr);

    const activeArc = activeArcRef.current;
    const activeCountriesThisFrame = new Set();

    if (!activeArc) {
      syncActiveCountries(activeCountriesThisFrame);
      return false;
    }

    const elapsed = time - activeArc.startTime;

    if (elapsed >= DETECTION_CYCLE_MS) {
      activeArcRef.current = null;
      syncActiveCountries(activeCountriesThisFrame);
      return false;
    }

    const srcCoords = COUNTRY_COORDS[activeArc.srcCountry];
    const dstCoords = COUNTRY_COORDS[activeArc.dstCountry];

    if (!srcCoords || !dstCoords) {
      activeArcRef.current = null;
      syncActiveCountries(activeCountriesThisFrame);
      return false;
    }

    const p1 = map.latLngToContainerPoint(srcCoords);
    const p2 = map.latLngToContainerPoint(dstCoords);

    const travelProgress = Math.min(elapsed / activeArc.travelDuration, 1);
    const fadeProgress =
      elapsed <= FADE_START_MS
        ? 0
        : Math.min((elapsed - FADE_START_MS) / FADE_DURATION_MS, 1);
    const intensity = Math.max(1 - fadeProgress, 0);
    const fillOpacity = BASE_HIGHLIGHT_OPACITY * intensity;

    if (intensity > 0) {
      const cx = (p1.x + p2.x) / 2;
      const cy = Math.min(p1.y, p2.y) - 80;

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.quadraticCurveTo(
        cx,
        cy,
        p1.x + (p2.x - p1.x) * travelProgress,
        p1.y + (p2.y - p1.y) * travelProgress
      );

      ctx.strokeStyle = activeArc.color;
      ctx.lineWidth = 2 * intensity;
      ctx.globalAlpha = intensity;
      ctx.shadowBlur = 12 * intensity;
      ctx.shadowColor = activeArc.color;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    if (elapsed < DETECTION_CYCLE_MS && fillOpacity > 0.02) {
      setCountryFill(
        activeArc.srcCountry,
        activeArc.color,
        fillOpacity,
        activeCountriesThisFrame
      );

      if (elapsed >= activeArc.travelDuration) {
        setCountryFill(
          activeArc.dstCountry,
          activeArc.color,
          fillOpacity,
          activeCountriesThisFrame
        );
      }
    }

    syncActiveCountries(activeCountriesThisFrame);

    return true;
  }

  function handleFrame(time) {
    animationFrameRef.current = null;
    const shouldContinue = renderFrame(time);
    if (shouldContinue) {
      animationFrameRef.current = requestAnimationFrame(handleFrame);
    }
  }

  function ensureAnimationLoop() {
    if (animationFrameRef.current !== null) {
      return;
    }

    animationFrameRef.current = requestAnimationFrame(handleFrame);
  }

  function stopAnimationLoop() {
    if (animationFrameRef.current !== null) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }

  useEffect(() => {
    if (!detection || !mapReadyRef.current) {
      resetActiveArc();
      return;
    }

    const { src, dst, level } = detection;
    if (!COUNTRY_COORDS[src] || !COUNTRY_COORDS[dst]) {
      resetActiveArc();
      return;
    }

    const startTime = performance.now();
    const travelDuration = calculateTravelDuration(src, dst);

    activeArcRef.current = {
      srcCountry: src,
      dstCountry: dst,
      startTime,
      travelDuration,
      color: ARC_COLORS[level],
    };

    ensureAnimationLoop();

    return () => {
      resetActiveArc();
    };
  }, [detection, mapReady]);

  return (
    <div className="threat-map-wrapper">
      <div id="threat-map" style={{ width: "100%", height: "100%" }} />
    </div>
  );
}
