package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"time"
	_ "time/tzdata"
	"unicode/utf8"
)

type Person struct {
	Name   string `json:"name"`
	Birth  string `json:"birth"`
	Zodiac string `json:"zodiac"`
	City   string `json:"city"`
	Zone   string `json:"zone"`
}

type Partner struct {
	Name     string `json:"name"`
	City     string `json:"city"`
	Zone     string `json:"zone"`
	Language string `json:"language"`
}

type Settings struct {
	Language   string   `json:"language"`
	Person     *Person  `json:"person"`
	Partner    *Partner `json:"partner"`
	TargetZone string   `json:"targetZone"`
	From       string   `json:"from"`
	To         string   `json:"to"`
	Revision   uint64   `json:"revision"`
}

func (m Memory) settingsPath() string {
	return filepath.Join(filepath.Dir(m.root), "desktop-settings.json")
}

func (m Memory) settings() (Settings, error) {
	defaults := Settings{Language: "en", From: "en", To: "de"}
	b, err := os.ReadFile(m.settingsPath())
	if errors.Is(err, os.ErrNotExist) {
		return defaults, nil
	}
	if err != nil {
		return defaults, err
	}
	err = json.Unmarshal(b, &defaults)
	if err == nil {
		if !slices.Contains([]string{"en", "de"}, defaults.Language) {
			err = errors.New("INVALID_LANGUAGE")
		} else if !validPair(defaults.From, defaults.To) {
			err = errors.New("INVALID_PAIR")
		} else if err = validateProfile(defaults.Person, defaults.Partner); err == nil && defaults.TargetZone != "" {
			_, err = zone(defaults.TargetZone)
		}
	}
	return defaults, err
}

func zone(name string) (*time.Location, error) {
	if name == "" || name == "Local" || len(name) > 80 {
		return nil, errors.New("INVALID_ZONE")
	}
	loc, err := time.LoadLocation(name)
	if err != nil {
		return nil, errors.New("INVALID_ZONE")
	}
	return loc, nil
}

func zodiac(birth time.Time) string {
	names := []string{"capricorn", "aquarius", "pisces", "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius"}
	start := []int{20, 19, 21, 20, 21, 21, 23, 23, 23, 23, 22, 22}
	i := int(birth.Month()) - 1
	if birth.Day() >= start[i] {
		i = (i + 1) % 12
	}
	return names[i]
}

func trimField(s *string) bool {
	*s = strings.TrimSpace(*s)
	return utf8.RuneCountInString(*s) <= 150 && !strings.ContainsAny(*s, "\x00\r\n")
}

func validateProfile(person *Person, partner *Partner) error {
	if person == nil && partner != nil {
		return errors.New("PROFILE_REQUIRED")
	}
	if person != nil {
		if !trimField(&person.Name) || !trimField(&person.City) || person.Name == "" || person.City == "" {
			return errors.New("PROFILE_REQUIRED")
		}
		birth, err := time.Parse("2006-01-02", person.Birth)
		if err != nil || birth.Year() < 1 || birth.After(time.Now().UTC().Truncate(24*time.Hour)) {
			return errors.New("INVALID_BIRTH")
		}
		if _, err = zone(person.Zone); err != nil {
			return err
		}
		person.Zodiac = zodiac(birth)
	}
	if partner != nil {
		if !trimField(&partner.Name) || !trimField(&partner.City) || !slices.Contains(profiles, partner.Language) {
			return errors.New("INVALID_PARTNER")
		}
		if _, err := zone(partner.Zone); err != nil {
			return err
		}
	}
	return nil
}

func (m Memory) updateSettings(change func(*Settings) error) (Settings, error) {
	unlock, err := m.lock()
	if err != nil {
		return Settings{}, err
	}
	defer unlock()
	p, err := m.settings()
	if err != nil {
		return Settings{}, err
	}
	if err = change(&p); err != nil {
		return Settings{}, err
	}
	p.Revision++
	dir := filepath.Dir(m.settingsPath())
	if err = os.MkdirAll(dir, 0700); err != nil {
		return Settings{}, err
	}
	file, err := os.CreateTemp(dir, ".settings-*")
	if err != nil {
		return Settings{}, err
	}
	defer os.Remove(file.Name())
	if err = json.NewEncoder(file).Encode(p); err == nil {
		err = file.Sync()
	}
	closeErr := file.Close()
	if err = errors.Join(err, closeErr); err != nil {
		return Settings{}, err
	}
	if err = os.Rename(file.Name(), m.settingsPath()); err != nil {
		return Settings{}, err
	}
	return p, nil
}

func validPair(from, to string) bool {
	return from != to && slices.Contains(profiles, from) && slices.Contains(profiles, to)
}

func applyProfile(p *Settings, person *Person, partner *Partner) {
	if partner != nil {
		if p.Partner == nil || p.Partner.Zone != partner.Zone {
			p.TargetZone = partner.Zone
		}
		if p.Partner == nil || p.Partner.Language != partner.Language {
			if p.From == partner.Language {
				if p.To != partner.Language {
					p.From = p.To
				} else if partner.Language == "de" {
					p.From = "en"
				} else {
					p.From = "de"
				}
			}
			p.To = partner.Language
		}
	} else if p.Partner != nil && p.TargetZone == p.Partner.Zone {
		p.TargetZone = ""
	}
	p.Person = person
	p.Partner = partner
}

