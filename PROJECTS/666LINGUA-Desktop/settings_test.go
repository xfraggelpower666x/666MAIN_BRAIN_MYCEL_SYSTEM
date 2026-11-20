package main

import (
	"testing"
	"time"
)

func TestTemporalDSTAndCalendar(t *testing.T) {
	cases := []struct {
		date, clock, from, to, wantErr, wantInstant string
		shift, delta                                int
	}{
		{"2026-03-29", "02:30", "Europe/Berlin", "America/New_York", "CLOCK_GAP", "", 0, 0},
		{"2026-10-25", "02:30", "Europe/Berlin", "America/New_York", "CLOCK_FOLD", "", 0, 0},
		{"2026-12-31", "23:30", "America/New_York", "Asia/Tokyo", "", "2027-01-01T04:30:00Z", 1, 840},
		{"2026-03-14", "12:00", "Europe/Berlin", "America/New_York", "", "2026-03-14T11:00:00Z", 0, -300},
		{"2026-01-01", "00:30", "Europe/Berlin", "America/Los_Angeles", "", "2025-12-31T23:30:00Z", -1, -540},
		{"2026-03-14", "12:00", "Local", "Europe/Berlin", "INVALID_ZONE", "", 0, 0},
	}
	for _, c := range cases {
		t.Run(c.date+"/"+c.clock+"/"+c.from, func(t *testing.T) {
			got, err := temporal(TemporalRequest{c.date, c.clock, c.from, c.to})
			if c.wantErr != "" {
				if err == nil || err.Error() != c.wantErr {
					t.Fatal(err)
				}
				return
			}
			if err != nil || got.Instant != c.wantInstant || got.DayShift != c.shift || got.DifferenceMinutes != c.delta {
				t.Fatal(got, err)
			}
		})
	}
}

func TestSettingsPersistProfileLanguageAndPartner(t *testing.T) {
	m := Memory{t.TempDir() + "/translations"}
	p, err := m.settings()
	if err != nil || p.Language != "en" || p.From != "en" || p.To != "de" {
		t.Fatal(p, err)
	}
	if _, err = m.updateSettings(func(p *Settings) error { p.Language = "de"; return nil }); err != nil {
		t.Fatal(err)
	}
	person := &Person{Name: " Example ", Birth: "1990-11-17", City: "Winterberg", Zone: "Europe/Berlin"}
	partner := &Partner{Name: "Example", Zone: "America/New_York", Language: "en-US"}
	if err = validateProfile(person, partner); err != nil {
		t.Fatal(err)
	}
	if _, err = m.updateSettings(func(p *Settings) error { applyProfile(p, person, partner); return nil }); err != nil {
		t.Fatal(err)
	}
	p, err = m.settings()
	if err != nil || p.Language != "de" || p.Person.Name != "Example" || p.Person.Zodiac != "scorpio" || p.To != "en-US" || p.TargetZone != "America/New_York" || p.Revision != 2 {
		t.Fatal(p, err)
	}
	if _, err = m.updateSettings(func(p *Settings) error { p.TargetZone = "Asia/Tokyo"; applyProfile(p, person, partner); return nil }); err != nil {
		t.Fatal(err)
	}
	p, err = m.settings()
	if err != nil || p.TargetZone != "Asia/Tokyo" {
		t.Fatal(p, err)
	}
	if _, err = m.updateSettings(func(p *Settings) error { applyProfile(p, nil, nil); return nil }); err != nil {
		t.Fatal(err)
	}
	p, err = m.settings()
	if err != nil || p.Person != nil || p.Partner != nil || p.Language != "de" || p.TargetZone != "Asia/Tokyo" {
		t.Fatal(p, err)
	}
}

func TestZodiacBoundaries(t *testing.T) {
	for date, want := range map[string]string{"1990-01-19": "capricorn", "1990-01-20": "aquarius", "1990-12-21": "sagittarius", "1990-12-22": "capricorn", "2000-02-29": "pisces"} {
		d, _ := time.Parse("2006-01-02", date)
		if got := zodiac(d); got != want {
			t.Fatalf("%s: %s", date, got)
		}
	}
}
