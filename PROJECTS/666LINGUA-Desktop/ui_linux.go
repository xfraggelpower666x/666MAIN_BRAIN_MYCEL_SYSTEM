package main

import (
	"fmt"
	"os"
	"os/exec"
)

func showError(message string) { fmt.Fprintln(os.Stderr, message) }
func runDesktop(_ *app, _ bool) error {
	return fmt.Errorf("Die Desktop-Ausgabe ist für Windows. Für lokale Linux-Entwicklung steht --serve zur Verfügung.")
}

func openExternal(url string) error {
	cmd := exec.Command("xdg-open", url)
	if err := cmd.Start(); err != nil {
		return err
	}
	go func() { _ = cmd.Wait() }()
	return nil
}
