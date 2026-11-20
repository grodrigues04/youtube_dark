import type { PaletteName } from "./types";

export type Palette = {
  background: [string, string, string];
  accent: string;
  accent2: string;
  text: string;
  blobs: string[];
};

// Saturated, high-contrast palettes: shorts are watched on phones, often with low brightness
export const PALETTES: Record<PaletteName, Palette> = {
  neon: {
    background: ["#12002e", "#3b0a7a", "#0a2a6e"],
    accent: "#39ff88",
    accent2: "#ff3df2",
    text: "#ffffff",
    blobs: ["#ff3df2", "#00e5ff", "#7c3aed", "#39ff88"],
  },
  sunset: {
    background: ["#2b0a3d", "#c2185b", "#ff6f00"],
    accent: "#ffe600",
    accent2: "#00e5ff",
    text: "#ffffff",
    blobs: ["#ff9100", "#ff1744", "#ffd600", "#d500f9"],
  },
  ocean: {
    background: ["#001b3a", "#004e92", "#00a6c0"],
    accent: "#ffd400",
    accent2: "#ff4fa0",
    text: "#ffffff",
    blobs: ["#00e5ff", "#2979ff", "#1de9b6", "#ffd400"],
  },
  candy: {
    background: ["#3d0066", "#ff2e93", "#ff8a00"],
    accent: "#00ffd5",
    accent2: "#fff200",
    text: "#ffffff",
    blobs: ["#ff6ec7", "#7df9ff", "#fff200", "#b388ff"],
  },
  lime: {
    background: ["#002b1f", "#00804a", "#9be15d"],
    accent: "#fff200",
    accent2: "#ff4081",
    text: "#ffffff",
    blobs: ["#c6ff00", "#00e676", "#18ffff", "#ffea00"],
  },
  fire: {
    background: ["#1a0000", "#8b0000", "#ff4500"],
    accent: "#ffea00",
    accent2: "#00e5ff",
    text: "#ffffff",
    blobs: ["#ff6d00", "#ff1744", "#ffc400", "#ff3d00"],
  },
};

export const getPalette = (name: PaletteName | undefined): Palette => PALETTES[name ?? "neon"] ?? PALETTES.neon;
