import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

import { BigEmoji } from "../components/BigEmoji";
import { Card } from "../components/Card";
import { Confetti } from "../components/Confetti";
import { PopWords } from "../components/PopWords";
import { SceneEnter } from "../components/SceneEnter";
import { bodyFont, displayFont, emojiFont } from "../fonts";
import type { Palette } from "../palettes";
import type {
  CompareScene,
  CtaScene,
  HookScene,
  JourneyScene,
  ListScene,
  QuestionScene,
  RevealScene,
  Scene,
  StatementScene,
  StatScene,
  StepsScene,
} from "../types";

type SceneProps<T extends Scene> = { scene: T; palette: Palette };

// Items of lists/steps/compare appear spread over the first 70% of the scene, so they arrive
// roughly while the narration talks about them
const revealDelay = (index: number, count: number, durationInFrames: number): number =>
  Math.round(8 + (index * (durationInFrames * 0.7 - 8)) / Math.max(count, 1));

const Subtitle: React.FC<{ text?: string; delay?: number }> = ({ text, delay = 10 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!text) {
    return null;
  }
  const progress = spring({ frame: frame - delay, fps, config: { damping: 14 } });
  return (
    <div
      style={{
        fontFamily: bodyFont,
        fontWeight: 800,
        fontSize: 54,
        color: "#ffffff",
        textAlign: "center",
        lineHeight: 1.2,
        opacity: progress,
        transform: `translateY(${(1 - progress) * 40}px)`,
        textShadow: "0 5px 0 rgba(0,0,0,0.35)",
      }}
    >
      {text}
    </div>
  );
};

const HookView: React.FC<SceneProps<HookScene>> = ({ scene, palette }) => (
  <SceneEnter durationInFrames={scene.durationInFrames} shake>
    <BigEmoji emoji={scene.emoji} size={260} />
    <PopWords text={scene.text} highlight={scene.highlight} accent={palette.accent} fontSize={130} stagger={3} />
  </SceneEnter>
);

const StatementView: React.FC<SceneProps<StatementScene>> = ({ scene, palette }) => (
  <SceneEnter durationInFrames={scene.durationInFrames}>
    <BigEmoji emoji={scene.emoji} size={200} />
    <PopWords text={scene.title} highlight={scene.highlight} accent={palette.accent} fontSize={112} />
    <Subtitle text={scene.subtitle} delay={14} />
  </SceneEnter>
);

