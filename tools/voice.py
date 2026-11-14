"""Natural narration for Explorer Man (Kokoro TTS).
- Letters used as names (group A, vitamin C, type O, plan B...) are spoken as letters.
- Acronyms in ALL CAPS (WHO, DNA, NASA) are passed through the lexicon below.
- Pauses: commas/ellipses inside sentences; sentence_pause between sentences.
"""
import re, numpy as np
from kokoro_onnx import Kokoro
import os
MD = os.environ.get("KOKORO_DIR", os.path.expanduser("~/kokoro"))
K = Kokoro(f"{MD}/kokoro-v1.0.onnx", f"{MD}/voices-v1.0.bin")
LETTER = dict(A="ˈeɪ", B="bˈiː", C="sˈiː", D="dˈiː", E="ˈiː", F="ˈɛf", G="dʒˈiː", H="ˈeɪtʃ", I="ˈaɪ", J="dʒˈeɪ", K="kˈeɪ", L="ˈɛl", M="ˈɛm", N="ˈɛn", O="ˈoʊ", P="pˈiː", Q="kjˈuː", R="ˈɑːɹ", S="ˈɛs", T="tˈiː", U="jˈuː", V="vˈiː", W="dˈʌbəljuː", X="ˈɛks", Y="wˈaɪ", Z="zˈiː")
# words after which a lone capital letter is a name, not the article "a"
NAME_BEFORE = r"(group|type|vitamin|hepatitis|class|plan|grade|streptolysin|blood type|section|point|exhibit|letter|strain|lane|row|zone|phase|stage|level)"
LEX = {"WHO": "dˈʌbəljuː ˈeɪtʃ ˈoʊ", "DNA": "dˈiː ˈɛn ˈeɪ", "RNA": "ˈɑːɹ ˈɛn ˈeɪ", "Tempel": "tˈɛmpəl"}

def phonemes(text, lang="en-us"):
    marks = {}
    def sub(m):
        key = f"zqx{len(marks)}q"; marks[key] = LETTER[m.group(2)]; return m.group(1) + " " + key
    t = re.sub(NAME_BEFORE + r"\s+([A-Z])\b", sub, text, flags=re.I)
    for w, ph in LEX.items():
        if re.search(rf"\b{w}\b", t):
            key = f"zqx{len(marks)}q"; marks[key] = ph; t = re.sub(rf"\b{w}\b", key, t)
    ph = K.tokenizer.phonemize(t, lang)
    for key, p in marks.items():
        kp = K.tokenizer.phonemize(key, lang).strip(" .")
        ph = ph.replace(kp, p)
        assert p in ph, f"pronunciation fix failed for {key}"
    return ph

def say(text, voice="am_puck", speed=1.0, lang="en-us"):
    w, sr = K.create(phonemes(text, lang), voice=voice, speed=speed, lang=lang, is_phonemes=True,
                     sentence_pause=0.32, clause_pause=0.12)
    a = np.abs(w); idx = np.where(a > 0.01)[0]
    return w[max(0, idx[0] - 240): idx[-1] + 2400], sr
