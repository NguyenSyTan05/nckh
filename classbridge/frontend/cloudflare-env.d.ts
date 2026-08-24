/// <reference types="@cloudflare/workers-types" />

declare namespace Cloudflare {
  interface Env {
    /** Present only when `.openai/hosting.json` enables the logical DB binding. */
    DB?: D1Database;
  }
}
