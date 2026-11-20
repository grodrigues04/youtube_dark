import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

import { emojiFont } from "../fonts";

// Emoji that bounces in, then keeps wobbling and floating
export const BigEmoji: React.FC<{ emoji?: string; size?: number; delay?: number }> = ({ emoji, size = 220, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!emoji) {
    return null;
  }
  const pop = spring({ frame: frame - delay, fps, config: { damping: 7, stiffness: 180 } });
  const wobble = Math.sin((frame - delay) / 5) * 8;
  const float = Math.sin((frame - delay) / 10) * 14;
  return (
    <div
      style={{
        fontFamily: emojiFont,
        fontSize: size,
        lineHeight: 1,
        transform: `translateY(${float}px) scale(${pop}) rotate(${interpolate(pop, [0, 1], [-90, 0]) + wobble}deg)`,
        filter: "drop-shadow(0 20px 30px rgba(0,0,0,0.45))",
      }}
    >
      {emoji}
    </div>
  );
};
