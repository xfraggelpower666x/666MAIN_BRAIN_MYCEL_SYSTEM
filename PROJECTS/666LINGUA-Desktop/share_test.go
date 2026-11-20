package main

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"testing"
)

func TestShareURLPreservesText(t *testing.T) {
	message := "Tom & Ada + 💜\nKannst du? #123\r\nBcc: other@example.com"
	cases := []struct {
		target string
		scheme string
		host   string
		field  string
	}{
		{"whatsapp", "https", "wa.me", "text"},
		{"email", "mailto", "", "body"},
	}
	for _, tc := range cases {
		t.Run(tc.target, func(t *testing.T) {
			address, err := shareURL(tc.target, message)
			if err != nil {
				t.Fatal(err)
			}
			link, err := url.Parse(address)
			if err != nil {
				t.Fatal(err)
			}
			query := link.Query()
			if link.Scheme != tc.scheme || link.Host != tc.host || link.Fragment != "" ||
				len(query) != 1 || query.Get(tc.field) != message {
				t.Fatalf("unexpected share URL: %q", address)
			}
		})
	}
}

func TestShareRequest(t *testing.T) {
	cases := []struct {
		name, body string
		code       int
		openError  error
		opens      bool
	}{
		{"opens WhatsApp", `{"target":"whatsapp","text":"hello"}`, 200, nil, true},
		{"rejects unknown target", `{"target":"https://example.org","text":"hello"}`, 400, nil, false},
		{"rejects URL override", `{"target":"whatsapp","text":"hello","url":"https://example.org"}`, 400, nil, false},
		{"rejects empty text", `{"target":"email","text":"  "}`, 400, nil, false},
		{"rejects long URI", `{"target":"whatsapp","text":"` + strings.Repeat("💜", 250) + `"}`, 400, nil, false},
		{"reports open failure", `{"target":"email","text":"hello"}`, 502, errors.New("unavailable"), true},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			r := httptest.NewRequest(http.MethodPost, "/api/share", strings.NewReader(tc.body))
			r.Header.Set("Content-Type", "application/json")
			w := httptest.NewRecorder()
			called := false
			handleShare(w, r, func(_ string) error {
				called = true
				return tc.openError
			})
			if w.Code != tc.code || called != tc.opens {
				t.Fatalf("status=%d opened=%v body=%q", w.Code, called, w.Body.String())
			}
		})
	}
}
