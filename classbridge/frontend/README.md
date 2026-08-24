# ClassBridge MVP

ClassBridge follows multiple speakers from one shared microphone as stable continuous streams. Local voice features assign `Người 1`, `Người 2`, … automatically; audio windows close at natural pauses, and overlapping recognition windows are reconciled before display:

`Microphone / browser-tab audio → Faster-Whisper → optional LLM correction → EnViT5 → bilingual subtitles`

The browser uses the default microphone and preserves every completed utterance in order. No microphone or language selection is required. The AI service distinguishes turn-taking speakers locally and detects only English or Vietnamese for automatic translation in the opposite direction. English and Vietnamese have fixed columns; whichever column contains the spoken source is highlighted. A pause, speaker change, language change, or long paragraph starts a new display line. A single mono microphone cannot reliably separate voices that speak at exactly the same time. The MVP writes no original audio and stores no transcript database.

## Run locally

### Run web and AI together (recommended)

```powershell
npm install
npm run dev
```

This command starts the web application, starts the Python AI service from
`ai-service/.venv`, checks port 8000, and automatically restarts AI if it exits.
The first startup can take about one minute while local models are loaded.

### Run each service manually

#### 1. AI service

```powershell
cd ai-service
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:MODEL_MODE="local"
$env:WHISPER_MODEL="base"
$env:WHISPER_ACCURATE_MODEL="small"
$env:WHISPER_CPU_THREADS="4"
$env:WHISPER_NUM_WORKERS="3"
$env:WHISPER_ACCURATE_WORKERS="1"
$env:WHISPER_ACCURATE_THREADS="4"
$env:CLASSBRIDGE_OPENBLAS_THREADS="1"
$env:CLASSBRIDGE_OMP_THREADS="4"
$env:CLASSBRIDGE_MKL_THREADS="4"
$env:WHISPER_BEAM_SIZE="1"
$env:WHISPER_MUSIC_BEAM_SIZE="1"
$env:WHISPER_ACCURATE_BEAM_SIZE="2"
$env:WHISPER_RETRY_CONFIDENCE="0.30"
$env:WHISPER_VI_RETRY_CONFIDENCE="0.34"
$env:WHISPER_WARMUP="true"
$env:SPEAKER_SIMILARITY_THRESHOLD="0.84"
$env:SPEAKER_CONTINUITY_THRESHOLD="0.76"
$env:MAX_SPEAKERS_PER_SESSION="8"
$env:TRANSLATION_CPU_THREADS="3"
$env:TRANSLATION_NUM_BEAMS="1"
$env:TRANSLATION_QUANTIZATION="int8"
uvicorn main:app --reload --port 8000
```

The first real-mode startup downloads Whisper and EnViT5. Direct microphone
speech uses a `hybrid` recognition profile. The shared stream closes early at
a real pause or after about 1 second, displays source text first, and starts
translation immediately on a separate low-thread worker. Language is detected
automatically for every window and restricted to English or Vietnamese. The
Small accuracy retry is reserved for genuinely uncertain, non-trivial text. Browser-tab
music keeps its separate clean digital capture. Timer-only windows from the
same speaker stay on one line, while an acoustic pause starts a new line.
Speaker numbers come from local voice matching on the shared microphone.
Microphone windows are processed in capture order so identities stay stable.
Words masked by instruments still cannot be recovered perfectly.

#### 2. Web application

Open another terminal:

```powershell
npm install
npm run dev:web
```

Visit the local URL printed by the development server and press the listening
button. ClassBridge uses the system's default microphone and automatically
labels turn-taking speakers; no person or language setup is needed. Use
**Tab / nhạc** when sound is playing in the same computer; digital tab capture
remains the most accurate choice for lyrics.

## Realtime streaming pipeline

The live path is `AudioWorklet → mono float32 PCM 16 kHz → WebSocket → VAD →
5-second rolling buffer → fast ASR partials`. The UI receives a partial update
about every 300–700 ms. A pause finalizes the original transcript first; an
optional accurate GPU pass may refine that final line, then translation runs on
a separate queue and arrives as its own message. REST audio uploads are used
only when the WebSocket cannot connect or disconnects during a class.

Important tuning variables:

