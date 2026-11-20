package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
)

const desktopOrigin = "lingua://desktop"

type desktopRequest struct {
	ID                 int
	Method, Path, Body string
}

type desktopResponse struct {
	ID      int               `json:"id"`
	Status  int               `json:"status"`
	Headers map[string]string `json:"headers"`
	Body    []byte            `json:"body"`
}

// Der Desktop nutzt einen separaten lokalen Datenkanal. Die vorhandenen Handler benötigen keinen TCP-Port.
func serveDesktopPipe(input io.Reader, output io.Writer, handler http.Handler) error {
	scanner := bufio.NewScanner(input)
	// JSON kann Steuerzeichen aus einer 200-KB-Anfrage sechsfach maskieren.
	scanner.Buffer(make([]byte, 8192), 1300000)
	encoder := json.NewEncoder(output)
	for scanner.Scan() {
		var message desktopRequest
		if err := json.Unmarshal(scanner.Bytes(), &message); err != nil {
			return fmt.Errorf("Electron-Anfrage konnte nicht gelesen werden: %w", err)
		}
		response := desktopResponse{ID: message.ID, Status: http.StatusBadRequest}
		path, err := url.ParseRequestURI(message.Path)
		if err == nil && path.Host == "" && !path.IsAbs() && strings.HasPrefix(path.Path, "/") &&
			!strings.HasPrefix(path.Path, "//") && !strings.Contains(path.Path, "\\") &&
			(message.Method == http.MethodGet || message.Method == http.MethodPost) && len(message.Body) <= 200000 {
			request := httptest.NewRequest(message.Method, path.RequestURI(), strings.NewReader(message.Body))
			request.Header.Set("Origin", desktopOrigin)
			request.Header.Set("X-Lingua-Session", "desktop")
			if message.Method == http.MethodPost {
				request.Header.Set("Content-Type", "application/json")
			}
			recorder := httptest.NewRecorder()
			handler.ServeHTTP(recorder, request)
			response.Status = recorder.Code
			response.Body = recorder.Body.Bytes()
			response.Headers = make(map[string]string)
			for name, values := range recorder.Header() {
				response.Headers[name] = strings.Join(values, ", ")
			}
		}
		if err := encoder.Encode(response); err != nil {
			return err
		}
	}
	return scanner.Err()
}
