package main

import (
	"crypto/rand"
	"embed"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net"
	"net/http"
	"os"
	"slices"
	"strings"
	"sync"
	"time"
)

//go:embed app/*
var web embed.FS

const version = "1.4.0"

type app struct {
	lex     Lexicon
	memory  Memory
	mu      sync.Mutex
	address string
	prefix  string
	stop    chan struct{}
}

func reply(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(v)
}

func fail(w http.ResponseWriter, code int, err error) {
	reply(w, code, map[string]string{"error": err.Error()})
}

func readJSON(w http.ResponseWriter, r *http.Request, v any) error {
	if v == nil {
		return nil
	}
	if r.Header.Get("Content-Type") != "application/json" {
		return errors.New("JSON erforderlich.")
	}
	decoder := json.NewDecoder(http.MaxBytesReader(w, r.Body, 200000))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(v); err != nil {
		return errors.New("Ungültige oder zu große Anfragedaten.")
	}
	if decoder.Decode(new(any)) != io.EOF {
		return errors.New("Es wird genau ein JSON-Objekt erwartet.")
	}
	return nil
}

func (a *app) handler() http.Handler {
	files, _ := fs.Sub(web, "app")
	static := http.FileServer(http.FS(files))
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Cache-Control", "no-store")
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("Referrer-Policy", "no-referrer")
		w.Header().Set("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
		if r.Host != a.address || !strings.HasPrefix(r.URL.Path, a.prefix) {
			http.NotFound(w, r)
			return
		}
		path := strings.TrimPrefix(r.URL.Path, a.prefix)
		if !strings.HasPrefix(path, "api/") {
			if r.Method != http.MethodGet || !slices.Contains([]string{"", "index.html", "app.js", "dictionary.js", "style.css", "icon.svg", "settings.js", "i18n.js", "cities.json", "emoji-en.json", "emoji-de.json", "notices.txt"}, path) {
				http.NotFound(w, r)
				return
			}
			http.StripPrefix(strings.TrimSuffix(a.prefix, "/"), static).ServeHTTP(w, r)
			return
		}
		// Auch andere lokale Webseiten erhalten keine Berechtigung.
		if r.Header.Get("X-Lingua-Session") != strings.Trim(a.prefix, "/") ||
			(r.Method == http.MethodPost && r.Header.Get("Origin") != "http://"+a.address) {
			fail(w, http.StatusForbidden, errors.New("Ungültiger lokaler Sitzungskontext."))
			return
		}
		a.mu.Lock()
		defer a.mu.Unlock()
		route := r.Method + " " + path
		if a.handleSettings(route, w, r) {
			return
		}
		switch route {
		case "GET api/info":
			reply(w, 200, map[string]any{"version": version, "source": "666LINGUA v3.4.7 / R19", "authority": "DESKTOP_CANDIDATE", "externalGate": "MUM_PENDING", "profiles": profiles})
		case "POST api/translate":
			var request Request
			if err := readJSON(w, r, &request); err != nil {
				fail(w, 400, err)
				return
			}
			if err := request.validate(); err != nil {
				fail(w, 400, err)
				return
			}
			rules, err := a.memory.read()
			if err != nil {
				fail(w, 500, fmt.Errorf("Lokales Regelwerk konnte nicht gelesen werden. %w", err))
				return
			}
			lex := a.lex
			if dictionaryPair(base(request.From), base(request.To)) {
				lex.dictionary, err = a.memory.dictionaries().readEntries(validateTerm)
				if err != nil {
					fail(w, 500, err)
					return
				}
			}
			reply(w, 200, lex.translate(request, rules))
		case "GET api/dictionary":
			entries, err := a.memory.dictionaries().readEntries(validateTerm)
			if err != nil {
				fail(w, 500, err)
				return
			}
			list := make([]Rule, 0, len(entries))
			for _, entry := range entries {
				list = append(list, entry)
			}
			reply(w, 200, list)
		case "POST api/dictionary":
			var request struct {
				Request
				Target   string `json:"target"`
				Previous string `json:"previous"`
			}
			if err := readJSON(w, r, &request); err != nil {
				fail(w, 400, err)
				return
			}
			entry, err := a.memory.dictionaries().confirmEntry(request.Request, request.Target, request.Previous, validateTerm)
			if err != nil {
				fail(w, 409, err)
				return
			}
			reply(w, 200, entry)
		case "POST api/dictionary/delete":
			var request struct {
				ID       string `json:"id"`
				Previous string `json:"previous"`
			}
			if err := readJSON(w, r, &request); err != nil {
				fail(w, 400, err)
				return
			}
			if err := a.memory.dictionaries().forgetEntry(request.ID, request.Previous, validateTerm); err != nil {
				fail(w, 409, err)
				return
			}
			reply(w, 200, true)
		case "GET api/memory":
			m, err := a.memory.read()
			if err != nil {
				fail(w, 500, err)
				return
			}
			list := make([]Rule, 0, len(m))
			for _, rule := range m {
				list = append(list, rule)
			}
			slices.SortFunc(list, func(x, y Rule) int { return strings.Compare(y.Created, x.Created) })
			reply(w, 200, list)
		case "POST api/confirm":
			var request struct {
				Request
				Target   string `json:"target"`
				Previous string `json:"previous"`
			}
			if err := readJSON(w, r, &request); err != nil {
				fail(w, 400, err)
				return
			}
			rule, err := a.memory.confirm(request.Request, request.Target, request.Previous)
			if err != nil {
				fail(w, 409, err)
				return
			}
			reply(w, 200, rule)
		case "POST api/forget":
			var request struct {
				ID       string `json:"id"`
				Previous string `json:"previous"`
			}
			if err := readJSON(w, r, &request); err != nil {
				fail(w, 400, err)
				return
			}
			if err := a.memory.forget(request.ID, request.Previous); err != nil {
				fail(w, 409, err)
				return
			}
			reply(w, 200, true)
		case "POST api/quit":
			reply(w, 200, true)
			select {
			case <-a.stop:
			default:
				close(a.stop)
			}
		default:
			http.NotFound(w, r)
		}
	})
}

