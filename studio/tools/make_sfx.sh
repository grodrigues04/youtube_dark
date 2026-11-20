#!/usr/bin/env bash
# Synthesizes the sound effects with ffmpeg at image build time (no third-party audio files).
set -euo pipefail
OUT="${1:?usage: make_sfx.sh <output_dir>}"
mkdir -p "$OUT"
synth() { ffmpeg -loglevel error -y -f lavfi -i "aevalsrc=$2:s=44100:d=$3" -af "$4" "$OUT/$1.wav"; }
synth pop    '0.8*sin(2*PI*(500+1800*exp(-28*t))*t)*exp(-22*t)' 0.25 'volume=1'
synth ding   '0.5*sin(2*PI*1320*t)*exp(-5*t)+0.3*sin(2*PI*1980*t)*exp(-7*t)' 1.0 'volume=1'
synth riser  '0.35*sin(2*PI*(180+700*t*t)*t)*min(1\,t*1.5)' 1.0 'afade=t=out:st=0.85:d=0.15'
synth boom   '0.9*sin(2*PI*(45+140*exp(-9*t))*t)*exp(-3.5*t)' 1.0 'lowpass=f=600,volume=1.6'
ffmpeg -loglevel error -y -f lavfi -i "anoisesrc=d=0.7:c=pink:a=0.7:r=44100" \
  -af "bandpass=f=1400:w=1200,afade=t=in:d=0.3,afade=t=out:st=0.35:d=0.35,volume=1.8" "$OUT/whoosh.wav"
ls "$OUT"