const StatView: React.FC<SceneProps<StatScene>> = ({ scene, palette }) => {
  const frame = useCurrentFrame();
  const counting = interpolate(frame, [4, Math.min(40, scene.durationInFrames - 10)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  const value = (scene.value * counting).toLocaleString("pt-BR", {
    minimumFractionDigits: scene.decimals ?? 0,
    maximumFractionDigits: scene.decimals ?? 0,
  });
  const ring = 2 * Math.PI * 300;
  const pulse = 1 + Math.sin(frame / 4) * 0.02;
  return (
    <SceneEnter durationInFrames={scene.durationInFrames}>
      <div style={{ position: "relative", width: 680, height: 680, display: "grid", placeItems: "center" }}>
        <svg width={680} height={680} style={{ position: "absolute", transform: "rotate(-90deg)" }}>
          <circle cx={340} cy={340} r={300} stroke="rgba(255,255,255,0.15)" strokeWidth={34} fill="none" />
          <circle
            cx={340}
            cy={340}
            r={300}
            stroke={palette.accent}
            strokeWidth={34}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={ring}
            strokeDashoffset={ring * (1 - counting)}
            style={{ filter: `drop-shadow(0 0 24px ${palette.accent})` }}
          />
        </svg>
        <div style={{ textAlign: "center", transform: `scale(${pulse})` }}>
          <BigEmoji emoji={scene.emoji} size={110} />
          <div
            style={{
              fontFamily: displayFont,
              fontSize: 150,
              lineHeight: 1,
              color: "#ffffff",
              textShadow: `0 10px 0 rgba(0,0,0,0.35), 0 0 60px ${palette.accent}`,
              whiteSpace: "nowrap",
            }}
          >
            {scene.prefix}
            {value}
            {scene.suffix}
          </div>
        </div>
      </div>
      <Subtitle text={scene.label} delay={20} />
      <Confetti colors={palette.blobs} delay={Math.min(40, scene.durationInFrames - 10)} y={700} />
    </SceneEnter>
  );
};

const ListView: React.FC<SceneProps<ListScene>> = ({ scene, palette }) => (
  <SceneEnter durationInFrames={scene.durationInFrames}>
    <PopWords text={scene.title} highlight={scene.highlight} accent={palette.accent} fontSize={92} />
    <div style={{ display: "flex", flexDirection: "column", gap: 26, width: "100%" }}>
      {scene.items.slice(0, 4).map((item, index) => (
        <Card
          key={item.text}
          emoji={item.emoji ?? "✅"}
          text={item.text}
          color={index % 2 === 0 ? palette.accent : palette.accent2}
          delay={revealDelay(index, scene.items.length, scene.durationInFrames)}
          from={index % 2 === 0 ? "left" : "right"}
        />
      ))}
    </div>
  </SceneEnter>
);

const SideColumn: React.FC<{ side: CompareScene["left"]; color: string; delay: number; from: "left" | "right" }> = ({
  side,
  color,
  delay,
  from,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - delay, fps, config: { damping: 12 } });
  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 18,
        padding: "34px 22px",
        borderRadius: 36,
        background: "rgba(0,0,0,0.28)",
        border: `5px solid ${color}`,
        boxShadow: `0 0 50px ${color}66`,
        transform: `translateX(${(1 - progress) * (from === "left" ? -700 : 700)}px)`,
      }}
    >
      {side.emoji && <span style={{ fontFamily: emojiFont, fontSize: 120 }}>{side.emoji}</span>}
      <div style={{ fontFamily: displayFont, fontSize: 64, color, textTransform: "uppercase", textAlign: "center" }}>
        {side.title}
      </div>
      {side.items.slice(0, 3).map((item) => (
        <div
          key={item}
          style={{ fontFamily: bodyFont, fontWeight: 800, fontSize: 40, color: "#ffffff", textAlign: "center", lineHeight: 1.2 }}
        >
          {item}
        </div>
      ))}
    </div>
  );
};

const CompareView: React.FC<SceneProps<CompareScene>> = ({ scene, palette }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const versus = spring({ frame: frame - 18, fps, config: { damping: 6, stiffness: 200 } });
  return (
    <SceneEnter durationInFrames={scene.durationInFrames}>
      {scene.title && <PopWords text={scene.title} highlight={scene.highlight} accent={palette.accent} fontSize={88} />}
      <div style={{ position: "relative", display: "flex", gap: 30, width: "100%", alignItems: "stretch" }}>
        <SideColumn side={scene.left} color={palette.accent2} delay={4} from="left" />
        <SideColumn side={scene.right} color={palette.accent} delay={12} from="right" />
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            width: 130,
            height: 130,
            marginLeft: -65,
            marginTop: -65,
            borderRadius: "50%",
            background: "#ffffff",
            color: "#111111",
            display: "grid",
            placeItems: "center",
            fontFamily: displayFont,
            fontSize: 64,
            transform: `scale(${versus}) rotate(${(1 - versus) * 180}deg)`,
            boxShadow: "0 10px 0 rgba(0,0,0,0.3)",
          }}
        >
          VS
        </div>
      </div>
    </SceneEnter>
  );
};

