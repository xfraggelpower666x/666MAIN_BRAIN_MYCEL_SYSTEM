package main

import (
	"errors"
	"net/http"
	"net/url"
	"strings"
)

func shareURL(target, text string) (string, error) {
	if strings.TrimSpace(text) == "" {
		return "", errors.New("Kein Text zum Teilen vorhanden.")
	}
	escaped := strings.ReplaceAll(url.QueryEscape(text), "+", "%20")
	var address string
	switch target {
	case "whatsapp":
		address = "https://wa.me/?text=" + escaped
	case "email":
		address = "mailto:?body=" + escaped
	default:
		return "", errors.New("Unbekanntes Teilen-Ziel.")
	}
	// Lange URI-Argumente werden von manchen Windows-Handlern abgeschnitten.
	if len(address) > 2000 {
		return "", errors.New("Dieser Text ist für einen Freigabelink zu lang. Nutze Weitere Apps oder kopiere ihn.")
	}
	return address, nil
}

func handleShare(w http.ResponseWriter, r *http.Request, open func(string) error) {
	var request struct {
		Target string `json:"target"`
		Text   string `json:"text"`
	}
	if err := readJSON(w, r, &request); err != nil {
		fail(w, http.StatusBadRequest, err)
		return
	}
	address, err := shareURL(request.Target, request.Text)
	if err != nil {
		fail(w, http.StatusBadRequest, err)
		return
	}
	if err := open(address); err != nil {
		fail(w, http.StatusBadGateway, errors.New("Das Teilen-Ziel konnte nicht geöffnet werden."))
		return
	}
	reply(w, http.StatusOK, true)
}
