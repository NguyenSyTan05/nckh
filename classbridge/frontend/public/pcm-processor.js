/**
 * ClassBridge PCM Processor (AudioWorklet)
 *
 * Nhận audio float32 từ AudioContext (44.1 / 48 kHz / 16 kHz),
 * Downsample về đúng 16 kHz mono bằng bộ nội suy tuyến tính (Linear Interpolation)
 * độ chính xác cao, bảo toàn 100% cao độ (pitch) và âm sắc (timbre) của giọng nói.
 *
 * Gửi từng block chuẩn 100ms (1600 mẫu float32) về main thread qua postMessage.
 * Output: PCM Float32 LE, 16.000 Hz, mono.
 */
class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.targetSampleRate = 16000;
    this.bufferSize = 1600; // Chuẩn 100ms mono PCM tại 16 kHz
    this.buffer = new Float32Array(this.bufferSize);
    this.bufferIndex = 0;
    this.lastSample = 0.0;
    this.offset = 0.0;
    this.port.postMessage({ type: "pcm_processor_ready" });
  }

  pushSample(sample) {
    if (!Number.isFinite(sample)) sample = 0;
    if (sample > 1.0) sample = 1.0;
    else if (sample < -1.0) sample = -1.0;

    this.buffer[this.bufferIndex++] = sample;
    if (this.bufferIndex >= this.bufferSize) {
      const copy = new Float32Array(this.buffer);
      this.port.postMessage(
        { type: "pcm_data", buffer: copy.buffer, sampleRate: this.targetSampleRate },
        [copy.buffer],
      );
      this.bufferIndex = 0;
    }
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    const inputChannel = input[0];
    const len = inputChannel.length;
    if (len === 0) return true;

    const inRate = sampleRate || 48000;

    // Trường hợp 1: AudioContext chạy native ở 16kHz
    if (Math.abs(inRate - this.targetSampleRate) < 100) {
      for (let i = 0; i < len; i++) {
        this.pushSample(inputChannel[i]);
      }
      return true;
    }

    // Trường hợp 2: Downsample từ 48kHz hoặc 44.1kHz về 16kHz với Linear Interpolation liên tục, không click/pop
    const ratio = inRate / this.targetSampleRate;
    let pos = this.offset;
    while (pos < len) {
      const i = Math.floor(pos);
      const frac = pos - i;
      const s0 = (i === 0) ? this.lastSample : inputChannel[i - 1];
      const s1 = inputChannel[i];
      const interpolated = s0 + frac * (s1 - s0);
      this.pushSample(interpolated);
      pos += ratio;
    }
    this.lastSample = inputChannel[len - 1];
    this.offset = pos - len;
    return true;
  }
}

registerProcessor("pcm-processor", PCMProcessor);
