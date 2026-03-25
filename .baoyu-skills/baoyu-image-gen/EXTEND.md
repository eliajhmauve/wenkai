---
version: 1
default_provider: google
default_quality: 2k
default_aspect_ratio: "1:1"
default_image_size: 2K
default_model:
  google: "gemini-3-flash-image-preview"
batch:
  max_workers: 3
  provider_limits:
    google:
      concurrency: 2
      start_interval_ms: 2000
---
