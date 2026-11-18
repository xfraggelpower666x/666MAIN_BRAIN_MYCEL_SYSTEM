package main

import (
	"fmt"
	"os"
	"os/exec"
)

func showError(message string) { fmt.Fprintln(os.Stderr, message) }
func openUI(url string, _ bool) (<-chan struct{}, func(), error) {
	cmd := exec.Command("xdg-open", url)
	if err := cmd.Start(); err != nil {
		return nil, nil, err
	}
	go func() { _ = cmd.Wait() }()
	return nil, nil, nil
}
