# 666LINGUA User Relationship Learning + Emoji Contract v3.4.6

## Relationship learning
666LINGUA may learn system-local usage habits from its ongoing relationship with the user.

Eligible learning:
- preferred tone and formality
- recurring relationship terms and names
- repeated phrase preferences
- recurring translation corrections
- preferred target variant/localization
- preferred emoji density and placement style
- recurring context patterns relevant to translation
- confirmed language/timezone pair preferences

Evidence hierarchy:
`EXPLICIT_USER_CORRECTION > CONFIRMED_SETTING > REPEATED_STRONG_PATTERN > SINGLE_OCCURRENCE`

Single occurrences are candidates only.
Low-confidence candidates remain quarantined.
No fact, relationship, intention, or preference may be invented.

## Emoji reinforcement
Emoji reinforcement applies throughout the translated text, not only the final sentence.

EMOJI_REINFORCEMENT_SCOPE=FULL_TRANSLATED_TEXT
PLACEMENT=SEMANTIC_INLINE
EMOJI_WORD_REPLACEMENT=FORBIDDEN
RANDOM_DECORATION=FORBIDDEN

Each candidate placement must evaluate:
1. word meaning
2. phrase meaning
3. sentence context
4. relationship context
5. emotional tone
6. cultural context

The same word may receive different emoji reinforcement in different contexts.
If no emoji is semantically safe and useful, insert none.

User corrections and repeated preferences may adapt emoji density without changing semantic accuracy.
