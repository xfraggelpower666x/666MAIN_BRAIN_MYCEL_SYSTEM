package main

import (
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"regexp"
	"slices"
	"strings"
	"unicode/utf8"
)

//go:embed data/*
var dataFS embed.FS

const maxText = 12000

var profiles = []string{"de", "en", "en-US", "en-GB", "es", "pt-BR"}
var contracts = map[string]string{"GERMAN_STANDARD": "de", "INTERNATIONAL_ENGLISH": "en", "AMERICAN_ENGLISH": "en-US", "BRITISH_ENGLISH": "en-GB", "SPANISH_NEUTRAL": "es", "BRAZILIAN_PORTUGUESE": "pt-BR"}
var bases = []string{"de", "en", "es", "pt-BR"}

type Request struct {
	From  string `json:"from"`
	To    string `json:"to"`
	Text  string `json:"text"`
	Emoji bool   `json:"emoji"`
}

func (r Request) validate() error {
	if !slices.Contains(profiles, r.From) || !slices.Contains(profiles, r.To) || r.From == r.To {
		return fmt.Errorf("Bitte zwei unterschiedliche Sprachprofile wählen.")
	}
	if strings.TrimSpace(r.Text) == "" || utf8.RuneCountInString(r.Text) > maxText || strings.ContainsRune(r.Text, '\x00') {
		return fmt.Errorf("Der Quelltext muss 1 bis %d Zeichen umfassen.", maxText)
	}
	return nil
}

func base(profile string) string {
	if strings.HasPrefix(profile, "en") {
		return "en"
	}
	return profile
}

var normalizer = strings.NewReplacer("’", "'", "‘", "'", "–", "-", "—", "-", "\r\n", "\n")

func normalize(text string) string {
	return strings.ToLower(strings.Join(strings.Fields(normalizer.Replace(text)), " "))
}

func sentenceKey(text string) string {
	return strings.Trim(normalize(text), " .!?¿¡")
}

func digest(text string) string {
	raw := sha256.Sum256([]byte(text))
	return hex.EncodeToString(raw[:])
}

func routeKey(from, to, text string) string  { return from + "\x00" + to + "\x00" + normalize(text) }
func phraseKey(from, to, text string) string { return from + "\x00" + to + "\x00" + sentenceKey(text) }

type lexEntry struct{ text, ref string }
type Lexicon struct {
	exact, phrases map[string][]lexEntry
	dictionary     map[string]Rule
}

func put(m map[string][]lexEntry, key string, e lexEntry) {
	for _, old := range m[key] {
		if normalize(old.text) == normalize(e.text) {
			return
		}
	}
	m[key] = append(m[key], e)
}

func loadLexicon() (Lexicon, error) {
	lex := Lexicon{exact: map[string][]lexEntry{}, phrases: map[string][]lexEntry{}}
	document, _ := dataFS.ReadFile("data/r19.json")
	var imported []struct{ Source, Target, FromProfile, ToProfile, ID string }
	if err := json.Unmarshal(document, &imported); err != nil {
		return lex, err
	}
	for _, row := range imported {
		put(lex.exact, routeKey(contracts[row.FromProfile], contracts[row.ToProfile], row.Source), lexEntry{row.Target, row.ID})
	}
	document, _ = dataFS.ReadFile("data/phrases.tsv")
	for i, line := range strings.Split(strings.TrimSpace(string(document)), "\n") {
		phrases := strings.Split(line, "\t")
		if len(phrases) != len(bases) {
			return lex, fmt.Errorf("Phrasenbestand: Zeile %d ist fehlerhaft", i+1)
		}
		for a, from := range bases {
			for b, to := range bases {
				if a != b {
					put(lex.phrases, phraseKey(from, to, phrases[a]), lexEntry{phrases[b], fmt.Sprintf("phrases.tsv:%d", i+1)})
				}
			}
		}
	}
	return lex, nil
}

