package main

import (
	"slices"
	"strings"
)

type sentenceSpan struct{ start, end int }

func translationSpans(text string) []sentenceSpan {
	// Punkte innerhalb von Links, E-Mail-Adressen und Dezimalzahlen
	// gehören zum geschützten Ausdruck und trennen keine Sätze.
	masked := []byte(text)
	for _, match := range protectedRE.FindAllStringIndex(text, -1) {
		for i := match[0]; i < match[1]; i++ {
			if masked[i] == '.' && i+1 < match[1] {
				masked[i] = '_'
			}
		}
	}
	var spans []sentenceSpan
	for _, match := range sentences.FindAllStringIndex(string(masked), -1) {
		raw := text[match[0]:match[1]]
		part := strings.TrimSpace(raw)
		if part != "" {
			start := match[0] + strings.Index(raw, part)
			spans = append(spans, sentenceSpan{start, start + len(part)})
		}
	}
	return spans
}

type meaning struct {
	id      string
	outputs map[string]string
	cues    map[string][]string
}

var nightMeanings = []meaning{
	{
		id:      "GREETING.EVENING",
		outputs: map[string]string{"de": "Guten Abend.", "en": "Good evening."},
		cues: map[string][]string{
			"es":    {"me alegra verte", "cómo estás", "cómo estuvo tu día"},
			"pt-BR": {"fico feliz em ver você", "como você está", "como foi seu dia"},
		},
	},
	{
		id:      "FAREWELL.NIGHT",
		outputs: map[string]string{"de": "Gute Nacht.", "en": "Good night."},
		cues: map[string][]string{
			"es":    {"duerme bien", "quiero dormir", "hasta mañana"},
			"pt-BR": {"durma bem", "quero dormir", "até amanhã"},
		},
	},
}

var meaningTable = map[string][]meaning{
	"es\x00buenas noches": nightMeanings,
	"pt-BR\x00boa noite":  nightMeanings,
	"en\x00the bank": {
		{id: "BANK.FINANCIAL", outputs: map[string]string{"de": "Die Bank."}, cues: map[string][]string{"en": {"i want to withdraw money", "i need to deposit money"}}},
		{id: "BANK.RIVER", outputs: map[string]string{"de": "Das Flussufer."}, cues: map[string][]string{"en": {"we are walking along the river", "the river is rising"}}},
	},
	"de\x00die bank": {
		{id: "BANK.FINANCIAL", outputs: map[string]string{"en": "The bank."}, cues: map[string][]string{"de": {"ich möchte geld abheben", "ich muss geld einzahlen"}}},
		{id: "BANK.SEATING", outputs: map[string]string{"en": "The bench."}, cues: map[string][]string{"de": {"ich möchte mich hinsetzen", "hier kann man sitzen"}}},
	},
}

func (lex Lexicon) contextualSegment(r Request, text string, learned map[string]Rule, neighbors []string) (string, Evidence) {
	target, proof := lex.segment(r, text, learned)
	if (proof.Kind == "PHRASE" || proof.Kind == "QUELLBELEG") && len(lex.dictionary) != 0 {
		return lex.applyAlignedTerms(r, text, target, proof)
	}
	if (target != "" && proof.Kind != "BESTÄTIGT") || strings.HasSuffix(text, "?") {
		return target, proof
	}
	if span := trailingEmoji.FindStringIndex(text); span != nil && span[0] > 0 && target == "" {
		main := strings.TrimSpace(text[:span[0]])
		target, proof := lex.contextualSegment(r, main, learned, neighbors)
		proof.Segment = text
		if target != "" {
			target += " " + strings.TrimSpace(text[span[0]:])
			proof.Selected = target
		}
		return target, proof
	}
	from, to := base(r.From), base(r.To)
	options := meaningTable[from+"\x00"+sentenceKey(text)]
	var alternatives, signals []string
	var chosen meaning
	var selected string
	conflict := false
	for _, option := range options {
		output := option.outputs[to]
		if output == "" {
			continue
		}
		alternatives = append(alternatives, output)
		for _, neighbor := range neighbors {
			if !slices.Contains(option.cues[from], sentenceKey(neighbor)) {
				continue
			}
			signals = append(signals, neighbor)
			if selected != "" && selected != output {
				conflict = true
			}
			chosen, selected = option, output
		}
	}
	if len(alternatives) == 0 {
		return target, proof
	}
	confirmedConflict := target != "" && selected != "" && sentenceKey(target) != sentenceKey(selected)
	if target != "" && !conflict && !confirmedConflict {
		if selected != "" {
			proof.Signals, proof.Selected, proof.Alternatives = signals, target, alternatives
		}
		return target, proof
	}
	if conflict || confirmedConflict || selected == "" {
		reason := "Mehrere Bedeutungen sind möglich. Der Nachbarsatz liefert keinen passenden Hinweis."
		if conflict {
			reason = "Die benachbarten Sätze stützen unterschiedliche Bedeutungen."
		} else if confirmedConflict {
			reason = "Gespeicherte und kontextgestützte Fassung weichen ab. Bestätige die gesamte Satzfolge."
			signals = append(signals, target)
		}
		return "", Evidence{Kind: "OFFEN", Ref: "CONTEXT_MEANING", Segment: text, Reason: reason, Signals: signals, Alternatives: alternatives}
	}
	if strings.HasSuffix(text, "!") {
		selected = strings.TrimSuffix(selected, ".") + "!"
	}
	return selected, Evidence{Kind: "KONTEXT", Ref: chosen.id, Segment: text,
		Reason: "Ein benachbarter Satz stützt diese Bedeutung.", Signals: signals, Selected: selected, Alternatives: alternatives}
}

