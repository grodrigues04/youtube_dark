import { spring, useCurrentFrame, useVideoConfig } from "remotion";

import { displayFont } from "../fonts";
import { normalizeWord } from "./text";

// Big title whose words slam in one after the other; highlighted words get a color marker
export const PopWords: React.FC<{
  text: string;
  highlight?: string[];
  accent: string;
  fontSize?: number;
  delay?: number;
  stagger?: number;
  color?: string;
}> = ({ text, highlight = [], accent, fontSize = 120, delay = 0, stagger = 4, color = "#ffffff" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const marked = new Set(highlight.map(normalizeWord));
  const words = text.split(/\s+/).filter(Boolean);

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        gap: `${fontSize * 0.12}px ${fontSize * 0.24}px`,
        fontFamily: displayFont,
        fontSize,
        lineHeight: 1.05,
        textTransform: "uppercase",
        textAlign: "center",
      }}
    >
      {words.map((word, index) => {
        const progress = spring({ frame: frame - delay - index * stagger, fps, config: { damping: 9, stiffness: 220 } });
        const isMarked = marked.has(normalizeWord(word));
        return (
          <span
            key={`${word}-${index}`}
            style={{
              display: "inline-block",
              color: isMarked ? "#111111" : color,
              background: isMarked ? accent : "transparent",
              padding: isMarked ? `0 ${fontSize * 0.12}px` : 0,
              borderRadius: fontSize * 0.12,
              transform: `scale(${progress}) translateY(${(1 - progress) * 80}px) rotate(${isMarked ? -3 : 0}deg)`,
              opacity: Math.min(progress * 2, 1),
              textShadow: isMarked ? "none" : "0 8px 0 rgba(0,0,0,0.35), 0 0 40px rgba(0,0,0,0.35)",
              boxShadow: isMarked ? `0 10px 0 rgba(0,0,0,0.3)` : "none",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
