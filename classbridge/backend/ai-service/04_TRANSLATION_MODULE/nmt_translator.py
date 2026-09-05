"""
ClassBridge 2-Module Architecture
Component: 04_TRANSLATION_MODULE / nmt_translator.py
Chức năng: Dịch thuật song ngữ 2 chiều (EnViT5 LoRA).
VI -> EN (chuẩn học thuật CNTT) & EN -> VI (tự nhiên, chính xác).
"""

from __future__ import annotations
import os
from pathlib import Path


class DualTranslator:
    def __init__(self, device: str = "cuda") -> None:
        self.device = device
        self.model_dir = "d:/TailieuNPKH/classbridge/backend/ai-service/nmt-academic-lora-balanced"
        self.pipeline = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            print(f"[Translation Module] 🌐 Nạp mô hình Dịch thuật EnViT5 LoRA từ: {self.model_dir}")
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
            base_model = "VietAI/envit5-translation"
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            
            if os.path.exists(self.model_dir):
                from peft import PeftModel
                model = AutoModelForSeq2SeqLM.from_pretrained(base_model)
                model = PeftModel.from_pretrained(model, self.model_dir)
            else:
                model = AutoModelForSeq2SeqLM.from_pretrained(base_model)
                
            if self.device == "cuda":
                model = model.half().cuda()

            self.pipeline = pipeline("translation", model=model, tokenizer=tokenizer, device=0 if self.device == "cuda" else -1)
            print("[Translation Module] ✅ EnViT5 Translation đã sẵn sàng!")
        except Exception as e:
            print(f"[Translation Module] ⚠️ Nạp EnViT5 offline: {e}")
            self.pipeline = None

    def translate(self, text: str, source_language: str) -> str:
        if not text or not text.strip():
            return ""
        
        prefix = "vi: " if source_language == "vi" else "en: "
        input_text = prefix + text.strip()
        
        if self.pipeline:
            try:
                res = self.pipeline(input_text, max_length=512, max_new_tokens=256)
                output = res[0]["translation_text"]
                if output.startswith("vi: ") or output.startswith("en: "):
                    output = output[4:]
                return output.strip()
            except Exception:
                pass
        
        return f"[Dịch {source_language.upper()}] {text.strip()}"
