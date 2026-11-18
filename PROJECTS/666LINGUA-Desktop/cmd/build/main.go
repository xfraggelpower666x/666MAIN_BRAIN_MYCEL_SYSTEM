package main

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
	"debug/pe"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"lingua666/internal/electronruntime"
)

const (
	release      = "release"
	payload      = "cmd/setup/payload/666LINGUA.exe"
	appName      = "666LINGUA-x64.exe"
	setupName    = "666LINGUA-Setup.exe"
	portableName = "666LINGUA-Portable.exe"
	packageName  = "666LINGUA-Portable-win-x64.zip"
)

var carrierHashes = map[string]string{
	"666LINGUA_MAIN_v3.4.7_R19_REPAIR_CARRIER_FINAL2_NOT_PUBLISHED.zip":            "5cfe14e8c6df624873806002999d855d42740e0642d667b435fb27c7a01f052d",
	"666LINGUA_PORTABLE_FULL_v3.4.7_R19_REPAIR_CARRIER_FINAL_NOT_PUBLISHED(1).zip": "54f61dd8641ffb151233c49ed260234110d109a9fd12bee4ecd7d0c557efc81e",
}

func goTool(args []string, env ...string) error {
	name := "go"
	if runtime.GOOS == "windows" {
		name += ".exe"
	}
	command := exec.Command(filepath.Join(runtime.GOROOT(), "bin", name), args...)
	command.Env = append(os.Environ(), env...)
	command.Stdout, command.Stderr, command.Stdin = os.Stdout, os.Stderr, os.Stdin
	return command.Run()
}
func build(out, pkg string, tags ...string) error {
	args := []string{"build", "-buildvcs=false", "-trimpath", "-ldflags=-H windowsgui -s -w", "-o", out}
	args = append(args, tags...)
	fmt.Printf("Build %s / Windows x64\n", pkg)
	return goTool(append(args, pkg), "GOOS=windows", "GOARCH=amd64", "CGO_ENABLED=0")
}
func hash(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer f.Close()
	h := sha256.New()
	if _, err = io.Copy(h, f); err != nil {
		return "", err
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}
func preflight() error {
	for _, path := range []string{"go.mod", "STARTEN.bat", "scripts/windows-go.ps1", "app/index.html", "electron/main.cjs", "electron/preload.cjs", "electron/package.json", "data/phrases.tsv", "data/r19.json", "cmd/setup/setup_windows.go"} {
		if _, err := os.Stat(path); err != nil {
			return err
		}
	}
	// Im öffentlichen Checkout liegen nur die ableitbaren Desktop-Dateien.
	// Sobald der Quellenordner vorhanden ist, müssen beide Originalarchive stimmen.
	if _, err := os.Stat("sources"); errors.Is(err, os.ErrNotExist) {
		fmt.Println("QUELLBELEG NICHT ENTHALTEN: öffentlicher Desktop-Checkout")
		return nil
	} else if err != nil {
		return err
	}
	for name, expected := range carrierHashes {
		got, err := hash(filepath.Join("sources", name))
		if err != nil {
			return err
		}
		if got != expected {
			return fmt.Errorf("R19-Quellarchiv stimmt nicht mit dem Reparaturbericht überein: %s", name)
		}
		fmt.Println("QUELLBELEG OK", name)
	}
	return nil
}
func verifyPE(r io.ReaderAt, name string) error {
	f, err := pe.NewFile(r)
	if err != nil {
		return fmt.Errorf("%s: %w", name, err)
	}
	defer f.Close()
	header, is64 := f.OptionalHeader.(*pe.OptionalHeader64)
	if !is64 || f.Machine != pe.IMAGE_FILE_MACHINE_AMD64 || header.Subsystem != 2 {
		return fmt.Errorf("Erwartet wurde ein Windows-x64-GUI-Programm: %s", name)
	}
	return nil
}

func ensureElectron(d electronruntime.Distribution) (string, error) {
	cache := os.Getenv("LINGUA_ELECTRON_ARCHIVES")
	if cache == "" {
		cache = filepath.Join("build-output", "electron-downloads")
	}
	if err := os.MkdirAll(cache, 0700); err != nil {
		return "", err
	}
	local := filepath.Join(cache, d.Name)
	if err := d.Verify(local); err != nil {
		fmt.Printf("[DOWNLOAD] Electron %s / Windows x64\n", electronruntime.Version)
		if err := downloadElectron(d, local); err != nil {
			return "", err
		}
	}
	fmt.Printf("[OK] Electron %s / Windows x64 (SHA-256)\n", electronruntime.Version)
	return local, nil
}

func downloadElectron(d electronruntime.Distribution, destination string) error {
	client := &http.Client{Timeout: 15 * time.Minute}
	response, err := client.Get(d.URL())
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		return fmt.Errorf("Electron-Download fehlgeschlagen: %s", response.Status)
	}
	file, err := os.CreateTemp(filepath.Dir(destination), ".electron-*.zip")
	if err != nil {
		return err
	}
	defer os.Remove(file.Name())
	_, err = io.Copy(file, io.LimitReader(response.Body, 512<<20))
	if err = errors.Join(err, file.Close()); err != nil {
		return err
	}
	if err := d.Verify(file.Name()); err != nil {
		return err
	}
	return os.Rename(file.Name(), destination)
}

