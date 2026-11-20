package main

import "testing"

func TestDictionariesAcrossDirections(t *testing.T) {
	memory := Memory{t.TempDir() + "/translations"}
	store := memory.dictionaries()
	de, err := store.confirmEntry(Request{From: "de", To: "en", Text: "Neonspule"}, "neon coil", "", validateTerm)
	if err != nil {
		t.Fatal(err)
	}
	_, err = store.confirmEntry(Request{From: "en", To: "de", Text: "microphone"}, "Talkback", "", validateTerm)
	if err != nil {
		t.Fatal(err)
	}
	_, err = store.confirmEntry(Request{From: "en", To: "de", Text: "Fragglepower"}, "Fragglepower", "", validateTerm)
	if err != nil {
		t.Fatal(err)
	}
	lex, err := loadLexicon()
	if err != nil {
		t.Fatal(err)
	}
	lex.dictionary, err = store.readEntries(validateTerm)
	if err != nil {
		t.Fatal(err)
	}

	for _, c := range []struct{ from, to, source, expected string }{
		{"de", "en-GB", "Neonspule!", "neon coil!"},
		{"de", "en-US", "Ich brauche Neonspule.", "I need neon coil."},
		{"en-US", "de", "The microphone is muted.", "Das Talkback ist stumm."},
		{"en", "de", "Fragglepower", "Fragglepower"},
	} {
		got := lex.translate(Request{From: c.from, To: c.to, Text: c.source}, nil)
		if got.Plain != c.expected || got.Evidence[0].Kind != "WÖRTERBUCH" {
			t.Fatalf("%q: %+v", c.source, got)
		}
	}
	if got := lex.translate(Request{From: "en", To: "de", Text: "neon coil"}, nil); got.Plain != "" {
		t.Fatalf("forward entry leaked into reverse direction: %+v", got)
	}
	if got := lex.translate(Request{From: "de", To: "es", Text: "Neonspule"}, nil); got.Plain != "" {
		t.Fatalf("German-English dictionary leaked into Spanish: %+v", got)
	}
	r := Request{From: "de", To: "en", Text: "Neonspule"}
	if _, err := store.confirmEntry(r, "glow coil", "", validateTerm); err == nil {
		t.Fatal("concurrent replacement succeeded without the previous revision")
	}
	revised, err := store.confirmEntry(r, "glow coil", digest(de.Target), validateTerm)
	if err != nil || revised.ID != de.ID {
		t.Fatal(revised, err)
	}
	if err := store.forgetEntry(revised.ID, digest(revised.Target), validateTerm); err != nil {
		t.Fatal(err)
	}
	lex.dictionary, err = store.readEntries(validateTerm)
	if err != nil {
		t.Fatal(err)
	}
	if got := lex.translate(r, nil); got.Plain != "" {
		t.Fatalf("deleted term still applies: %+v", got)
	}
}

func TestDictionaryKeepsExplicitCorrectionsAndProtectedContent(t *testing.T) {
	lex, _ := loadLexicon()
	r := Request{From: "en", To: "de", Text: "The microphone is muted."}
	lex.dictionary = map[string]Rule{
		routeKey("en", "de", "microphone"): {ID: "term", Source: "microphone", Target: "Talkback"},
	}
	full := map[string]Rule{routeKey(r.From, r.To, r.Text): {ID: "confirmed", Target: "Das Mikrofon wurde stummgeschaltet."}}
	if got := lex.translate(r, full); got.Plain != "Das Mikrofon wurde stummgeschaltet." || got.Evidence[0].Ref != "confirmed" {
		t.Fatal(got)
	}
	if err := validateTerm(Request{From: "en", To: "de", Text: "@account"}, "@another"); err == nil {
		t.Fatal("changed a protected identifier")
	}
	if actual := wholeTerm("profile file https://test.invalid/file", "file"); len(actual) != 1 || actual[0] != [2]int{8, 12} {
		t.Fatal(actual)
	}
}