type TemporalRequest struct {
	Date     string `json:"date"`
	Time     string `json:"time"`
	FromZone string `json:"fromZone"`
	ToZone   string `json:"toZone"`
}

type TemporalResult struct {
	Instant           string `json:"instant"`
	SourceOffset      string `json:"sourceOffset"`
	TargetOffset      string `json:"targetOffset"`
	DifferenceMinutes int    `json:"differenceMinutes"`
	DayShift          int    `json:"dayShift"`
}

func temporal(r TemporalRequest) (TemporalResult, error) {
	from, err := zone(r.FromZone)
	if err != nil {
		return TemporalResult{}, err
	}
	to, err := zone(r.ToZone)
	if err != nil {
		return TemporalResult{}, err
	}
	const layout = "2006-01-02 15:04"
	wall := r.Date + " " + r.Time
	parsed, err := time.Parse(layout, wall)
	if err != nil || parsed.Format(layout) != wall || parsed.Year() < 1 {
		return TemporalResult{}, errors.New("INVALID_WALL_TIME")
	}
	// Beide Regeln am DST-Übergang prüfen, einschließlich Zeitlücken und
	// doppelt auftretender Ortszeit. Eindeutigkeit geht der Konvertierung voraus.
	offsets := map[int]bool{}
	for h := -36; h <= 36; h++ {
		_, offset := parsed.Add(time.Duration(h) * time.Hour).In(from).Zone()
		offsets[offset] = true
	}
	matches := []time.Time{}
	for offset := range offsets {
		t := parsed.Add(-time.Duration(offset) * time.Second).In(from)
		if t.Format(layout) == wall {
			matches = append(matches, t)
		}
	}
	if len(matches) == 0 {
		return TemporalResult{}, errors.New("CLOCK_GAP")
	}
	if len(matches) > 1 {
		return TemporalResult{}, errors.New("CLOCK_FOLD")
	}
	src := matches[0]
	target := src.In(to)
	day := func(t time.Time) time.Time { return time.Date(t.Year(), t.Month(), t.Day(), 0, 0, 0, 0, time.UTC) }
	shift := int(day(target).Sub(day(src)).Hours() / 24)
	_, srcOffset := src.Zone()
	_, dstOffset := target.Zone()
	return TemporalResult{src.UTC().Format(time.RFC3339), src.Format("-07:00"), target.Format("-07:00"), (dstOffset - srcOffset) / 60, shift}, nil
}

func (a *app) handleSettings(route string, w http.ResponseWriter, r *http.Request) bool {
	switch route {
	case "GET api/settings":
		p, err := a.memory.settings()
		if err != nil {
			fail(w, 500, fmt.Errorf("SETTINGS_READ: %w", err))
			return true
		}
		reply(w, 200, p)
	case "POST api/language":
		var body struct {
			Language string `json:"language"`
		}
		if err := readJSON(w, r, &body); err != nil {
			fail(w, 400, err)
			return true
		}
		if !slices.Contains([]string{"en", "de"}, body.Language) {
			fail(w, 400, errors.New("INVALID_LANGUAGE"))
			return true
		}
		p, err := a.memory.updateSettings(func(p *Settings) error { p.Language = body.Language; return nil })
		settingsReply(w, p, err)
	case "POST api/profile":
		var body struct {
			Person  *Person  `json:"person"`
			Partner *Partner `json:"partner"`
		}
		if err := readJSON(w, r, &body); err != nil {
			fail(w, 400, err)
			return true
		}
		if err := validateProfile(body.Person, body.Partner); err != nil {
			fail(w, 400, err)
			return true
		}
		p, err := a.memory.updateSettings(func(p *Settings) error {
			applyProfile(p, body.Person, body.Partner)
			return nil
		})
		settingsReply(w, p, err)
	case "POST api/route":
		var body struct {
			From string `json:"from"`
			To   string `json:"to"`
		}
		if err := readJSON(w, r, &body); err != nil {
			fail(w, 400, err)
			return true
		}
		if !validPair(body.From, body.To) {
			fail(w, 400, errors.New("INVALID_PAIR"))
			return true
		}
		p, err := a.memory.updateSettings(func(p *Settings) error { p.From = body.From; p.To = body.To; return nil })
		settingsReply(w, p, err)
	case "POST api/target-zone":
		var body struct {
			Zone string `json:"zone"`
		}
		if err := readJSON(w, r, &body); err != nil {
			fail(w, 400, err)
			return true
		}
		if body.Zone != "" {
			if _, err := zone(body.Zone); err != nil {
				fail(w, 400, err)
				return true
			}
		}
		p, err := a.memory.updateSettings(func(p *Settings) error { p.TargetZone = body.Zone; return nil })
		settingsReply(w, p, err)
	case "POST api/temporal":
		var body TemporalRequest
		if err := readJSON(w, r, &body); err != nil {
			fail(w, 400, err)
			return true
		}
		converted, err := temporal(body)
		if err != nil {
			fail(w, 400, err)
			return true
		}
		reply(w, 200, converted)
	default:
		return false
	}
	return true
}

func settingsReply(w http.ResponseWriter, p Settings, err error) {
	if err != nil {
		fail(w, 500, fmt.Errorf("SETTINGS_WRITE: %w", err))
		return
	}
	reply(w, 200, p)
}