func writePackage(stage, app, archive, archiveName string) error {
	file, err := os.Create(filepath.Join(stage, packageName))
	if err != nil {
		return err
	}
	w := zip.NewWriter(file)
	entries := []struct {
		path, name string
		method     uint16
	}{
		{app, appName, zip.Deflate},
		{archive, archiveName, zip.Store},
		{"PORTABLE.txt", "PORTABLE.txt", zip.Deflate},
	}
	for _, item := range entries {
		if err = writePackageEntry(w, item.path, item.name, item.method); err != nil {
			break
		}
	}
	return errors.Join(err, w.Close(), file.Close())
}

func writePackageEntry(w *zip.Writer, path, name string, method uint16) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}
	defer file.Close()
	item, err := w.CreateHeader(&zip.FileHeader{Name: name, Method: method})
	if err != nil {
		return err
	}
	_, err = io.Copy(item, file)
	return err
}

func verifyPackage(dir string, d electronruntime.Distribution) error {
	z, err := zip.OpenReader(filepath.Join(dir, packageName))
	if err != nil {
		return err
	}
	defer z.Close()
	expected := map[string]func(io.Reader) error{
		appName: func(r io.Reader) error {
			data, err := io.ReadAll(io.LimitReader(r, 32<<20))
			if err != nil {
				return err
			}
			return verifyPE(bytes.NewReader(data), appName)
		},
		d.Name: d.VerifyReader,
		"PORTABLE.txt": func(r io.Reader) error {
			data, err := io.ReadAll(io.LimitReader(r, 32<<10))
			if err != nil {
				return err
			}
			notice, err := os.ReadFile("PORTABLE.txt")
			if err == nil && !bytes.Equal(data, notice) {
				return errors.New("Portable-Anleitung im ZIP weicht von der Projektdatei ab.")
			}
			return err
		},
	}
	for _, item := range z.File {
		validate, ok := expected[item.Name]
		if !ok {
			return fmt.Errorf("Unerwarteter ZIP-Eintrag: %s", item.Name)
		}
		in, err := item.Open()
		if err != nil {
			return err
		}
		if err := errors.Join(validate(in), in.Close()); err != nil {
			return fmt.Errorf("%s: %w", item.Name, err)
		}
		delete(expected, item.Name)
	}
	if len(expected) != 0 {
		return errors.New("Das portable ZIP enthält nicht alle erforderlichen Dateien.")
	}
	return nil
}
func readManifest(dir string) (map[string]string, error) {
	raw, err := os.ReadFile(filepath.Join(dir, "SHA256SUMS.txt"))
	if err != nil {
		return nil, err
	}
	result := map[string]string{}
	for _, line := range strings.Split(strings.TrimSpace(string(raw)), "\n") {
		parts := strings.SplitN(strings.TrimSpace(line), "  ", 2)
		if len(parts) != 2 || len(parts[0]) != 64 || filepath.Base(parts[1]) != parts[1] {
			return nil, errors.New("Ungültige Release-Prüfliste.")
		}
		result[parts[1]] = parts[0]
	}
	return result, nil
}
func outputNames(action, archiveName string) []string {
	switch action {
	case "setup":
		return []string{setupName, portableName}
	case "package":
		return []string{packageName}
	case "build", "dev":
		return []string{appName, archiveName}
	default:
		return []string{setupName, portableName, packageName}
	}
}

func verify(dir, action string) error {
	files, err := readManifest(dir)
	if err != nil {
		return err
	}
	d := electronruntime.WindowsX64()
	expected := outputNames(action, d.Name)
	if len(files) != len(expected) {
		return errors.New("Die Release-Prüfliste enthält eine unerwartete Zahl von Ausgaben.")
	}
	for _, name := range expected {
		path := filepath.Join(dir, name)
		got, err := hash(path)
		if err != nil {
			return err
		}
		if got != files[name] {
			return fmt.Errorf("Datei stimmt nicht mit der Prüfliste überein: %s", name)
		}
		switch name {
		case packageName:
			if err := verifyPackage(dir, d); err != nil {
				return err
			}
		case setupName, portableName:
			if err := verifyBundledExe(path, d); err != nil {
				return err
			}
		case appName:
			file, err := os.Open(path)
			if err != nil {
				return err
			}
			if err := errors.Join(verifyPE(file, name), file.Close()); err != nil {
				return err
			}
		case d.Name:
			if got != d.SHA256 {
				return fmt.Errorf("Die festgelegte Electron-Prüfsumme fehlt: %s", d.Name)
			}
		}
	}
	return nil
}

func verifyBundledExe(path string, d electronruntime.Distribution) error {
	file, stub, archive, err := electronruntime.OpenPayload(path)
	if err != nil {
		return fmt.Errorf("%s: %w", path, err)
	}
	defer file.Close()
	if err := verifyPE(stub, filepath.Base(path)); err != nil {
		return err
	}
	return d.VerifyReader(archive)
}