type Evidence struct {
	Kind         string   `json:"kind"`
	Ref          string   `json:"ref,omitempty"`
	Segment      string   `json:"segment,omitempty"`
	Reason       string   `json:"reason"`
	Signals      []string `json:"signals,omitempty"`
	Terms        []string `json:"terms,omitempty"`
	Alternatives []string `json:"alternatives,omitempty"`
	Selected     string   `json:"selected,omitempty"`
}
type Variant struct {
	ID       string `json:"id"`
	Label    string `json:"label"`
	Text     string `json:"text"`
	Hash     string `json:"hash"`
	Note     string `json:"note,omitempty"`
	Distinct bool   `json:"distinct"`
}
type Result struct {
	Status   string     `json:"status"`
	Plain    string     `json:"plain,omitempty"`
	Pair     string     `json:"pair"`
	Variants []Variant  `json:"variants,omitempty"`
	Evidence []Evidence `json:"evidence"`
}

func blocked(segment, reason string) Evidence {
	return Evidence{Kind: "OFFEN", Segment: segment, Reason: reason}
}

var sentences = regexp.MustCompile(`[^.!?\n]+(?:[.!?]+|$|\n)?|[.!?]+|\n`)
var trailingEmoji = regexp.MustCompile(`(?:^|\s)[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}\x{200D}\x{FE0F}\s]+$`)
var timePatterns = map[string]*regexp.Regexp{
	"de":    regexp.MustCompile(`^ich rufe dich um ([0-9]{2}:[0-9]{2}) an[.!]?$`),
	"en":    regexp.MustCompile(`^i'll call you at ([0-9]{2}:[0-9]{2})[.!]?$`),
	"es":    regexp.MustCompile(`^te llamo a las ([0-9]{2}:[0-9]{2})[.!]?$`),
	"pt-BR": regexp.MustCompile(`^eu te ligo às ([0-9]{2}:[0-9]{2})[.!]?$`),
}
var timeForm = map[string]string{"de": "Ich rufe dich um %s an.", "en": "I'll call you at %s.", "es": "Te llamo a las %s.", "pt-BR": "Eu te ligo às %s."}

func (lex Lexicon) segment(r Request, text string, learned map[string]Rule) (string, Evidence) {
	if fix, ok := learned[routeKey(r.From, r.To, text)]; ok {
		return fix.Target, Evidence{Kind: "BESTÄTIGT", Ref: fix.ID, Segment: text, Reason: "Explizit bestätigte lokale Korrektur für dieses Sprachpaar."}
	}
	if target, proof := lex.dictionarySegment(r, text); target != "" {
		return target, proof
	}
	if rows := lex.exact[routeKey(r.From, r.To, text)]; len(rows) == 1 {
		return rows[0].text, Evidence{Kind: "QUELLBELEG", Ref: rows[0].ref, Segment: text, Reason: "R19-Kompatibilitätsbestand mit direktem Profiltreffer."}
	}
	if span := trailingEmoji.FindStringIndex(text); span != nil {
		main := strings.TrimSpace(text[:span[0]])
		symbols := strings.TrimSpace(text[span[0]:])
		if main == "" {
			return symbols, Evidence{Kind: "IDENTITÄT", Ref: "SOURCE_EMOJI", Segment: text, Reason: "Vorhandene Emojis bleiben unverändert."}
		}
		target, proof := lex.segment(r, main, learned)
		if target == "" {
			return target, proof
		}
		return target + " " + symbols, proof
	}
	from, to := base(r.From), base(r.To)
	if from != to {
		if rows := lex.phrases[phraseKey(from, to, text)]; len(rows) > 0 {
			if len(rows) > 1 {
				return "", blocked(text, "Mehrdeutige Phrase. Bitte Quelltext präzisieren oder eine Fassung bestätigen.")
			}
			// Eine Frage bleibt eine Frage. Ausrufe dürfen die Satzenergie erhalten.
			if strings.HasSuffix(text, "?") != strings.HasSuffix(rows[0].text, "?") {
				return "", blocked(text, "Satzabsicht passt nicht zur hinterlegten Phrase.")
			}
			if normalize(text) == normalize(rows[0].text) {
				return rows[0].text, Evidence{Kind: "IDENTITÄT", Ref: rows[0].ref, Segment: text, Reason: "Die belegte Form ist in beiden Sprachprofilen gleich."}
			}

			target := rows[0].text
			if strings.HasSuffix(text, "!") && strings.HasSuffix(target, ".") {
				target = strings.TrimSuffix(target, ".") + "!"
				if to == "es" && !strings.HasPrefix(target, "¡") {
					target = "¡" + target
				}
			}
			return target, Evidence{Kind: "PHRASE", Ref: rows[0].ref, Segment: text, Reason: "Direkter lokaler Phrasentreffer."}
		}
		if match := timePatterns[from].FindStringSubmatch(normalize(text)); len(match) > 0 {
			clock := match[1]
			if clock[:2] <= "23" && clock[3:] <= "59" {
				return fmt.Sprintf(timeForm[to], clock), Evidence{Kind: "GRAMMATIK", Ref: "CALL_TIME_24H", Segment: text, Reason: "Satzmuster erkannt. Die Uhrzeit wurde unverändert übernommen."}
			}
		}
	}
	return "", blocked(text, "Für diesen Abschnitt gibt es keinen ausreichend belegten lokalen Treffer.")
}

