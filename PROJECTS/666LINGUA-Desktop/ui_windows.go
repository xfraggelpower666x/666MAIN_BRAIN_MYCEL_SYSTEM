package main

import (
	"bytes"
	"crypto/rand"
	"embed"
	"encoding/hex"
	"errors"
	"fmt"
	"io/fs"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/Microsoft/go-winio"
	"golang.org/x/sys/windows"

	"lingua666/internal/electronruntime"
	"lingua666/internal/win"
)

//go:embed electron/*.cjs electron/package.json
var electronApp embed.FS

func showError(message string) { win.StartupError("666LINGUA", version, errors.New(message)) }

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
		return fmt.Errorf("Electron %s konnte nicht vorbereitet werden: %w", electronruntime.Version, err)
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
	var key [16]byte
	if _, err := rand.Read(key[:]); err != nil {
		return err
	}
	pipe := `\\.\pipe\666LINGUA-` + hex.EncodeToString(key[:])
	account, err := windows.GetCurrentProcessToken().GetTokenUser()
	if err != nil {
		return fmt.Errorf("Windows-Konto für den Electron-Datenkanal: %w", err)
	}
	listener, err := winio.ListenPipe(pipe, &winio.PipeConfig{
		SecurityDescriptor: "D:P(A;;GA;;;" + account.User.Sid.String() + ")",
	})
	if err != nil {
		return fmt.Errorf("Electron-Datenkanal konnte nicht geöffnet werden: %w", err)
	}
	defer listener.Close()
	command.Env = append(command.Env, "ELECTRON_NO_ATTACH_CONSOLE=1", "LINGUA_BRIDGE_PIPE="+pipe)
	var stderr bytes.Buffer
	command.Stderr = &stderr
	command.WaitDelay = 3 * time.Second
	handler := a.desktopMiddleware(openDesktopShare)(http.FileServer(http.FS(assets)))
	if err := runElectronProcess(command, listener, handler); err != nil {
		detail := strings.TrimSpace(stderr.String())
		if detail != "" {
			return fmt.Errorf("Das 666LINGUA-Fenster wurde mit einem Fehler beendet: %w\nElectron %s: %s", err, electronruntime.Version, detail)
		}
		return fmt.Errorf("Das 666LINGUA-Fenster wurde mit einem Fehler beendet: %w", err)
	}
	return nil
}

func runElectronProcess(command *exec.Cmd, listener net.Listener, handler http.Handler) error {
	if err := command.Start(); err != nil {
		return fmt.Errorf("Electron %s konnte nicht gestartet werden: %w", electronruntime.Version, err)
	}
	exited := make(chan error, 1)
	go func() {
		exited <- command.Wait()
		_ = listener.Close()
	}()
	timer := time.AfterFunc(30*time.Second, func() { _ = listener.Close() })
	client, err := listener.Accept()
	timer.Stop()
	if err != nil {
		select {
		case processErr := <-exited:
			return errors.Join(errors.New("Electron hat den Datenkanal vor dem Programmende nicht geöffnet."), processErr)
		default:
			_ = command.Process.Kill()
			return errors.Join(fmt.Errorf("Electron hat den Datenkanal innerhalb von 30 Sekunden nicht geöffnet: %w", err), <-exited)
		}
	}
	_ = listener.Close()
	defer client.Close()
	pipeErr := serveDesktopPipe(client, client, handler)
	if pipeErr != nil {
		_ = command.Process.Kill()
	}
	return errors.Join(pipeErr, <-exited)
}
