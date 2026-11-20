# Private / Manual Chat Import — v1.7.0

## Goal

v1.7.0 extends ChatBackup so private ChatGPT conversations can be archived without pretending that a private `/c/` URL is publicly downloadable. The application never bypasses ChatGPT authentication and never copies session cookies.

## Private chat workflow

1. Open the private chat in ChatGPT while authenticated.
2. Copy the complete visible conversation text.
3. In ChatBackup choose **Private / Manual** or press `Ctrl+Shift+V`.
4. Paste/import is analyzed immediately.
5. Explicit role markers are recovered into structured messages when possible.
6. If role markers are insufficient, the complete pasted text is preserved as one manual message. No turns are invented.

Recognized role markers include English and German forms such as `You said`, `User`, `Benutzer`, `Du`, `ChatGPT said`, `ChatGPT`, `Assistant`, `Assistent`, including Markdown heading forms.

## Manual analysis output

The `manual-transcript` parser creates machine-readable messages with:

- stable synthetic message IDs (`manual-0001`, ...)
- role / author
- rendered text
- original pasted source text in `rawContent.sourceText`
- manual-import metadata
- statically detected Copy/UI fields
- warnings

Manual analyses are available to the Structure Inspector and to JSON/JSONL/Portable exports. Markdown is rebuilt from recovered message structure; TXT/JavaScript use normalized transcript content.

## Chat-full share-link recovery guidance

The integrated bilingual help documents an observed, non-guaranteed ChatGPT behavior: when a conversation is reported as full, sending one additional short prompt can sometimes cause ChatGPT to process again, during which the Share / Copy link control may briefly become available. The user must copy the share link during that short window. This behavior is explicitly documented as opportunistic and version-dependent, not as a supported API contract.

If the temporary share window is unavailable, the private/manual workflow is the supported fallback.

## Privacy boundary

Public Share links can be accessible to anyone who receives the URL. The help explicitly recommends removing or disabling the share when it is no longer needed for sensitive content.
