import { spring, useCurrentFrame, useVideoConfig } from "remotion";

import { bodyFont } from "../fonts";
import type { Word } from "../types";
import { CAPTIONS_TOP, SAFE } from "./layout";
import { normalizeWord } from "./text";

const WORDS_PER_CHUNK = 3;

// Word-synced captions, 3 words at a time; the word being spoken pops and turns accent color
export const Captions: React.FC<{ words: Word[]; highlight?: string[]; accent: string; accent2: string }> = ({
  words,
  highlight = [],
  accent,
  accent2,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (words.length === 0) {
    return null;
  }
  const marked = new Set(highlight.map(normalizeWord));
  let current = words.findIndex((word) => frame >= word.startFrame && frame < word.endFrame);
  if (current === -1) {
    // Between words: keep the last one that already started
    current = Math.max(0, words.filter((word) => word.startFrame <= frame).length - 1);
  }
  const chunkStart = Math.floor(current / WORDS_PER_CHUNK) * WORDS_PER_CHUNK;
  const chunk = words.slice(chunkStart, chunkStart + WORDS_PER_CHUNK);
  const chunkPop = spring({ frame: frame - chunk[0].startFrame, fps, config: { damping: 10, stiffness: 260 } });

  return (
    <div
      style={{
        position: "absolute",
        top: CAPTIONS_TOP,
        left: SAFE.left,
        right: SAFE.right,
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        gap: "10px 0",
        transform: `scale(${0.7 + chunkPop * 0.3})`,
        fontFamily: bodyFont,
        fontWeight: 900,
        fontSize: 76,
        lineHeight: 1.1,
        textTransform: "uppercase",
      }}
    >
      {chunk.map((word, index) => {
        const active = chunkStart + index === current;
        const isMarked = marked.has(normalizeWord(word.text));
        return (
          <span
            key={`${word.text}-${word.startFrame}`}
            style={{
              display: "inline-block",
              // Margin instead of flex gap: the active word grows and must not touch its neighbors
              margin: "0 22px",
              color: active ? accent : isMarked ? accent2 : "#ffffff",
              transform: `scale(${active ? 1.15 : 1}) rotate(${active ? -2 : 0}deg)`,
              transformOrigin: "center bottom",
              WebkitTextStroke: "3px #000000",
              paintOrder: "stroke fill",
              textShadow: "0 7px 0 #000000, 0 0 30px rgba(0,0,0,0.6)",
            }}
          >
            {word.text}
          </span>
        );
      })}
    </div>
  );
};