func run(mode string) error {
	lex, err := loadLexicon()
	if err != nil {
		return err
	}
	mem, err := defaultMemory()
	if err != nil {
		return err
	}
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		return err
	}
	defer listener.Close()
	var bytes [24]byte
	if _, err = rand.Read(bytes[:]); err != nil {
		return err
	}
	appState := app{lex: lex, memory: mem, address: listener.Addr().String(), prefix: "/" + hex.EncodeToString(bytes[:]) + "/", stop: make(chan struct{})}
	server := http.Server{Handler: appState.handler(), ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 15 * time.Second, WriteTimeout: 15 * time.Second, IdleTimeout: 30 * time.Second, MaxHeaderBytes: 16384}
	defer server.Close()
	failed := make(chan error, 1)
	go func() { failed <- server.Serve(listener) }()
	url := "http://" + appState.address + appState.prefix
	var browserDone <-chan struct{}
	var cleanup func()
	if mode == "--serve" {
		fmt.Println(url)
	} else {
		browserDone, cleanup, err = openUI(url, mode == "--browser")
		if err != nil {
			return err
		}
		if cleanup != nil {
			defer cleanup()
		}
	}
	select {
	case err = <-failed:
		return err
	case <-browserDone:
		return nil
	case <-appState.stop:
		time.Sleep(250 * time.Millisecond)
		return nil
	}
}

func main() {
	mode := ""
	if len(os.Args) > 1 {
		mode = os.Args[1]
	}
	if len(os.Args) > 2 || !slices.Contains([]string{"", "--browser", "--serve", "--version"}, mode) {
		showError("Unbekannter Startparameter.")
		os.Exit(2)
	}
	if mode == "--version" {
		fmt.Println(version)
		return
	}
	if err := run(mode); err != nil {
		showError(err.Error())
		os.Exit(1)
	}
}
