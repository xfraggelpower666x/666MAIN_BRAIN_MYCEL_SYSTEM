package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"lingua666/internal/win"
)

func showError(message string) { win.Message("666LINGUA", message, 0x10) }

func openExternal(url string) error { return win.Open(url) }

func openUI(url string, browser bool) (<-chan struct{}, func(), error) {
	if browser {
		return nil, nil, openExternal(url)
	}
	for _, key := range []string{"ProgramFiles(x86)", "ProgramFiles", "ProgramW6432", "LOCALAPPDATA"} {
		root := os.Getenv(key)
		if root == "" {
			continue
		}
		edge := filepath.Join(root, "Microsoft", "Edge", "Application", "msedge.exe")
		if _, err := os.Stat(edge); err != nil {
			continue
		}
		profile, err := os.MkdirTemp("", "666LINGUA-window-")
		if err != nil {
			return nil, nil, err
		}
		cmd := exec.Command(edge, "--user-data-dir="+profile, "--no-first-run", "--no-default-browser-check", "--disable-background-mode", "--disable-background-networking", "--disable-sync", "--disable-features=Translate,msEdgeTranslate", "--kiosk", url, "--edge-kiosk-type=fullscreen")
		if err = cmd.Start(); err != nil {
			_ = os.RemoveAll(profile)
			continue
		}
		done := make(chan struct{})
		go func() { _ = cmd.Wait(); close(done) }()
		cleanup := func() {
			select {
			case <-done:
			default:
				_ = cmd.Process.Kill()
				<-done
			}
			if err := os.RemoveAll(profile); err != nil {
				// Ist ein Edge-Unterprozess noch aktiv, kann Windows Dateien kurz sperren.
				fmt.Fprintln(os.Stderr, err)
			}
		}
		return done, cleanup, nil
	}
	if win.Message("666LINGUA", "Microsoft Edge wurde für das App-Fenster nicht gefunden. Im Standardbrowser öffnen?", 0x24) != 6 {
		return nil, nil, fmt.Errorf("App-Fenster benötigt Microsoft Edge. Der Browser-Modus ist über STARTEN.bat verfügbar.")
	}
	return nil, nil, openExternal(url)
}
