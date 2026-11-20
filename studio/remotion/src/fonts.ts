import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";

export const { fontFamily: displayFont } = loadAnton("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] });
export const { fontFamily: bodyFont } = loadMontserrat("normal", {
  weights: ["700", "800", "900"],
  subsets: ["latin", "latin-ext"],
});

export const emojiFont = '"Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", sans-serif';
