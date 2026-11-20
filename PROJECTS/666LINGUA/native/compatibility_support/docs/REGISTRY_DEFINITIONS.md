# Registerdefinitionen v1.2.4

## TERM_REGISTRY

- source_term
- target_profile
- preferred_translation
- forbidden_translation
- case_sensitive
- domain

## DO_NOT_TRANSLATE_REGISTRY

- exact_token
- token_type
- preserve_case

## RELATIONSHIP_REGISTRY

- person_id
- relationship_type
- closeness_level
- formality
- address_style
- pet_names_allowed

## SPEAKER_REGISTRY

- speaker_id
- language_profile
- pronouns
- role

## Regeln

- Keine Ableitung von Geschlecht oder Identität allein aus Namen.
- Keine stillen Registeränderungen.
- Änderungen werden als Delta protokolliert und auditiert.
- Register werden im Checkpoint nur über notwendige Einträge oder Hashes referenziert.


## START_ALIAS_REGISTRY

```text
ROOT_ID
ALIAS_PROFILE
EXACT_COMMAND
LANGUAGE_HINT
AUTOSELECT_SYSTEM_LANGUAGE=false
ACTIVE
```

Das Register enthält ausschließlich Eingabealiase für denselben Bootstrap-Root.
