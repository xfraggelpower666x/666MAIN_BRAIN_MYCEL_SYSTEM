package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"time"
	"unicode/utf8"
)

type Rule struct {
	ID           string `json:"id"`
	From         string `json:"from"`
	To           string `json:"to"`
	Source       string `json:"source"`
	Target       string `json:"target"`
	Created      string `json:"created"`
	PreviousHash string `json:"previousHash,omitempty"`
}

type Memory struct{ root string }

func defaultMemory() (Memory, error) {
	root, err := os.UserConfigDir()
	return Memory{filepath.Join(root, "666SOUNDsDESIGn", "666LINGUA", "translations")}, err
}

func validateCorrection(r Request, target string) error {
	if err := r.validate(); err != nil {
		return err
	}
	return validateTarget(r.Text, target)
}

func (m Memory) read() (map[string]Rule, error) {
	return m.readEntries(validateCorrection)
}

func (m Memory) readEntries(validate func(Request, string) error) (map[string]Rule, error) {
	out := map[string]Rule{}
	files, err := os.ReadDir(m.root)
	if errors.Is(err, os.ErrNotExist) {
		return out, nil
	}
	if err != nil {
		return nil, err
	}
	for _, entry := range files {
		name := entry.Name()
		if entry.IsDir() || len(name) != 69 || !strings.HasSuffix(name, ".json") {
			continue
		}
		info, err := entry.Info()
		if err != nil {
			return nil, err
		}
		if !info.Mode().IsRegular() || info.Size() > 130000 {
			return nil, fmt.Errorf("Ungültige lokale Regeldatei: %s", name)
		}
		raw, err := os.ReadFile(filepath.Join(m.root, name))
		if err != nil {
			return nil, err
		}
		var rule Rule
		if err = json.Unmarshal(raw, &rule); err != nil {
			return nil, fmt.Errorf("Lokale Regeldatei beschädigt: %s", name)
		}
		k := routeKey(rule.From, rule.To, rule.Source)
		if digest(k) != rule.ID || rule.ID+".json" != name ||
			validate(Request{From: rule.From, To: rule.To, Text: rule.Source}, rule.Target) != nil {
			return nil, fmt.Errorf("Lokale Regeldatei inkonsistent: %s", name)
		}
		out[k] = rule
	}
	return out, nil
}

func validateTarget(source, target string) error {
	if target == "" || normalize(source) == normalize(target) || utf8.RuneCountInString(target) > maxText || strings.ContainsRune(target, '\x00') {
		return fmt.Errorf("Bitte eine eigenständige Zielfassung mit bis zu %d Zeichen eintragen.", maxText)
	}
	if !slices.Equal(protected(source), protected(target)) {
		return fmt.Errorf("Geschützte Zahlen, Links und Kennungen müssen erhalten bleiben.")
	}
	return nil
}

func (m Memory) confirm(r Request, target, previous string) (Rule, error) {
	return m.confirmEntry(r, target, previous, validateCorrection)
}

func (m Memory) confirmEntry(r Request, target, previous string, validate func(Request, string) error) (Rule, error) {
	target = strings.TrimSpace(target)
	if err := validate(r, target); err != nil {
		return Rule{}, err
	}
	unlock, err := m.lock()
	if err != nil {
		return Rule{}, err
	}
	defer unlock()
	old, err := m.readEntries(validate)
	if err != nil {
		return Rule{}, err
	}
	key := routeKey(r.From, r.To, r.Text)
	prior := old[key]
	current := ""
	if prior.ID != "" {
		current = digest(prior.Target)
		if prior.Target == target {
			return prior, nil
		}
	}
	if previous != current {
		return Rule{}, fmt.Errorf("Die Regel wurde zwischenzeitlich geändert. Bitte die aktuelle Fassung prüfen.")
	}
	record := Rule{digest(key), r.From, r.To, strings.TrimSpace(r.Text), target, time.Now().UTC().Format(time.RFC3339), current}
	if err = os.MkdirAll(m.root, 0700); err != nil {
		return Rule{}, err
	}
	f, err := os.CreateTemp(m.root, ".pending-*")
	if err != nil {
		return Rule{}, err
	}
	defer os.Remove(f.Name())
	if err = json.NewEncoder(f).Encode(record); err == nil {
		err = f.Sync()
	}
	closeErr := f.Close()
	if err != nil {
		return Rule{}, err
	}
	if closeErr != nil {
		return Rule{}, closeErr
	}
	if err = os.Rename(f.Name(), filepath.Join(m.root, record.ID+".json")); err != nil {
		return Rule{}, err
	}
	return record, nil
}

func (m Memory) forget(id, previous string) error {
	return m.forgetEntry(id, previous, validateCorrection)
}

func (m Memory) forgetEntry(id, previous string, validate func(Request, string) error) error {
	unlock, err := m.lock()
	if err != nil {
		return err
	}
	defer unlock()
	rules, err := m.readEntries(validate)
	if err != nil {
		return err
	}
	for _, rule := range rules {
		if rule.ID != id {
			continue
		}
		if digest(rule.Target) != previous {
			return fmt.Errorf("Die Regel wurde zwischenzeitlich geändert.")
		}
		return os.Remove(filepath.Join(m.root, rule.ID+".json"))
	}
	return nil
}
