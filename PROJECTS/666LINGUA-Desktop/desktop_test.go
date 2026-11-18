package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"strings"
	"testing"
)

func TestDesktopMiddleware(t *testing.T) {
	lex, err := loadLexicon()
	if err != nil {
		t.Fatal(err)
	}
	a := &app{lex: lex, memory: Memory{filepath.Join(t.TempDir(), "translations")}, stop: make(chan struct{})}
	var opened string
	h := a.desktopMiddleware(func(address string) error {
		opened = address
		return nil
	})(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNoContent)
	}))
	tests := []struct {
		method, path, body, origin, session, contains string
		code                                          int
	}{
		{"GET", "/", "", "", "", "", 204},
		{"GET", "/api/settings", "", "", "desktop", `"from":"en"`, 200},
		{"POST", "/api/translate", `{"text":"I miss you.","from":"en","to":"de","emoji":false}`, desktopOrigin, "desktop", "Ich vermisse dich.", 200},
		{"POST", "/api/share", `{"target":"email","text":"A + B"}`, desktopOrigin, "desktop", "true", 200},
		{"POST", "/api/language", `{"language":"de"}`, "https://example.invalid", "desktop", "", 403},
		{"GET", "/api/info", "", "", "", "", 403},
	}
	for _, tc := range tests {
		t.Run(tc.method+" "+tc.path, func(t *testing.T) {
			req := httptest.NewRequest(tc.method, "http://desktop"+tc.path, strings.NewReader(tc.body))
			req.Header.Set("X-Lingua-Session", tc.session)
			req.Header.Set("Origin", tc.origin)
			if tc.body != "" {
				req.Header.Set("Content-Type", "application/json")
			}
			res := httptest.NewRecorder()
			h.ServeHTTP(res, req)
			if res.Code != tc.code || !strings.Contains(res.Body.String(), tc.contains) {
				t.Fatalf("status=%d body=%s", res.Code, res.Body.String())
			}
			if res.Header().Get("Content-Security-Policy") == "" {
				t.Fatal("missing local content-security policy")
			}
		})
	}
	if opened != "mailto:?body=A%20%2B%20B" {
		t.Fatalf("unexpected share URL: %q", opened)
	}
}

func TestDesktopPipeRoundTrip(t *testing.T) {
	input := strings.NewReader(`{"id":1,"method":"POST","path":"/api/translate","body":"{\"text\":\"A + B\"}"}` + "\n" +
		`{"id":2,"method":"GET","path":"https://example.invalid/","body":""}` + "\n")
	var output bytes.Buffer
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/translate" || r.Header.Get("Origin") != desktopOrigin ||
			r.Header.Get("X-Lingua-Session") != "desktop" || r.Header.Get("Content-Type") != "application/json" {
			t.Fatal("unexpected desktop request", r)
		}
		var data struct{ Text string }
		if err := readJSON(w, r, &data); err != nil || data.Text != "A + B" {
			t.Fatal("unexpected JSON body", data, err)
		}
		reply(w, http.StatusOK, map[string]string{"text": "A + B"})
	})
	if err := serveDesktopPipe(input, &output, handler); err != nil {
		t.Fatal(err)
	}
	decoder := json.NewDecoder(&output)
	var response desktopResponse
	if err := decoder.Decode(&response); err != nil || response.ID != 1 || response.Status != 200 ||
		strings.TrimSpace(string(response.Body)) != `{"text":"A + B"}` {
		t.Fatal("unexpected desktop response", response, err)
	}
	if err := decoder.Decode(&response); err != nil || response.ID != 2 || response.Status != 400 {
		t.Fatal("unexpected rejection", response, err)
	}
}
