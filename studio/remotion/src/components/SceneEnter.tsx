import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

import { SAFE } from "./layout";

// Every scene punches in (zoom + tilt) and keeps a slow push-in; `shake` adds a camera shake
export const SceneEnter: React.FC<{ children: React.ReactNode; shake?: boolean; durationInFrames: number }> = ({
  children,
  shake = false,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 12, stiffness: 160 } });
  const exit = interpolate(frame, [durationInFrames - 6, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(enter, [0, 1], [1.35, 1]) * interpolate(frame, [0, durationInFrames], [1, 1.06]);
  const rotate = interpolate(enter, [0, 1], [-4, 0]);
  const shakeAmount = shake ? Math.max(0, 1 - frame / 18) * 16 : 0;
  const x = Math.sin(frame * 2.3) * shakeAmount;
  const y = Math.cos(frame * 1.7) * shakeAmount;

  return (
    <AbsoluteFill
      style={{
        paddingTop: SAFE.top,
        paddingLeft: SAFE.left,
        paddingRight: SAFE.right,
        paddingBottom: SAFE.bottom,
        transform: `translate(${x}px, ${y}px) scale(${scale}) rotate(${rotate}deg)`,
        opacity: Math.min(enter * 1.5, 1) * exit,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 48,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
