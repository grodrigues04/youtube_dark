import { Composition, Still } from "remotion";

import { Short } from "./Short";
import { Thumbnail } from "./Thumbnail";
import type { ShortProps, ThumbnailProps } from "./types";

const FPS = 30;

const exampleShort: ShortProps = {
  fps: FPS,
  palette: "neon",
  scenes: [
    {
      type: "hook",
      text: "Isso está bombando no Japão",
      highlight: ["Japão"],
      emoji: "🤯",
      sfx: "boom",
      narration: "Isso está bombando no Japão.",
      durationInFrames: 60,
      audio: "",
      words: [],
    },
  ],
};

const exampleThumbnail: ThumbnailProps = {
  title: "Isso vai chegar no Brasil",
  highlight: ["Brasil"],
  emoji: "🚀",
  badge: "🇯🇵 → 🇧🇷",
  palette: "sunset",
};

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Short"
      component={Short}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={60}
      defaultProps={exampleShort}
      calculateMetadata={({ props }) => ({
        fps: props.fps,
        durationInFrames: Math.max(1, props.scenes.reduce((total, scene) => total + scene.durationInFrames, 0)),
      })}
    />
    <Still id="Thumbnail" component={Thumbnail} width={1080} height={1920} defaultProps={exampleThumbnail} />
  </>
);