func adjacentText(text string, spans []sentenceSpan, i int) []string {
	var out []string
	if i > 0 && !strings.ContainsAny(text[spans[i-1].end:spans[i].start], "\r\n") {
		out = append(out, text[spans[i-1].start:spans[i-1].end])
	}
	if i+1 < len(spans) && !strings.ContainsAny(text[spans[i].end:spans[i+1].start], "\r\n") {
		out = append(out, text[spans[i+1].start:spans[i+1].end])
	}
	return out
}

type passageMatch struct {
	end  int
	rule Rule
}

func confirmedPassages(r Request, input string, spans []sentenceSpan, learned map[string]Rule) []passageMatch {
	matches := make([]passageMatch, len(spans))
	if len(learned) == 0 {
		return matches
	}
	for start := range spans {
		// Ein Teiltreffer bleibt auf höchstens acht vollständige Sätze
		// begrenzt. Der direkte Volltexttreffer wird separat geprüft.
		for end := start + 1; end < len(spans) && end < start+8; end++ {
			if strings.Count(input[spans[end-1].end:spans[end].start], "\n") > 1 {
				break
			}
			part := input[spans[start].start:spans[end].end]
			if rule, ok := learned[routeKey(r.From, r.To, part)]; ok {
				matches[start] = passageMatch{end, rule}
			}
		}
	}
	return matches
}

func (lex Lexicon) compose(r Request, input string, learned map[string]Rule) (string, []Evidence) {
	spans := translationSpans(input)
	passages := confirmedPassages(r, input, spans, learned)
	var out strings.Builder
	var checks []Evidence
	last := 0
	for i := 0; i < len(spans); i++ {
		span := spans[i]
		var target string
		var proof Evidence
		if match := passages[i]; match.rule.ID != "" {
			span.end = spans[match.end].end
			part := input[span.start:span.end]
			target, proof = match.rule.Target, Evidence{Kind: "BESTÄTIGT", Ref: match.rule.ID, Segment: part,
				Reason: "Eine bestätigte Satzfolge passt vollständig zu diesem Abschnitt."}
			for other := i + 1; other <= match.end; other++ {
				if passages[other].rule.ID != "" && passages[other].end > match.end {
					target, proof = "", blocked(part, "Bestätigte Satzfolgen überlappen. Bestätige eine gemeinsame Fassung für den gesamten Abschnitt.")
					proof.Ref = "LEARNED_OVERLAP"
					proof.Signals = []string{part, input[spans[other].start:spans[passages[other].end].end]}
					break
				}
			}
			i = match.end
		} else {
			part := input[span.start:span.end]
			target, proof = lex.contextualSegment(r, part, learned, adjacentText(input, spans, i))
		}
		if target != "" && !slices.Equal(protected(input[span.start:span.end]), protected(target)) {
			target, proof = "", blocked(input[span.start:span.end], "Geschützte Zahlen, Links oder Kennungen würden sich ändern.")
		}
		checks = append(checks, proof)
		out.WriteString(input[last:span.start])
		out.WriteString(target)
		last = span.end
	}
	for _, check := range checks {
		if check.Kind == "OFFEN" {
			return "", checks
		}
	}
	out.WriteString(input[last:])
	return strings.TrimSpace(out.String()), checks
}
