import { AbsoluteFill } from "remotion";

import { Background } from "./components/Background";
import { normalizeWord } from "./components/text";
import { bodyFont, displayFont, emojiFont } from "./fonts";
import { getPalette } from "./palettes";
import type { ThumbnailProps } from "./types";

// Static cover (1080x1920): huge emoji, 3-6 words with marker highlight and an optional badge
export const Thumbnail: React.FC<ThumbnailProps> = ({ title, highlight = [], subtitle, emoji, badge, palette }) => {
  const colors = getPalette(palette);
  const marked = new Set(highlight.map(normalizeWord));
  return (
    <AbsoluteFill>
      <Background palette={colors} seed="thumbnail" />
      <AbsoluteFill
        style={{
          padding: "220px 90px 520px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 50,
        }}
      >
        {badge && (
          <div
            style={{
              padding: "18px 44px",
              borderRadius: 999,
              background: "#ff0033",
              color: "#ffffff",
              fontFamily: bodyFont,
              fontWeight: 900,
              fontSize: 54,
              textTransform: "uppercase",
              transform: "rotate(-4deg)",
              boxShadow: "0 10px 0 #8a0018",
            }}
          >
            {badge}
          </div>
        )}
        {emoji && (
          <div style={{ fontFamily: emojiFont, fontSize: 330, lineHeight: 1, filter: "drop-shadow(0 24px 30px rgba(0,0,0,0.5))" }}>
            {emoji}
          </div>
        )}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            gap: "14px 26px",
            fontFamily: displayFont,
            fontSize: 150,
            lineHeight: 1.02,
            textTransform: "uppercase",
            textAlign: "center",
          }}
        >
          {title.split(/\s+/).map((word, index) => {
            const isMarked = marked.has(normalizeWord(word));
            return (
              <span
                key={`${word}-${index}`}
                style={{
                  color: isMarked ? "#111111" : "#ffffff",
                  background: isMarked ? colors.accent : "transparent",
                  padding: isMarked ? "0 18px" : 0,
                  borderRadius: 18,
                  transform: isMarked ? "rotate(-3deg)" : "none",
                  WebkitTextStroke: isMarked ? "0" : "4px #000000",
                  paintOrder: "stroke fill",
                  textShadow: isMarked ? "none" : "0 10px 0 #000000",
                  boxShadow: isMarked ? "0 12px 0 rgba(0,0,0,0.35)" : "none",
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
        {subtitle && (
          <div style={{ fontFamily: bodyFont, fontWeight: 900, fontSize: 60, color: colors.accent, textAlign: "center", textShadow: "0 6px 0 #000000" }}>
            {subtitle}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
