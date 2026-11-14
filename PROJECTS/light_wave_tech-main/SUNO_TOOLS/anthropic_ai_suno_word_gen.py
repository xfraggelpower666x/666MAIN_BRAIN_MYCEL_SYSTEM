import anthropic  # or openai
import os
import random

"""
V2:
4. **Semantic Clustering**:
   - Intro: serene, crystalline, inviting
   - Verses: curious, exploratory, building
   - Choruses: expansive, ecstatic (high word density), anthemic
   - Solos: sparse, breathlike, instrumental feel
   - Improvisation: freeform, spontaneous, multidimensional
"""

class CloudAILyricsGenerator:
    def __init__(self, word_list_path, api_key):
#        self.client = anthropic.Anthropic(api_key=api_key)
        self.words = self._load_words(word_list_path)

    def _load_words(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            text = [w.strip() for w in f.readlines() if w.strip()]
        random.shuffle(text)
        return text
    
    def generate_complete_song(self):
        """
        Single-shot generation with full context
        """
        # Create compressed word list (every 10th word for token efficiency)
        word_sample = self.words[::10]  # 7000 words
        
        prompt = f"""Generate experimental song workflow for AI music (Suno v5).

WORD UNIVERSE (70,000 words - sample provided):
{', '.join(word_sample[:1000])}
[...6000 more words available from: psychedelic, cosmic, spiritual, neologistic domains]

STRUCTURE REQUIRED:
[Intro] → [Verse 1] → [Chorus 1] → [Solo 1] → [Verse 2] → [Chorus 2] → [Solo 2] → [Verse 3] → [Chorus 3] → [Solo 3] → [Improvisation] → [Outro]

CREATIVE RULES:
1. **Punctuation Rhythm**:
   - Commas = breath pauses
   - Spaces = flow
   - ~ = vibrato, ^ = pitch rise, _ = bass drop, * = glitch
   - Use --- for dramatic pauses

2. **Word Selection**:
   - Blend SHORT (2-6 char) and MEDIUM (7-14 char) and LONG (15-33 char) words
   - Create neologisms: compound unexpected words
   - Use phonetic cascades

3. **Numeric Seeds**:
   - Insert 3-5 numeric sequences
   - Place at section transitions

4. **Semantic Clustering**:
   - Intro: serene, crystalline
   - Verses: exploratory, building
   - Choruses: expansive, ecstatic (high word density)
   - Solos: sparse, instrumental feel
   - Improvisation: freeform chaos

5. **Fractal Refrains**:
   - Choose 2-3 "anchor phrases"
   - Repeat at Fibonacci intervals

6. **Section Lengths** (characters):
   - Intro: ~100
   - Verses: 180-250
   - Choruses: 300-400
   - Solos: 100-400 (Solo 2 longest)
   - Improvisation: 400+

OUTPUT: Complete lyric workflow, abstract & poetic, ready for Suno. No explanations.

GENERATE:"""

#        message = self.client.messages.create(
#            model="claude-sonnet-4-5-20250929",
#            max_tokens=8000,
#            temperature=0.9,
#            messages=[{"role": "user", "content": prompt}]
#        )
        
#        return message.content[0].text

        return prompt

# USAGE
api_key = ""
#os.getenv("ANTHROPIC_API_KEY")  # Set in environment
#generator = CloudAILyricsGenerator(
#    "F:/Deep_Learning_Local/suno/suno_words_all_new.txt",
#    api_key
#)

#"F:/Deep_Learning_Local/suno/suno_words_all_new.txt",

for i in range(40):
    generator = CloudAILyricsGenerator(
        "F:/Deep_Learning_Local/suno/montecarlo_words_unique_001.txt",
        api_key
    )

    lyrics = generator.generate_complete_song()
    print(f"LYRICS: {lyrics}")
    with open(f"ai_ai_lyrics_monte{i:03d}.txt", 'w', encoding='utf-8') as f:
        f.write(lyrics)