const JourneyView: React.FC<SceneProps<JourneyScene>> = ({ scene, palette }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const travel = interpolate(frame, [12, Math.min(48, scene.durationInFrames - 8)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => t * t * (3 - 2 * t),
  });
  const arrive = spring({ frame: frame - Math.min(48, scene.durationInFrames - 8), fps, config: { damping: 6 } });
  const planeX = interpolate(travel, [0, 1], [150, 770]);
  const planeY = 300 - Math.sin(travel * Math.PI) * 220;
  const flag = (value: string, label: string, scale: number) => (
    <div style={{ textAlign: "center", transform: `scale(${scale})` }}>
      <div style={{ fontFamily: emojiFont, fontSize: 190, lineHeight: 1 }}>{value}</div>
      <div style={{ fontFamily: displayFont, fontSize: 56, color: "#ffffff", marginTop: 12, textTransform: "uppercase" }}>
        {label}
      </div>
    </div>
  );
  return (
    <SceneEnter durationInFrames={scene.durationInFrames}>
      <div style={{ position: "relative", width: 850, height: 510 }}>
        <svg width={850} height={460} style={{ position: "absolute", inset: 0 }}>
          <path
            d="M 150 300 Q 460 -140 770 300"
            stroke={palette.accent}
            strokeWidth={12}
            strokeDasharray="30 26"
            strokeDashoffset={-frame * 4}
            fill="none"
            opacity={0.9}
          />
        </svg>
        <div style={{ position: "absolute", left: 0, top: 200 }}>{flag(scene.from.flag, scene.from.label, 1)}</div>
        <div style={{ position: "absolute", right: 0, top: 200 }}>{flag(scene.to.flag, scene.to.label, 1 + arrive * 0.15)}</div>
        <div
          style={{
            position: "absolute",
            left: planeX - 60,
            top: planeY - 60,
            fontFamily: emojiFont,
            fontSize: 120,
            transform: `rotate(${interpolate(travel, [0, 0.5, 1], [-35, 0, 35])}deg)`,
          }}
        >
          {scene.emoji ?? "🚀"}
        </div>
      </div>
      <PopWords text={scene.text} highlight={scene.highlight} accent={palette.accent} fontSize={86} delay={8} />
      <Confetti colors={palette.blobs} delay={Math.min(48, scene.durationInFrames - 8)} x={840} y={560} count={45} />
    </SceneEnter>
  );
};

const StepsView: React.FC<SceneProps<StepsScene>> = ({ scene, palette }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <SceneEnter durationInFrames={scene.durationInFrames}>
      <PopWords text={scene.title} highlight={scene.highlight} accent={palette.accent} fontSize={90} />
      <div style={{ display: "flex", flexDirection: "column", gap: 24, width: "100%" }}>
        {scene.steps.slice(0, 4).map((step, index) => {
          const delay = revealDelay(index, scene.steps.length, scene.durationInFrames);
          const progress = spring({ frame: frame - delay, fps, config: { damping: 10 } });
          const color = [palette.accent, palette.accent2, palette.blobs[0], palette.blobs[2]][index % 4];
          return (
            <div
              key={step}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 28,
                transform: `scale(${progress})`,
                opacity: Math.min(progress * 2, 1),
              }}
            >
              <div
                style={{
                  flexShrink: 0,
                  width: 110,
                  height: 110,
                  borderRadius: "50%",
                  background: color,
                  display: "grid",
                  placeItems: "center",
                  fontFamily: displayFont,
                  fontSize: 68,
                  color: "#111111",
                  boxShadow: `0 0 36px ${color}`,
                }}
              >
                {index + 1}
              </div>
              <div style={{ fontFamily: bodyFont, fontWeight: 800, fontSize: 52, color: "#ffffff", lineHeight: 1.15 }}>
                {step}
              </div>
            </div>
          );
        })}
      </div>
    </SceneEnter>
  );
};

