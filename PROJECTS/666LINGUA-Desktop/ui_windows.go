package main

import (
	"embed"
	"errors"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"lingua666/internal/electronruntime"
	"lingua666/internal/win"
)

//go:embed electron/*.cjs electron/package.json
var electronApp embed.FS

func showError(message string) { win.Message("666LINGUA", message, 0x10) }

func openExternal(url string) error { return win.Open(url) }

func openDesktopShare(address string) error {
	if text, ok := strings.CutPrefix(address, "https://wa.me/?text="); ok {
		return win.Open("whatsapp://send?text=" + text)
	}
	return openExternal(address)
}

func runDesktop(a *app, windowed bool) error {
	distribution := electronruntime.WindowsX64()
	self, err := os.Executable()
	if err != nil {
		return err
	}
	cache, err := electronruntime.CacheDir()
	if err != nil {
		return err
	}
	executable, err := distribution.PrepareExecutable(self, cache)
	if errors.Is(err, electronruntime.ErrNoPayload) {
		executable, err = distribution.Prepare(filepath.Join(filepath.Dir(self), distribution.Name), cache)
	}
	if err != nil {
		return err
	}
	profile := filepath.Join(cache, "profile")
	if err := os.MkdirAll(profile, 0700); err != nil {
		return err
	}
	stage, err := os.MkdirTemp(cache, ".app-")
	if err != nil {
		return err
	}
	defer os.RemoveAll(stage)
	appFiles, err := fs.Sub(electronApp, "electron")
	if err != nil {
		return err
	}
	if err := os.CopyFS(stage, appFiles); err != nil {
		return err
	}
	assets, err := fs.Sub(web, "app")
	if err != nil {
		return err
	}
	args := []string{stage, "--lingua-profile", profile}
	if windowed {
		args = append(args, "--lingua-windowed")
	}
	command := exec.Command(executable, args...)
	command.Dir = stage
	// Eine fremde Node-/Electron-Konfiguration darf den Desktopstart nicht umleiten.
	for _, entry := range os.Environ() {
		key, _, _ := strings.Cut(entry, "=")
		key = strings.ToUpper(key)
		if !strings.HasPrefix(key, "ELECTRON_") && !strings.HasPrefix(key, "NODE_") {
			command.Env = append(command.Env, entry)
		}
	}
	output, err := command.StdoutPipe()
	if err != nil {
		return err
	}
	input, err := command.StdinPipe()
	if err != nil {
		return err
	}
	defer input.Close()
	if err := command.Start(); err != nil {
		return fmt.Errorf("Electron %s konnte nicht gestartet werden: %w", electronruntime.Version, err)
	}
	handler := a.desktopMiddleware(openDesktopShare)(http.FileServer(http.FS(assets)))
	pipeErr := serveDesktopPipe(output, input, handler)
	_ = input.Close()
	if pipeErr != nil {
		_ = command.Process.Kill()
	}
	if err := errors.Join(pipeErr, command.Wait()); err != nil {
		return fmt.Errorf("Das 666LINGUA-Fenster wurde mit einem Fehler beendet: %w", err)
	}
	return nil
}
