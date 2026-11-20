import { spring, useCurrentFrame, useVideoConfig } from "remotion";

import { bodyFont, emojiFont } from "../fonts";

// Glassy colored card that slides in from a side
export const Card: React.FC<{
  emoji?: string;
  text: string;
  color: string;
  delay: number;
  from?: "left" | "right";
  fontSize?: number;
}> = ({ emoji, text, color, delay, from = "left", fontSize = 52 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - delay, fps, config: { damping: 11, stiffness: 170 } });
  const direction = from === "left" ? -1 : 1;
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 28,
        width: "100%",
        padding: "28px 36px",
        borderRadius: 32,
        background: "rgba(255,255,255,0.14)",
        border: `4px solid ${color}`,
        boxShadow: `0 14px 0 rgba(0,0,0,0.25), 0 0 40px ${color}55`,
        transform: `translateX(${(1 - progress) * 900 * direction}px) rotate(${(1 - progress) * 8 * direction}deg)`,
        opacity: Math.min(progress * 2, 1),
        fontFamily: bodyFont,
        fontWeight: 800,
        fontSize,
        color: "#ffffff",
        lineHeight: 1.15,
      }}
    >
      {emoji && <span style={{ fontFamily: emojiFont, fontSize: fontSize * 1.4 }}>{emoji}</span>}
      <span>{text}</span>
    </div>
  );
};
