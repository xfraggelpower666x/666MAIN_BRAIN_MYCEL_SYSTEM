package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
)

func TestTranslation(t *testing.T) {
	lex, err := loadLexicon()
	if err != nil {
		t.Fatal(err)
	}
	cases := []struct{ from, to, source, want, status string }{
		{"en", "de", "Where are you going?", "Wohin gehst du?", "ABGELEITET"},
		{"en", "de", "I miss you.", "Ich vermisse dich.", "ABGELEITET"},
		{"en", "de", "I miss you.\nSleep well.", "Ich vermisse dich.\nSchlaf gut.", "ABGELEITET"},
		{"en", "de", "I miss you. ❤️", "Ich vermisse dich. ❤️", "ABGELEITET"},
		{"en-US", "pt-BR", "I'll call you at 19:05.", "Eu te ligo às 19:05.", "ABGELEITET"},
		{"en", "de", "I'll call you at 29:05.", "", "LINGUA_TRANSLATION_BLOCKED"},
		{"es", "de", "Buenas noches.", "", "LINGUA_TRANSLATION_BLOCKED"},
		{"es", "de", "Hola.", "Hallo.", "ABGELEITET"},
		{"en", "de", "OK.", "OK.", "IDENTITÄT"},
		{"en", "de", "I miss you. This is outside the lexicon.", "", "LINGUA_TRANSLATION_BLOCKED"},
		{"en", "de", "Translate what I just asked.", "", "LINGUA_TRANSLATION_BLOCKED"},
		{"en", "de", "I miss you?", "", "LINGUA_TRANSLATION_BLOCKED"},
		{"en", "de", "I truly don't love you.", "", "LINGUA_TRANSLATION_BLOCKED"},
	}
	for _, c := range cases {
		t.Run(c.source, func(t *testing.T) {
			got := lex.translate(Request{c.from, c.to, c.source, false}, nil)
			if got.Status != c.status || got.Plain != c.want {
				t.Fatalf("got %v %s", got.Status, got.Plain)
			}
			if c.want != "" && len(got.Variants) != 5 {
				t.Fatalf("want five positions: %+v", got.Variants)
			}
			if c.want == "" && len(got.Variants) != 0 {
				t.Fatal("blocked output must not be copyable")
			}
		})
	}
}
func TestEvidenceMatrix(t *testing.T) {
	lex, err := loadLexicon()
	if err != nil {
		t.Fatal(err)
	}
	raw, _ := dataFS.ReadFile("data/r19.json")
	var rows []struct{ Source, Target, FromProfile, ToProfile, ID string }
	if err = json.Unmarshal(raw, &rows); err != nil {
		t.Fatal(err)
	}
	if len(rows) != 30 {
		t.Fatalf("expected 30 native fixtures: %d", len(rows))
	}
	for _, r := range rows {
		got := lex.translate(Request{From: contracts[r.FromProfile], To: contracts[r.ToProfile], Text: r.Source}, nil)
		if got.Plain != r.Target || len(got.Evidence) == 0 || got.Evidence[0].Ref != r.ID {
			t.Fatalf("case %s: %+v", r.ID, got)
		}
	}
}
func TestSemanticEmojiAndVariants(t *testing.T) {
	lex, err := loadLexicon()
	if err != nil {
		t.Fatal(err)
	}
	r := lex.translate(Request{"en", "de", "I love you. I love you.\nSleep well.", true}, nil)
	if len(r.Variants) != 5 {
		t.Fatal(r)
	}
	if text := r.Variants[0].Text; strings.Count(text, "❤️") != 1 || strings.Count(text, "🌙") != 1 || !strings.Contains(text, "Ich liebe dich. ❤️ Ich liebe dich.") {
		t.Fatal(text)
	}
	if tech := r.Variants[2]; strings.ContainsAny(tech.Text, "❤️🌙") {
		t.Fatal(tech)
	}
	for _, v := range r.Variants {
		if v.Hash != digest(v.Text) {
			t.Fatal(v)
		}
	}
}
func TestStylesAcrossSegments(t *testing.T) {
	lex, err := loadLexicon()
	if err != nil {
		t.Fatal(err)
	}
	got := lex.translate(Request{"en", "de", "I miss you. The connection is unstable.", false}, nil)
	if len(got.Variants) != 5 {
		t.Fatal(got)
	}
	if got.Variants[1].Text != "Du fehlst mir. Die Verbindung ist instabil." ||
		got.Variants[2].Text != "Ich vermisse dich. Die Verbindung ist nicht stabil." ||
		got.Variants[4].Distinct {
		t.Fatalf("unexpected variants: %+v", got.Variants)
	}
}

