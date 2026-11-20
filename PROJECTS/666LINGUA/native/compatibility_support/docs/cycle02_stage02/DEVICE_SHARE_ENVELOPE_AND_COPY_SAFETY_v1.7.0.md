# Device/Share Envelope and Copy Safety v1.7.0

The adapter receives finalized output only.

Envelope fields: `output_id`, `output_hash`, `language_profile`, `format_profile`, `share_target_class`, `copy_mode`, `created_at`.

Rules:
- no source text unless explicitly requested;
- no framework instructions or hidden metadata in shared content;
- writing-block/share UI is presentation, not semantic transformation;
- iOS, Android and WhatsApp behavior remains `REAL_DEVICE_TEST_PENDING`;
- copy/share failure never changes the translated text.
