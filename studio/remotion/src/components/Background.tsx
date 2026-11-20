import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";

import type { Palette } from "../palettes";

// Animated gradient + drifting color blobs + floating sparkles: the screen is never static
export const Background: React.FC<{ palette: Palette; seed?: string }> = ({ palette, seed = "bg" }) => {
  const frame = useCurrentFrame();
  const angle = 135 + Math.sin(frame / 60) * 25;
  const [first, second, third] = palette.background;

  return (
    <AbsoluteFill style={{ background: `linear-gradient(${angle}deg, ${first}, ${second} 55%, ${third})` }}>
      {palette.blobs.map((color, index) => {
        const x = 540 + Math.sin(frame / (45 + index * 11) + index * 2) * 420;
        const y = 960 + Math.cos(frame / (52 + index * 7) + index) * 760;
        const size = 520 + Math.sin(frame / 30 + index) * 80;
        return (
          <div
            key={color + index}
            style={{
              position: "absolute",
              left: x - size / 2,
              top: y - size / 2,
              width: size,
              height: size,
              borderRadius: "50%",
              background: color,
              opacity: 0.45,
              filter: "blur(120px)",
            }}
          />
        );
      })}
      {Array.from({ length: 26 }, (_, index) => {
        const x = random(`${seed}-x-${index}`) * 1080;
        const speed = 0.6 + random(`${seed}-s-${index}`) * 1.6;
        const y = (1920 + 100 - ((frame * speed * 3 + random(`${seed}-y-${index}`) * 2000) % 2100)) - 50;
        const size = 6 + random(`${seed}-r-${index}`) * 14;
        const twinkle = interpolate(Math.sin(frame / 8 + index), [-1, 1], [0.25, 0.9]);
        return (
          <div
            key={index}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              background: index % 3 === 0 ? palette.accent : "#ffffff",
              opacity: twinkle,
              boxShadow: `0 0 ${size * 2}px ${index % 3 === 0 ? palette.accent : "#ffffff"}`,
            }}
          />
        );
      })}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.55) 100%)" }} />
    </AbsoluteFill>
  );
};
