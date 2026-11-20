import { random, useCurrentFrame } from "remotion";

// Confetti burst from a point, deterministic so every render is identical
export const Confetti: React.FC<{ colors: string[]; delay?: number; x?: number; y?: number; count?: number }> = ({
  colors,
  delay = 0,
  x = 540,
  y = 900,
  count = 70,
}) => {
  const frame = useCurrentFrame() - delay;
  if (frame < 0 || frame > 75) {
    return null;
  }
  return (
    <>
      {Array.from({ length: count }, (_, index) => {
        const angle = random(`c-a-${index}`) * Math.PI * 2;
        const speed = 18 + random(`c-s-${index}`) * 30;
        const px = x + Math.cos(angle) * speed * frame;
        const py = y + Math.sin(angle) * speed * frame + 0.9 * frame * frame;
        const size = 14 + random(`c-z-${index}`) * 18;
        return (
          <div
            key={index}
            style={{
              position: "absolute",
              left: px,
              top: py,
              width: size,
              height: size * 0.55,
              background: colors[index % colors.length],
              borderRadius: 3,
              transform: `rotate(${frame * 18 + index * 40}deg)`,
              opacity: 1 - frame / 75,
            }}
          />
        );
      })}
    </>
  );
};