func configure(target string) error {
	if err := preflight(); err != nil {
		return err
	}
	lockPath := ".666lingua-build.lock"
	if err := os.Mkdir(lockPath, 0700); err != nil {
		return fmt.Errorf("Build-Sperre %s: %w", lockPath, err)
	}
	defer os.Remove(lockPath)
	stage, err := os.MkdirTemp(".", ".666lingua-stage-")
	if err != nil {
		return err
	}
	defer os.RemoveAll(stage)
	d := electronruntime.WindowsX64()
	archive, err := ensureElectron(d)
	if err != nil {
		return err
	}
	names := outputNames(target, d.Name)
	if err := stageOutputs(stage, archive, d, names); err != nil {
		return err
	}
	var list strings.Builder
	for _, name := range names {
		h, err := hash(filepath.Join(stage, name))
		if err != nil {
			return err
		}
		fmt.Fprintf(&list, "%s  %s\n", h, name)
	}
	if err := os.WriteFile(filepath.Join(stage, "SHA256SUMS.txt"), []byte(list.String()), 0644); err != nil {
		return err
	}
	if err := verify(stage, target); err != nil {
		return err
	}
	if target == "all" || target == "repair" {
		return commit(stage, release)
	}
	if err := os.MkdirAll("build-output", 0755); err != nil {
		return err
	}
	return commit(stage, filepath.Join("build-output", target))
}

func stageOutputs(stage, archive string, d electronruntime.Distribution, names []string) error {
	work, err := os.MkdirTemp(stage, "inputs-")
	if err != nil {
		return err
	}
	defer os.RemoveAll(work)
	app := filepath.Join(work, appName)
	if err := build(app, "."); err != nil {
		return err
	}
	for _, name := range names {
		out := filepath.Join(stage, name)
		switch name {
		case appName:
			if err := os.Rename(app, out); err != nil {
				return err
			}
		case d.Name:
			if err := d.Copy(archive, out); err != nil {
				return err
			}
		case setupName:
			if err := stageSetup(work, app, archive, out); err != nil {
				return err
			}
		case portableName:
			if err := electronruntime.AppendPayload(app, archive, out); err != nil {
				return err
			}
		case packageName:
			if err := writePackage(stage, app, archive, d.Name); err != nil {
				return err
			}
		}
	}
	return nil
}

func stageSetup(work, app, archive, out string) error {
	raw, err := os.ReadFile(app)
	if err != nil {
		return err
	}
	if err := os.WriteFile(payload, raw, 0600); err != nil {
		return err
	}
	defer os.Remove(payload)
	stub := filepath.Join(work, setupName)
	if err := build(stub, "./cmd/setup", "-tags=installer"); err != nil {
		return err
	}
	return electronruntime.AppendPayload(stub, archive, out)
}

func commit(stage, dest string) error {
	backup := dest + ".previous"
	if _, err := os.Stat(backup); !errors.Is(err, os.ErrNotExist) {
		return fmt.Errorf("Vorherigen Sicherungsordner prüfen: %s", backup)
	}
	renamed := false
	if _, err := os.Stat(dest); err == nil {
		if err = os.Rename(dest, backup); err != nil {
			return err
		}
		renamed = true
	} else if !errors.Is(err, os.ErrNotExist) {
		return err
	}
	if err := os.Rename(stage, dest); err != nil {
		if renamed {
			return errors.Join(err, os.Rename(backup, dest))
		}
		return err
	}
	fmt.Println("Geprüfte Dateien:", dest)
	if renamed {
		fmt.Println("Vorherige Ausgabe:", backup)
		// Die vorige Ausgabe liegt für eine explizite Wiederherstellung separat.
		stash, err := os.MkdirTemp(filepath.Dir(dest), ".666lingua-backup-")
		if err != nil {
			return err
		}
		if err := os.Rename(backup, filepath.Join(stash, filepath.Base(dest))); err != nil {
			return err
		}
		fmt.Println("Sicherung:", stash)
	}
	return nil
}
func run(action string) error {
	switch action {
	case "toolstarter":
		return preflight()
	case "check":
		if err := preflight(); err != nil {
			return err
		}
		if _, err := ensureElectron(electronruntime.WindowsX64()); err != nil {
			return err
		}
		return run("test")
	case "diagnose":
		if err := preflight(); err != nil {
			return err
		}
		if err := verify(release, "all"); err != nil {
			return err
		}
		fmt.Println("RELEASE OK: SHA-256, Windows-PE, Windows x64, eingebettete Electron-Laufzeit und portables ZIP")
		return nil
	case "test":
		return goTool([]string{"test", "-count=1", "./..."})
	case "all", "repair", "package", "setup":
		if err := run("test"); err != nil {
			return err
		}
		return configure(action)
	case "build":
		return configure(action)
	case "dev", "dev-amd64":
		return configure("dev")
	}
	return fmt.Errorf("Unbekannte Build-Aktion: %s", action)
}
func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "build ACTION")
		os.Exit(2)
	}
	if err := run(os.Args[1]); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
