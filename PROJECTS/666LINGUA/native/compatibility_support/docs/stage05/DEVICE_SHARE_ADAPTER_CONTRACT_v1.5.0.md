# Device and Share Adapter Contract v1.5.0

## Unterstützte Hüllen

### Eingabe

- TEXT_INPUT
- ASR_INPUT
- CLIPBOARD_INPUT
- DOCUMENT_INPUT

### Ausgabe

- SHARE_OUTPUT
- WHATSAPP_SHARE
- GENERIC_MESSENGER_SHARE
- COPY_TO_CLIPBOARD

## Trennung

Die Übersetzung, beide Companion-Ausgaben, Confidence-Evidenz und Adaptermetadaten bleiben getrennte Felder.

## Aussagegrenze

```text
DEVICE_RUNTIME_VERIFIED=false
IOS_TEST=NOT_PERFORMED
ANDROID_TEST=NOT_PERFORMED
WHATSAPP_UI_TEST=NOT_PERFORMED
```

Der Vertrag definiert die Datenform, behauptet aber keinen erfolgreichen Endgerätetest.
