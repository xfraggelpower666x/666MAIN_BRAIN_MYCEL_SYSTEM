package main

import (
	"fmt"
	"path/filepath"
	"regexp"
	"slices"
	"strings"
	"unicode"
	"unicode/utf8"
)

func (m Memory) dictionaries() Memory {
	return Memory{filepath.Join(filepath.Dir(m.root), "dictionaries")}
}

func dictionaryPair(from, to string) bool {
	return (from == "de" && to == "en") || (from == "en" && to == "de")
}

func validateTerm(r Request, target string) error {
	if !dictionaryPair(r.From, r.To) {
		return fmt.Errorf("Wähle Deutsch → Englisch oder Englisch → Deutsch.")
	}
	for _, word := range []string{strings.TrimSpace(r.Text), target} {
		if word == "" || utf8.RuneCountInString(word) > 160 || strings.ContainsAny(word, "\r\n\x00") {
			return fmt.Errorf("Begriff und Übersetzung brauchen jeweils eine Zeile mit 1 bis 160 Zeichen.")
		}
	}
	if !slices.Equal(protected(r.Text), protected(target)) {
		return fmt.Errorf("Geschützte Zahlen, Links und Kennungen müssen erhalten bleiben.")
	}
	return nil
}

func dictionaryProof(rule Rule, source, target string) Evidence {
	return Evidence{Kind: "WÖRTERBUCH", Ref: rule.ID, Segment: source, Selected: target,
		Reason:  "Ein gespeicherter Begriff wurde für dieses Sprachpaar verwendet.",
		Signals: []string{rule.Source + " → " + rule.Target}, Terms: []string{rule.Target}}
}

type termPattern struct{ left, right, output string }

var dictionaryPatterns = map[string][]termPattern{
	"de": {{"ich brauche ", "", "I need %s"}, {"das ist ", "", "That is %s"},
		{"hier ist ", "", "Here is %s"}, {"ich suche ", "", "I am looking for %s"},
		{"wo ist ", "?", "Where is %s"}, {"bitte öffne ", "", "Please open %s"}},
	"en": {{"i need ", "", "Ich brauche %s"}, {"that is ", "", "Das ist %s"},
		{"this is ", "", "Das ist %s"}, {"here is ", "", "Hier ist %s"},
		{"i am looking for ", "", "Ich suche %s"}, {"where is ", "?", "Wo ist %s"},
		{"please open ", "", "Bitte öffne %s"}},
}

func (lex Lexicon) dictionarySegment(r Request, text string) (string, Evidence) {
	from, to := base(r.From), base(r.To)
	if len(lex.dictionary) == 0 || !dictionaryPair(from, to) {
		return "", Evidence{}
	}
	if rule, ok := lex.dictionary[routeKey(from, to, text)]; ok {
		return rule.Target, dictionaryProof(rule, text, rule.Target)
	}
	core := strings.TrimRight(text, ".!?")
	punctuation := text[len(core):]
	if rule, ok := lex.dictionary[routeKey(from, to, core)]; ok {
		target := strings.TrimRight(rule.Target, ".!?") + punctuation
		return target, dictionaryProof(rule, text, target)
	}
	key := normalize(core)
	for _, pattern := range dictionaryPatterns[from] {
		if strings.HasSuffix(punctuation, "?") != (pattern.right == "?") {
			continue
		}
		term, ok := strings.CutPrefix(key, pattern.left)
		if !ok {
			continue
		}
		if rule, ok := lex.dictionary[routeKey(from, to, term)]; ok {
			target := fmt.Sprintf(pattern.output, strings.TrimRight(rule.Target, ".!?")) + punctuation
			proof := dictionaryProof(rule, text, target)
			proof.Reason = "Ein Satzmuster hat den gespeicherten Begriff eingesetzt."
			proof.Terms = []string{strings.TrimRight(rule.Target, ".!?")}
			return target, proof
		}
	}
	return "", Evidence{}
}

// Die Paare sind explizite Wortzuordnungen für belegte Satzübersetzungen.
// Ersetzt wird nur ein Wort oder eine Wortgruppe, die auf beiden Seiten passt.
var alignedTerms = [][2]string{
	{"Verbindung", "connection"}, {"Datei", "file"}, {"Stream", "stream"},
	{"Mikrofon", "microphone"}, {"Bass", "bass"}, {"Lautstärke", "volume"},
	{"Übergang", "transition"}, {"Anwendung", "application"}, {"Download", "download"},
	{"Geburtstag", "birthday"}, {"Frage", "question"}, {"Hilfe", "help"},
	{"Geld", "money"}, {"Fluss", "river"},
}

func wholeTerm(text, term string) [][2]int {
	var hits [][2]int
	if term == "" {
		return hits
	}
	// Der reguläre Ausdruck behält Bytepositionen des Originaltexts bei,
	// auch wenn die Unicode-Groß-/Kleinschreibung verschiedene Bytebreiten hat.
	matcher := regexp.MustCompile("(?i)" + regexp.QuoteMeta(term))
	protectedSpans := protectedRE.FindAllStringIndex(text, -1)
	word := func(r rune) bool { return unicode.IsLetter(r) || unicode.IsMark(r) || unicode.IsNumber(r) || r == '_' }
	for _, p := range matcher.FindAllStringIndex(text, -1) {
		left, _ := utf8.DecodeLastRuneInString(text[:p[0]])
		right, _ := utf8.DecodeRuneInString(text[p[1]:])
		if word(left) || word(right) {
			continue
		}
		if slices.ContainsFunc(protectedSpans, func(span []int) bool { return span[0] < p[1] && p[0] < span[1] }) {
			continue
		}
		hits = append(hits, [2]int{p[0], p[1]})
	}
	return hits
}

func (lex Lexicon) applyAlignedTerms(r Request, source, target string, proof Evidence) (string, Evidence) {
	from, to := base(r.From), base(r.To)
	if !dictionaryPair(from, to) {
		return target, proof
	}
	type edit struct {
		start, end int
		rule       Rule
	}
	var edits []edit
	for _, pair := range alignedTerms {
		if from == "en" {
			pair[0], pair[1] = pair[1], pair[0]
		}
		rule, ok := lex.dictionary[routeKey(from, to, pair[0])]
		if !ok {
			continue
		}
		input, output := wholeTerm(source, pair[0]), wholeTerm(target, pair[1])
		if len(input) != 1 || len(output) != 1 {
			continue
		}
		edits = append(edits, edit{output[0][0], output[0][1], rule})
	}
	if len(edits) == 0 {
		return target, proof
	}
	slices.SortFunc(edits, func(a, b edit) int { return b.start - a.start })
	original := target
	var refs, signals, terms []string
	for _, change := range edits {
		target = target[:change.start] + change.rule.Target + target[change.end:]
		refs = append(refs, change.rule.ID)
		signals = append(signals, change.rule.Source+" → "+change.rule.Target)
		terms = append(terms, change.rule.Target)
	}
	if !slices.Equal(protected(original), protected(target)) {
		return original, proof
	}
	return target, Evidence{Kind: "WÖRTERBUCH", Ref: proof.Ref, Segment: source, Selected: target,
		Reason:  "Gespeicherte Begriffe wurden in einer belegten Satzübersetzung ersetzt.",
		Signals: append(signals, refs...), Terms: terms}
}

func (res Result) preservesDictionaryTerms(original, variant string) bool {
	for _, proof := range res.Evidence {
		for _, term := range proof.Terms {
			if strings.Count(original, term) > strings.Count(variant, term) {
				return false
			}
		}
	}
	return true
}
