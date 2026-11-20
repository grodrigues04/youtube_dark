// Contract between tools/prepare.py (writes props.json) and the compositions.
// The scene fields are written by Claude in video.json; prepare.py adds the timing fields.

export type PaletteName = "neon" | "sunset" | "ocean" | "candy" | "lime" | "fire";

export type Word = { text: string; startFrame: number; endFrame: number };

export type ListItem = { emoji?: string; text: string };

export type Side = { title: string; emoji?: string; items: string[] };

type SceneBase = {
  // Spoken text (pt-BR); turned into audio + word-synced captions by prepare.py
  narration: string;
  // Words of the narration painted with the accent color in the captions
  highlight?: string[];
  emoji?: string;
  sfx?: "whoosh" | "pop" | "ding" | "riser" | "boom" | null;
  palette?: PaletteName;
  // Added by prepare.py
  durationInFrames: number;
  audio: string;
  words: Word[];
};

export type HookScene = SceneBase & { type: "hook"; text: string };
export type StatementScene = SceneBase & { type: "statement"; title: string; subtitle?: string };
export type StatScene = SceneBase & {
  type: "stat";
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  label: string;
};
export type ListScene = SceneBase & { type: "list"; title: string; items: ListItem[] };
export type CompareScene = SceneBase & { type: "compare"; title?: string; left: Side; right: Side };
export type JourneyScene = SceneBase & {
  type: "journey";
  from: { flag: string; label: string };
  to: { flag: string; label: string };
  text: string;
};
export type StepsScene = SceneBase & { type: "steps"; title: string; steps: string[] };
export type QuestionScene = SceneBase & { type: "question"; text: string };
export type RevealScene = SceneBase & { type: "reveal"; teaser: string; reveal: string };
export type CtaScene = SceneBase & { type: "cta"; text: string; subtext?: string };

export type Scene =
  | HookScene
  | StatementScene
  | StatScene
  | ListScene
  | CompareScene
  | JourneyScene
  | StepsScene
  | QuestionScene
  | RevealScene
  | CtaScene;

export type ShortProps = {
  fps: number;
  palette: PaletteName;
  music?: string | null;
  musicVolume?: number;
  scenes: Scene[];
};

export type ThumbnailProps = {
  title: string;
  highlight?: string[];
  subtitle?: string;
  emoji?: string;
  badge?: string;
  palette: PaletteName;
};