func (lex Lexicon) translate(r Request, learned map[string]Rule) Result {
	result := Result{Status: "LINGUA_TRANSLATION_BLOCKED", Pair: r.From + " → " + r.To, Evidence: []Evidence{}}
	input := strings.TrimSpace(r.Text)
	exact := routeKey(r.From, r.To, input)
	var target string
	if _, known := learned[exact]; known || len(lex.exact[exact]) > 0 || lex.dictionary[routeKey(base(r.From), base(r.To), input)].ID != "" {
		line, proof := lex.segment(r, input, learned)
		if proof.Kind == "QUELLBELEG" && len(lex.dictionary) != 0 {
			line, proof = lex.applyAlignedTerms(r, input, line, proof)
		}
		result.Evidence = append(result.Evidence, proof)
		if line == "" {
			return result
		}
		target = line
	} else {
		target, result.Evidence = lex.compose(r, input, learned)
	}
	if target == "" {
		return result
	}
	tokens := protected(input)
	if !slices.Equal(tokens, protected(target)) {
		result.Evidence = append(result.Evidence, blocked(input, "Geschützte Zahlen, Links oder Kennungen würden sich ändern."))
		return result
	}
	if normalize(input) == normalize(target) {
		for _, proof := range result.Evidence {
			if proof.Kind != "IDENTITÄT" && proof.Kind != "WÖRTERBUCH" {
				result.Evidence = append(result.Evidence, blocked(input, "Unveränderte Ausgabe ohne belegte sprachliche Identität."))
				return result
			}
		}
		result.Status = "IDENTITÄT"
	} else {
		result.Status = "ABGELEITET"
	}
	if len(tokens) > 0 {
		result.Evidence = append(result.Evidence, Evidence{Kind: "PRÜFUNG", Ref: "PROTECTED_TOKENS",
			Reason: "Zahlen, Links und Kennungen wurden in der Hauptfassung geprüft.", Signals: tokens})
	}
	result.Plain = target
	result.Variants = render(r, target, &result)
	return result
}

var protectedRE = regexp.MustCompile(`(?i)https?://[^\s<>]+|[\pL\d_.+-]+@[\pL\d.-]+\.[\pL]{2,}|@[\pL\d_.-]+|#[\pL\d_-]+|\b\d+(?:[.:,/\-]\d+)*\b`)

func protected(s string) []string {
	var tokens []string
	for _, match := range protectedRE.FindAllString(s, -1) {
		tokens = append(tokens, strings.TrimRight(match, ".,!?;)"))
	}
	slices.Sort(tokens)
	return tokens
}

