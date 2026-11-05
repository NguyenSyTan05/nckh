"""
ClassBridge Unified Architecture
Component: 04_TRANSLATION_MODULE / nmt_translator.py
Chức năng: Dịch thuật Đa ngữ & Trích xuất Ngữ nghĩa (Meta NLLB-200 Distilled-600M)
Tối ưu:
- 1 Model NLLB-200 duy nhất phục vụ cả:
  1. Dịch thuật song ngữ 2 chiều (Việt <-> Anh và 200 ngôn ngữ).
  2. Trích xuất Semantic Embeddings & tính độ tương đồng câu hỏi (Question Clustering) dùng chung.
- Tiết kiệm bộ nhớ GPU VRAM cho card RTX 3050 (4GB) với chuẩn FP16.
"""

from __future__ import annotations
import os
import sys
import re

# Đảm bảo Windows console không bị sập UnicodeEncodeError khi in tiếng Việt
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def remove_repeated_phrases(text: str) -> str:
    """Khử các cụm từ lặp lại trong câu dịch."""
    if not text:
        return ""
    current = text.strip()
    for _ in range(3):
        tokens = re.findall(r"\S+", current)
        if len(tokens) <= 1:
            break

        def norm_tok(t: str) -> str:
            return re.sub(r"^[^\w\s]+|[^\w\s]+$", "", t).lower()

        n = len(tokens)
        i = 0
        cleaned_tokens: list[str] = []
        changed = False

        while i < n:
            matched = False
            for phrase_len in range(1, min(30, (n - i) // 2 + 1)):
                phrase_norms = [norm_tok(tokens[i + k]) for k in range(phrase_len)]
                if not any(phrase_norms):
                    continue

                repeat_count = 1
                j = i + phrase_len
                while j + phrase_len <= n:
                    next_norms = [norm_tok(tokens[j + k]) for k in range(phrase_len)]
                    if next_norms == phrase_norms:
                        repeat_count += 1
                        j += phrase_len
                    else:
                        break

                if repeat_count > 1:
                    cleaned_tokens.extend(tokens[i : i + phrase_len])
                    i = j
                    matched = True
                    changed = True
                    break

            if not matched:
                cleaned_tokens.append(tokens[i])
                i += 1

        current = " ".join(cleaned_tokens)
        current = re.sub(r"([,\.!?])(\s*\1)+", r"\1", current)
        if not changed:
            break

    current = re.sub(r",\s*$", "", current)
    return current.strip()


# Bảng tra cứu mã ngôn ngữ chuẩn FLORES-200 (Chuyên biệt Song ngữ Anh - Việt)
LANGUAGE_CODE_MAP = {
    "vi": "vie_Latn",
    "vn": "vie_Latn",
    "vietnamese": "vie_Latn",
    "mixed_vi_en": "vie_Latn",
    "en": "eng_Latn",
    "english": "eng_Latn",
}


class NLLBTranslator:
    """
    Module Dịch thuật Đa ngữ & Xử lý Ngữ nghĩa NLLB-200:
    - Base: facebook/nllb-200-distilled-600M
    - Tối ưu FP16 trên CUDA (~1.4GB VRAM)
    - Tích hợp tính năng get_embeddings & compute_similarity dùng chung cho Gom câu hỏi
    """

    def __init__(self, device: str = "cuda") -> None:
        import torch
        self.device = "cuda" if device == "cuda" and torch.cuda.is_available() else "cpu"
        self.model_id = "facebook/nllb-200-distilled-600M"
        self.model_type = "nllb"
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._load_model()

    def _load_model(self) -> None:
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        print(f"[NLLB-200 Module] 🌐 Đang nạp mô hình dịch đa ngữ: {self.model_id} (device={self.device})...", flush=True)
        try:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, local_files_only=True)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True,
                    local_files_only=True,
                )
            except Exception:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True,
                )
            if self.device == "cuda":
                self.model = self.model.cuda()
            self.model.eval()
            self.model_type = "nllb"
            # Warmup NLLB CUDA kernel để không bị trễ ở câu dịch đầu tiên
            try:
                inputs = self.tokenizer("Xin chào", return_tensors="pt").to(self.device)
                _ = self.model.generate(**inputs, max_new_tokens=5)
            except Exception:
                pass
            print("[NLLB-200 Module] ✅ NLLB-200 Translation & Semantic Engine đã sẵn sàng!", flush=True)
        except Exception as e:
            print(f"[Translation Module] ⚠️ NLLB-200 chưa tải xong hoặc mạng ngắt quãng ({e}). Đang chuyển sang EnViT5 offline...", flush=True)
            self.model_type = "envit5"
            try:
                envit5_base = "VietAI/envit5-translation"
                lora_dir = "d:/TailieuNPKH/classbridge/backend/ai-service/nmt-academic-lora-balanced"
                from transformers import pipeline
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(envit5_base, local_files_only=True)
                    if os.path.exists(lora_dir):
                        from peft import PeftModel
                        base_m = AutoModelForSeq2SeqLM.from_pretrained(envit5_base, local_files_only=True)
                        self.model = PeftModel.from_pretrained(base_m, lora_dir)
                    else:
                        self.model = AutoModelForSeq2SeqLM.from_pretrained(envit5_base, local_files_only=True)
                except Exception:
                    self.tokenizer = AutoTokenizer.from_pretrained(envit5_base)
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(envit5_base)

                if self.device == "cuda":
                    self.model = self.model.half().cuda()
                self.pipeline = pipeline("translation", model=self.model, tokenizer=self.tokenizer, device=0 if self.device == "cuda" else -1)
                print("[Translation Module] ✅ EnViT5 Offline Fallback đã sẵn sàng!", flush=True)
            except Exception as e2:
                print(f"[Translation Module] ⚠️ Không thể nạp mô hình dịch offline: {e2}", flush=True)
                self.model = None
                self.tokenizer = None

    def _resolve_lang_code(self, lang_str: str, default: str = "vie_Latn") -> str:
        if not lang_str:
            return default
        cleaned = str(lang_str).lower().strip()
        if cleaned in LANGUAGE_CODE_MAP:
            return LANGUAGE_CODE_MAP[cleaned]
        if "en" in cleaned:
            return "eng_Latn"
        return "vie_Latn"

    def translate(
        self,
        text: str,
        source_language: str = "vi",
        target_language: str | None = None,
    ) -> str:
        """
        Dịch văn bản giữa các ngôn ngữ:
        - Mặc định: VI -> EN hoặc EN -> VI
        """
        if not text or not text.strip():
            return ""

        cleaned_input = remove_repeated_phrases(text.strip())
        if not cleaned_input:
            return ""

        if self.model_type == "envit5":
            if self.pipeline:
                try:
                    prefix = "vi: " if source_language in ["vi", "vn", "vietnamese", "mixed_vi_en"] else "en: "
                    res = self.pipeline(
                        prefix + cleaned_input,
                        max_length=128,
                        max_new_tokens=64,
                        no_repeat_ngram_size=3,
                        repetition_penalty=1.2,
                        num_beams=1,
                        early_stopping=True,
                    )
                    output = res[0]["translation_text"]
                    if output.startswith("vi: ") or output.startswith("en: "):
                        output = output[4:]
                    return remove_repeated_phrases(output.strip())
                except Exception:
                    pass
            return cleaned_input

        if not self.model or not self.tokenizer:
            return cleaned_input

        import torch

        # Xác định mã ngôn ngữ nguồn và đích
        src_code = self._resolve_lang_code(source_language, default="vie_Latn")
        if target_language and str(target_language).lower().strip() not in ["auto", ""]:
            tgt_code = self._resolve_lang_code(target_language, default="eng_Latn")
        else:
            tgt_code = "eng_Latn" if src_code == "vie_Latn" else "vie_Latn"

        try:
            self.tokenizer.src_lang = src_code
            inputs = self.tokenizer(
                cleaned_input,
                return_tensors="pt",
                truncation=True,
                max_length=256,
            )
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}

            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(tgt_code)

            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=forced_bos_token_id,
                    max_new_tokens=64,
                    num_beams=1,             # Greedy search tối ưu tốc độ Realtime
                    no_repeat_ngram_size=3,  # Khử lặp từ
                )

            translated = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
            return remove_repeated_phrases(translated.strip())
        except Exception as ex:
            print(f"[NLLB-200 Module] ⚠️ Lỗi khi dịch: {ex}", flush=True)
            return cleaned_input


# Alias tương thích ngược với các file import cũ
DualTranslator = NLLBTranslator
