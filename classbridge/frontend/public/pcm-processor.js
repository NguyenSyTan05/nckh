/**
 * ClassBridge PCM Processor (AudioWorklet)
 *
 * Nhận audio float32 từ AudioContext (44.1/48 kHz), downsample về 16 kHz mono
 * và gửi từng block 100 ms (1600 samples) về main thread qua postMessage.
 * Main thread sẽ forward buffer này qua WebSocket tới AI service.
 *
 * Output format: PCM float32 LE, 16 kHz, mono – đúng protocol
 * mà backend /ws/stream/{session_id} mong đợi.
 */
class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.targetSampleRate = 16000;
    this.bufferSize = 1600; // 100 ms of mono PCM at 16 kHz
    this.buffer = new Float32Array(this.bufferSize);
    this.bufferIndex = 0;
    this.resamplePhase = 0;
    this.resampleSum = 0;
    this.resampleCount = 0;
    this.sentBlocks = 0;
    // Báo cho main thread biết worklet đã sống và xử lý audio thật.
    this.port.postMessage({ type: "pcm_processor_ready" });
  }

  pushSample(sample) {
    // Clamp giá trị float về [-1, 1] để tránh NaN/Inf làm hỏng ASR phía server.
    if (!Number.isFinite(sample)) sample = 0;
    if (sample > 1) sample = 1;
    else if (sample < -1) sample = -1;

    this.buffer[this.bufferIndex++] = sample;
    if (this.bufferIndex < this.bufferSize) return;

    const copy = new Float32Array(this.buffer);
    this.port.postMessage(
      { type: "pcm_data", buffer: copy.buffer, sampleRate: this.targetSampleRate },
      [copy.buffer],
    );
    this.bufferIndex = 0;
    this.sentBlocks += 1;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    const inputChannel = input[0];
    if (sampleRate <= this.targetSampleRate) {
      for (let i = 0; i < inputChannel.length; i++) {
        this.pushSample(inputChannel[i]);
      }
      return true;
    }

    // AudioContext normally runs at 44.1/48 kHz. Downsample in the worklet so
    // the server always receives the 16 kHz float32 stream declared by the
    // WebSocket protocol. Averaging each source interval also acts as a small
    // anti-aliasing filter and works for non-integer ratios such as 44.1 kHz.
    const phaseStep = this.targetSampleRate / sampleRate;
    for (let i = 0; i < inputChannel.length; i++) {
      this.resampleSum += inputChannel[i];
      this.resampleCount += 1;
      this.resamplePhase += phaseStep;
      if (this.resamplePhase >= 1) {
        this.pushSample(this.resampleSum / this.resampleCount);
        this.resamplePhase -= 1;
        this.resampleSum = 0;
        this.resampleCount = 0;
      }
    }

    return true;
  }
}

registerProcessor("pcm-processor", PCMProcessor);
