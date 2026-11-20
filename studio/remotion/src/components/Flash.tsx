import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

// White flash on the first frames of a scene: a hard visual cut that resets attention
export const Flash: React.FC<{ color?: string }> = ({ color = "#ffffff" }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 5], [0.85, 0], { extrapolateRight: "clamp" });
  if (opacity <= 0) {
    return null;
  }
  return <AbsoluteFill style={{ background: color, opacity, mixBlendMode: "screen" }} />;
};
