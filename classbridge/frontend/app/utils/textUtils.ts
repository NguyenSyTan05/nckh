/**
 * ClassBridge - Lightweight Frontend Text Utilities
 * Minimal NFC normalization and string helpers.
 * Deduplication and stabilization are handled centrally on the backend.
 */

export function normalizeVietnameseUnicode(text: string): string {
  if (!text) return "";
  return text.normalize("NFC");
}

export function cleanRepetitions(text: string): string {
  if (!text) return "";
  const normalized = normalizeVietnameseUnicode(text).trim();
  if (!normalized) return "";
  return normalized
    .replace(/(?<=^|\s)(\p{L}+)(?:\s+\1)+(?=\s|$)/giu, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