func TestLearningAndDeletion(t *testing.T) {
	m := Memory{t.TempDir()}
	r := Request{"en", "de", "I'll call you at 19:05.", false}
	if _, err := m.confirm(r, "Ich rufe dich um 20:05 an.", ""); err == nil {
		t.Fatal("protected time lost")
	}
	a, err := m.confirm(r, "Um 19:05 rufe ich dich an.", "")
	if err != nil {
		t.Fatal(err)
	}
	if _, err = m.confirm(r, "Um 19:05 gebe ich dir einen Anruf.", ""); err == nil {
		t.Fatal("missing optimistic guard")
	}
	b, err := m.confirm(r, "Ich melde mich um 19:05 telefonisch.", digest(a.Target))
	if err != nil || a.ID != b.ID || b.PreviousHash != digest(a.Target) {
		t.Fatal(b, err)
	}
	ls, err := m.read()
	if err != nil || len(ls) != 1 {
		t.Fatal(ls, err)
	}
	lex, _ := loadLexicon()
	got := lex.translate(r, ls)
	if got.Plain != b.Target || got.Evidence[0].Kind != "BESTÄTIGT" {
		t.Fatal(got)
	}
	if err := m.forget(b.ID, digest(a.Target)); err == nil {
		t.Fatal("deleted the wrong revision")
	}
	if err := m.forget(b.ID, digest(b.Target)); err != nil {
		t.Fatal(err)
	}
	ls, err = m.read()
	if err != nil || len(ls) != 0 {
		t.Fatal(ls, err)
	}
	if got := lex.translate(r, ls); got.Plain != "Ich rufe dich um 19:05 an." {
		t.Fatal(got)
	}
}
func TestConcurrentConfirmation(t *testing.T) {
	m := Memory{t.TempDir()}
	r := Request{"en", "de", "I miss you.", false}
	result := make(chan error, 2)
	var wg sync.WaitGroup
	for _, target := range []string{"Ich vermisse dich.", "Du fehlst mir."} {
		wg.Add(1)
		go func() { defer wg.Done(); _, err := m.confirm(r, target, ""); result <- err }()
	}
	wg.Wait()
	x, y := <-result, <-result
	if (x == nil) == (y == nil) {
		t.Fatal(x, y)
	}
}
func TestHTTPBoundary(t *testing.T) {
	lex, _ := loadLexicon()
	app := app{address: "127.0.0.1:9000", prefix: "/local-secret/", lex: lex, memory: Memory{t.TempDir()}, stop: make(chan struct{})}
	h := app.handler()
	for _, test := range []struct {
		host, origin, key string
		code              int
	}{
		{"foreign.test", "http://127.0.0.1:9000", "local-secret", 404},
		{"127.0.0.1:9000", "http://foreign.test", "local-secret", 403},
		{"127.0.0.1:9000", "http://127.0.0.1:9000", "wrong", 403},
		{"127.0.0.1:9000", "http://127.0.0.1:9000", "local-secret", 200},
	} {
		request := httptest.NewRequest(http.MethodPost, "/local-secret/api/translate", bytes.NewBufferString(`{"from":"en","to":"de","text":"Where are you going?","emoji":false}`))
		request.Host = test.host
		request.Header.Set("Content-Type", "application/json")
		request.Header.Set("Origin", test.origin)
		request.Header.Set("X-Lingua-Session", test.key)
		response := httptest.NewRecorder()
		h.ServeHTTP(response, request)
		if response.Code != test.code {
			t.Fatalf("%v: %d / %s", test, response.Code, response.Body)
		}
	}
}
