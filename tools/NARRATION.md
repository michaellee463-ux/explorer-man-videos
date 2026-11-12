# Narration rules (Explorer Man)

Voice: Kokoro **am_puck** (chosen by Michael, Nov 2026). Speed about 1.0 (up to 1.05 only to fit length).

Setup (fresh machine):
```
pip install --break-system-packages kokoro-onnx soundfile
mkdir -p ~/kokoro && cd ~/kokoro
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
Use `tools/voice.py`: `from voice import say, phonemes` → `w, sr = say(text, "am_puck")`.

Sound like a human narrator:
- Write for the ear: short sentences, commas where a person would breathe, "..." for a dramatic beat, a question mark for hooks.
- Leave a breath between lines (about 0.3–0.4 s), longer (about 0.5–0.6 s) after the hook and after a big reveal.
- Pronunciation pass on EVERY line before rendering: run `phonemes(line)` and read the output. Check letters used as names (group A, vitamin C, type O → spoken as letters; voice.py handles common cases), acronyms (add to LEX), numbers, units, years, and unusual or scientific words. Fix with LEX or by rewording, then re-check.
- Write numbers the way they should be said ("about four point two light-years", "two thousand twenty-six"), not as digits or symbols.
