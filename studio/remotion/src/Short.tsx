import { AbsoluteFill, Html5Audio, Sequence, staticFile } from "remotion";

import { Background } from "./components/Background";
import { Captions } from "./components/Captions";
import { Flash } from "./components/Flash";
import { ProgressBar } from "./components/ProgressBar";
import { getPalette } from "./palettes";
import { SceneView } from "./scenes";
import type { ShortProps } from "./types";

export const Short: React.FC<ShortProps> = ({ palette, scenes, music, musicVolume = 0.12 }) => {
  let from = 0;
  return (
    <AbsoluteFill style={{ background: "#000000" }}>
      {music && <Html5Audio src={staticFile(`music/${music}`)} volume={musicVolume} loop />}
      {scenes.map((scene, index) => {
        const scenePalette = getPalette(scene.palette ?? palette);
        const start = from;
        from += scene.durationInFrames;
        return (
          <Sequence key={index} from={start} durationInFrames={scene.durationInFrames} name={`${index + 1}. ${scene.type}`}>
            <Background palette={scenePalette} seed={`scene-${index}`} />
            <SceneView scene={scene} palette={scenePalette} />
            <Captions
              words={scene.words}
              highlight={scene.highlight}
              accent={scenePalette.accent}
              accent2={scenePalette.accent2}
            />
            <Flash />
            {scene.audio && <Html5Audio src={staticFile(scene.audio)} />}
            {scene.sfx && <Html5Audio src={staticFile(`sfx/${scene.sfx}.wav`)} volume={0.55} />}
          </Sequence>
        );
      })}
      <ProgressBar color={getPalette(palette).accent} />
    </AbsoluteFill>
  );
};