// Positionen folgen dem nativen Renderer. Wert null steht für die Hauptfassung.
var styles = map[string][5]string{
	"ich vermisse dich":                     {1: "Du fehlst mir.", 3: "Ich sehne mich nach dir."},
	"i miss you":                            {1: "I miss having you around.", 3: "I long for you."},
	"te extraño":                            {1: "Me haces falta.", 3: "Te añoro."},
	"sinto saudade de você":                 {1: "Sinto sua falta."},
	"herzlichen glückwunsch zum geburtstag": {1: "Alles Gute zum Geburtstag!", 4: "Alles Gute, Geburtstagskind!"},
	"happy birthday":                        {1: "Many happy returns!", 4: "Happy birthday, birthday star!"},
	"feliz cumpleaños":                      {1: "¡Felicidades!"},
	"feliz aniversário":                     {1: "Parabéns pelo seu dia!"},
	"die verbindung ist instabil":           {2: "Die Verbindung ist nicht stabil."},
	"the connection is unstable":            {2: "The connection is not stable."},
}
var inline = map[string]string{"ich vermisse dich": "🫂", "i miss you": "🫂", "te extraño": "🫂", "sinto saudade de você": "🫂", "ich liebe dich": "❤️", "i love you": "❤️", "te amo": "❤️", "eu te amo": "❤️", "schlaf gut": "🌙", "sleep well": "🌙", "duerme bien": "🌙", "durma bem": "🌙", "happy birthday": "🎂", "feliz cumpleaños": "🎂", "feliz aniversário": "🎂", "herzlichen glückwunsch zum geburtstag": "🎂"}

func reinforce(text string) (string, int) {
	// Verstärkung gilt für belegte vollständige Sätze. Negation, Ironie und
	// gemischte Aussagen fallen ohne passende Regel automatisch heraus.
	seen := map[string]bool{}
	count := 0
	out := sentences.ReplaceAllStringFunc(text, func(part string) string {
		t := strings.TrimSpace(part)
		emoji := inline[sentenceKey(t)]
		if emoji == "" || seen[emoji] || strings.Contains(text, emoji) {
			return part
		}
		seen[emoji] = true
		count++
		return strings.Replace(part, t, t+" "+emoji, 1)
	})
	return out, count
}

func render(r Request, text string, res *Result) []Variant {
	ids := []string{"PRIMARY", "LOCAL_NATIVE", "TECHNICAL_PRECISE", "EMOTIONAL_PLUS", "CHEEKY_PLAYFUL"}
	labels := []string{"Hauptübersetzung", "Natürlich / lokal", "Präzise / technisch", "Emotional+", "Frech / spielerisch"}
	out := make([]Variant, 0, len(ids))
	tokens := protected(text)
	seen := map[string]bool{}
	for i, id := range ids {
		value := text
		note := ""
		if i > 0 {
			value = sentences.ReplaceAllStringFunc(text, func(part string) string {
				line := strings.TrimSpace(part)
				replacement := styles[sentenceKey(line)][i]
				if replacement == "" {
					return part
				}
				return strings.Replace(part, line, replacement, 1)
			})
			if value == text {
				note = "Hauptfassung · keine eigenständige Fassung belegt"
			} else {
				note = "Lokale Stilregeln auf belegte Sätze angewendet"
			}
		}
		if r.Emoji && i != 2 {
			reinforced, count := reinforce(value)
			if i == 0 && count > 0 {
				res.Evidence = append(res.Evidence, Evidence{Kind: "EMOJI", Ref: "SEMANTIC_INLINE", Segment: "", Reason: "Sinnbezogene Verstärkung an belegten Sätzen. Wiederholte Symbole werden ausgelassen."})
			}
			value = reinforced
		}
		if !res.preservesDictionaryTerms(text, value) {
			value = text
			note = "Stilfassung behält die Wörterbuchbegriffe der Hauptfassung bei."
		}
		if !slices.Equal(tokens, protected(value)) {
			value = text
			note = "Stilfassung verworfen. Sie hätte geschützte Inhalte geändert."
		}
		key := normalize(value)
		out = append(out, Variant{id, labels[i], value, digest(value), note, !seen[key]})
		seen[key] = true
	}
	return out
}