const QuestionView: React.FC<SceneProps<QuestionScene>> = ({ scene, palette }) => {
  const frame = useCurrentFrame();
  return (
    <SceneEnter durationInFrames={scene.durationInFrames}>
      <div
        style={{
          fontFamily: displayFont,
          fontSize: 340,
          lineHeight: 0.9,
          color: palette.accent,
          transform: `rotate(${Math.sin(frame / 6) * 10}deg) scale(${1 + Math.sin(frame / 5) * 0.05})`,
          textShadow: `0 0 70px ${palette.accent}`,
        }}
      >
        {scene.emoji ?? "?"}
      </div>
      <PopWords text={scene.text} highlight={scene.highlight} accent={palette.accent2} fontSize={100} />
    </SceneEnter>
  );
};

const RevealView: React.FC<SceneProps<RevealScene>> = ({ scene, palette }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const revealAt = Math.round(scene.durationInFrames * 0.4);
  const reveal = spring({ frame: frame - revealAt, fps, config: { damping: 8, stiffness: 200 } });
  return (
    <SceneEnter durationInFrames={scene.durationInFrames}>
      <BigEmoji emoji={scene.emoji} size={190} />
      <Subtitle text={scene.teaser} delay={4} />
      <div
        style={{
          position: "relative",
          padding: "30px 44px",
          borderRadius: 30,
          background: palette.accent,
          transform: `scale(${0.6 + reveal * 0.4}) rotate(${(1 - reveal) * -6}deg)`,
          boxShadow: `0 14px 0 rgba(0,0,0,0.3), 0 0 70px ${palette.accent}`,
        }}
      >
        <div
          style={{
            fontFamily: displayFont,
            fontSize: 104,
            lineHeight: 1.05,
            color: "#111111",
            textAlign: "center",
            textTransform: "uppercase",
            filter: `blur(${(1 - reveal) * 26}px)`,
          }}
        >
          {scene.reveal}
        </div>
      </div>
      <Confetti colors={palette.blobs} delay={revealAt} y={760} />
    </SceneEnter>
  );
};

const CtaView: React.FC<SceneProps<CtaScene>> = ({ scene, palette }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const button = spring({ frame: frame - 10, fps, config: { damping: 7 } });
  const pulse = 1 + Math.max(0, Math.sin(frame / 4)) * 0.07;
  return (
    <SceneEnter durationInFrames={scene.durationInFrames}>
      <BigEmoji emoji={scene.emoji ?? "🔔"} size={210} />
      <PopWords text={scene.text} highlight={scene.highlight} accent={palette.accent} fontSize={100} />
      <div
        style={{
          padding: "30px 70px",
          borderRadius: 999,
          background: "#ff0033",
          color: "#ffffff",
          fontFamily: bodyFont,
          fontWeight: 900,
          fontSize: 62,
          textTransform: "uppercase",
          transform: `scale(${button * pulse})`,
          boxShadow: "0 12px 0 #8a0018, 0 0 60px #ff0033",
        }}
      >
        {scene.subtext ?? "Segue pra mais"}
      </div>
      <Confetti colors={palette.blobs} delay={12} y={900} />
    </SceneEnter>
  );
};

export const SceneView: React.FC<{ scene: Scene; palette: Palette }> = ({ scene, palette }) => {
  switch (scene.type) {
    case "hook":
      return <HookView scene={scene} palette={palette} />;
    case "statement":
      return <StatementView scene={scene} palette={palette} />;
    case "stat":
      return <StatView scene={scene} palette={palette} />;
    case "list":
      return <ListView scene={scene} palette={palette} />;
    case "compare":
      return <CompareView scene={scene} palette={palette} />;
    case "journey":
      return <JourneyView scene={scene} palette={palette} />;
    case "steps":
      return <StepsView scene={scene} palette={palette} />;
    case "question":
      return <QuestionView scene={scene} palette={palette} />;
    case "reveal":
      return <RevealView scene={scene} palette={palette} />;
    case "cta":
      return <CtaView scene={scene} palette={palette} />;
  }
};
