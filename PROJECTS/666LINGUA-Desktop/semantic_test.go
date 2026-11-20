package main

import (
	"strings"
	"testing"
)

func TestContextDisambiguation(t *testing.T) {
	lex, err := loadLexicon()
	if err != nil {
		t.Fatal(err)
	}
	cases := []struct{ from, to, source, want, ref, signal string }{
		{"es", "de", "Buenas noches. ¿Cómo estás?", "Guten Abend. Wie geht es dir?", "GREETING.EVENING", "¿Cómo estás?"},
		{"es", "de", "Duerme bien. Buenas noches!", "Schlaf gut. Gute Nacht!", "FAREWELL.NIGHT", "Duerme bien."},
		{"pt-BR", "en", "Boa noite. Durma bem.", "Good night. Sleep well.", "FAREWELL.NIGHT", "Durma bem."},
		{"en", "de", "I want to withdraw money. The bank.", "Ich möchte Geld abheben. Die Bank.", "BANK.FINANCIAL", "I want to withdraw money."},
		{"en-GB", "de", "The bank. We are walking along the river.", "Das Flussufer. Wir gehen am Fluss entlang.", "BANK.RIVER", "We are walking along the river."},
		{"de", "en-US", "Die Bank. Hier kann man sitzen.", "The bench. You can sit here.", "BANK.SEATING", "Hier kann man sitzen."},
	}
	for _, c := range cases {
		t.Run(c.source, func(t *testing.T) {
			got := lex.translate(Request{c.from, c.to, c.source, false}, nil)
			if got.Plain != c.want {
				t.Fatalf("result: %+v", got)
			}
			for _, e := range got.Evidence {
				if e.Ref == c.ref && e.Kind == "KONTEXT" && len(e.Alternatives) == 2 && len(e.Signals) == 1 && e.Signals[0] == c.signal && e.Selected != "" {
					return
				}
			}
			t.Fatalf("missing decision evidence: %+v", got.Evidence)
		})
	}
	for _, source := range []string{
		"Buenas noches.",
		"Buenas noches. Gracias.",
		"Buenas noches.\nDuerme bien.",
		"¿Cómo estás? Buenas noches. Duerme bien.",
	} {
		got := lex.translate(Request{"es", "de", source, false}, nil)
		if got.Plain != "" || len(got.Variants) != 0 {
			t.Fatalf("unsupported context published: %q %+v", source, got)
		}
		found := false
		for _, e := range got.Evidence {
			found = found || e.Kind == "OFFEN" && e.Ref == "CONTEXT_MEANING" && len(e.Alternatives) == 2
		}
		if !found {
			t.Fatal("missing alternatives", got)
		}
	}
}

func TestComposeConfirmedPassages(t *testing.T) {
	lex, _ := loadLexicon()
	memory := Memory{t.TempDir()}
	fix := Request{"en", "de", "I need the file. Open https://example.org/a.", false}
	learned, err := memory.confirm(fix, "Ich brauche die Datei. Öffne https://example.org/a.", "")
	if err != nil {
		t.Fatal(err)
	}
	more := Request{"en", "de", "Hello. " + fix.Text + " Thank you.", false}
	rules, err := memory.read()
	if err != nil {
		t.Fatal(err)
	}
	got := lex.translate(more, rules)
	if got.Plain != "Hallo. "+learned.Target+" Danke." || got.Evidence[1].Ref != learned.ID {
		t.Fatalf("verified sequence not reused: %+v", got)
	}
	if got.Evidence[len(got.Evidence)-1].Ref != "PROTECTED_TOKENS" {
		t.Fatalf("missing URL verification: %+v", got.Evidence)
	}
	other := more
	other.From = "en-US"
	if got := lex.translate(other, rules); got.Plain != "" {
		t.Fatalf("leaked confirmation across language profiles: %+v", got)
	}
	other = more
	other.Text = strings.ReplaceAll(other.Text, ". Open", ".\n \nOpen")
	if got := lex.translate(other, rules); got.Plain != "" {
		t.Fatalf("confirmation incorrectly crossed paragraph boundary: %+v", got)
	}
	if err := memory.forget(learned.ID, digest(learned.Target)); err != nil {
		t.Fatal(err)
	}
	rules, _ = memory.read()
	if got := lex.translate(more, rules); got.Plain != "" {
		t.Fatalf("removed rule still influences translation: %+v", got)
	}
}

func TestConfirmedOverlapRequiresExplicitDecision(t *testing.T) {
	lex, _ := loadLexicon()
	r := Request{"en", "de", "Hello. The bank. Thank you.", false}
	left, right := "Hello. The bank.", "The bank. Thank you."
	rules := map[string]Rule{
		routeKey("en", "de", left):  {ID: "left", Target: "Hallo. Die Bank."},
		routeKey("en", "de", right): {ID: "right", Target: "Das Flussufer. Danke."},
	}
	if got := lex.translate(r, rules); got.Plain != "" || got.Evidence[0].Kind != "OFFEN" {
		t.Fatalf("overlap incorrectly resolved: %+v", got)
	}
	rules[routeKey("en", "de", r.Text)] = Rule{ID: "direct", Target: "Hallo. Die Bank. Danke."}
	if got := lex.translate(r, rules); got.Plain == "" || got.Evidence[0].Ref != "direct" {
		t.Fatalf("explicit full text confirmation not honored: %+v", got)
	}
}

func TestConfirmedWordDoesNotSilentlyOverrideContext(t *testing.T) {
	lex, _ := loadLexicon()
	rules := map[string]Rule{
		routeKey("es", "de", "Buenas noches."): {ID: "confirmed-farewell", Target: "Gute Nacht."},
	}
	exact := lex.translate(Request{"es", "de", "Buenas noches.", false}, rules)
	if exact.Plain != "Gute Nacht." || exact.Evidence[0].Ref != "confirmed-farewell" {
		t.Fatalf("direct confirmation changed: %+v", exact)
	}
	conflict := lex.translate(Request{"es", "de", "Buenas noches. ¿Cómo estás?", false}, rules)
	if conflict.Plain != "" || conflict.Evidence[0].Kind != "OFFEN" || len(conflict.Evidence[0].Signals) != 2 {
		t.Fatalf("isolated confirmation overrode sentence context: %+v", conflict)
	}
}