```powershell
$env:STREAM_UPDATE_SECONDS="0.5"
$env:STREAM_ROLLING_SECONDS="5"
$env:STREAM_FINAL_SILENCE_SECONDS="0.7"
$env:STREAM_PRE_ROLL_SECONDS="0.25"
$env:STREAM_POST_ROLL_SECONDS="0.5"
$env:STREAM_FINAL_ACCURATE="true" # recommended on a GPU server
```

The local supervisor listens on `0.0.0.0:8000` so students on the same trusted
LAN can open `/join/DTU-xxx`. The browser automatically uses the website host
for the AI WebSocket. For a deployed HTTPS site, set
`NEXT_PUBLIC_AI_SERVICE_URL` to the public HTTPS/WSS AI endpoint. Course and
topic hints for the optional context-aware LLM translation review can be set
with `TRANSLATION_COURSE_CONTEXT` and `TRANSLATION_TOPIC_CONTEXT`.

## LLM correction

LLM correction is optional. Point `LLM_BASE_URL` at any OpenAI-compatible `/v1` API, for example a local vLLM or LM Studio server. If it is empty, the Whisper transcript is passed directly to EnViT5.

### Train the lightweight correction memory

When Whisper repeatedly writes the same phrase incorrectly, record only
verified text pairs (no audio is stored by this module):

```json
{"raw":"nhận dạng dọng nói","corrected":"nhận dạng giọng nói","language":"vi"}
```

Provide at least two examples of each repeated error, then train and restart AI:

```powershell
python training/train_correction_memory.py --input data/correction-pairs.jsonl --output ai-service/correction-memory.json
```

Only substitutions with at least two examples and 80% agreement are loaded.
For acoustic improvement across accents and speakers, use the Whisper LoRA
workflow below; it requires consented audio with verbatim transcripts.

## Multilingual, multi-voice fine-tuning

Training stays outside the live request pipeline. Use only recordings whose
speakers consented to model training, and verify every transcript word for word.
Each JSONL row identifies its language, speaker and accent:

```json
{"audio":"data/clip-001.wav","text":"Hôm nay chúng ta học về cơ sở dữ liệu.","language":"vi","speaker_id":"teacher-01","accent":"vi-central"}
{"audio":"data/clip-002.wav","text":"Today we study database normalization.","language":"en","speaker_id":"teacher-02","accent":"en-vietnamese"}
```

Add rows with other Whisper ISO language codes to preserve and improve those
languages too. Include quiet/loud microphones, regional accents, non-native
English, classroom noise and clean speech. Keep music/instrumental audio out of
the speech fine-tune unless the transcript contains verified sung words.

Create a speaker-disjoint split, then train the multilingual Base LoRA:

```powershell
pip install -r training/requirements.txt
python training/prepare_multilingual_manifest.py --input data/all.jsonl --train data/train.jsonl --validation data/validation.jsonl
python training/finetune_whisper_lora.py --train data/train.jsonl --validation data/validation.jsonl --language multilingual
```

The trainer balances languages, caps over-represented speakers, and simulates
different volume, noise and speaking rates. Validation speakers never appear in
training, so WER/CER reflect recognition of new voices instead of memorisation.

### Compare pipeline variants before promoting a LoRA adapter

After you have a held-out multilingual evaluation manifest, compare the four
important variants with the same speaker-disjoint test set:

```powershell
python training/evaluate_pipeline_variants.py --input data/evaluation/manifest.jsonl --output data/evaluation/results.csv
```

The script reports the mean WER, CER, BLEU, chrF and latency for:

1. Whisper + EnViT5
2. Whisper + Correction Memory + EnViT5
3. Whisper LoRA + Correction Memory + EnViT5
4. Whisper LoRA + Correction Memory + EnViT5 + AI review

Only promote the LoRA adapter when Vietnamese/English WER/CER, terminology
recall and end-to-end latency all improve on the same held-out set.

Export the best adapter to CTranslate2 for the live service:

```powershell
python training/export_whisper_lora.py --adapter outputs/whisper-classbridge-base-multilingual-lora --ct2-output outputs/whisper-classbridge-base-ct2
$env:WHISPER_MODEL="outputs/whisper-classbridge-base-ct2"
```

Restart the AI service and compare the original Base model with the tuned model
on the same held-out test set. Promote it only when Vietnamese WER/CER, English
WER, terminology recall and end-to-end latency all meet the target. For a first
useful run, collect multiple speakers per language/accent; more diverse verified
voices matter more than repeatedly recording one person.
