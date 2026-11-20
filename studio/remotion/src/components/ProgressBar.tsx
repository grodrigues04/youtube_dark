import { useCurrentFrame, useVideoConfig } from "remotion";

// Thin progress bar at the top: shows the video is short and keeps people until the end
export const ProgressBar: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 14, background: "rgba(255,255,255,0.18)" }}>
      <div
        style={{
          width: `${(frame / durationInFrames) * 100}%`,
          height: "100%",
          background: color,
          boxShadow: `0 0 20px ${color}`,
        }}
      />
    </div>
  );
};
