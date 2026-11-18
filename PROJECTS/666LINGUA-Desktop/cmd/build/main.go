package main

import (
	"archive/zip"
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
	release = "release"
	payload = "cmd/setup/payload/666LINGUA.exe"
)

var architectures = []string{"amd64", "arm64"}
var carrierHashes = map[string]string{
	"666LINGUA_MAIN_v3.4.7_R19_REPAIR_CARRIER_FINAL2_NOT_PUBLISHED.zip":            "5cfe14e8c6df624873806002999d855d42740e0642d667b435fb27c7a01f052d",
	"666LINGUA_PORTABLE_FULL_v3.4.7_R19_REPAIR_CARRIER_FINAL_NOT_PUBLISHED(1).zip": "54f61dd8641ffb151233c49ed260234110d109a9fd12bee4ecd7d0c557efc81e",
}

func architectureName(arch string) string {
	if arch == "arm64" {
		return "ARM64"
	}
	return "x64"
}
func appName(arch string) string   { return "666LINGUA-" + architectureName(arch) + ".exe" }
func setupName(arch string) string { return "666LINGUA-Setup-" + architectureName(arch) + ".exe" }

func packageName(arch string) string { return "666LINGUA-Windows-" + architectureName(arch) + ".zip" }

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
func build(arch, out, pkg string, tags ...string) error {
	args := []string{"build", "-buildvcs=false", "-trimpath", "-ldflags=-H windowsgui -s -w", "-o", out}
	args = append(args, tags...)
	fmt.Printf("Build %s / %s\n", pkg, architectureName(arch))
	return goTool(append(args, pkg), "GOOS=windows", "GOARCH="+arch, "CGO_ENABLED=0")
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
func verifyPE(path, arch string) error {
	f, err := pe.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()
	machine := uint16(pe.IMAGE_FILE_MACHINE_AMD64)
	if arch == "arm64" {
		machine = pe.IMAGE_FILE_MACHINE_ARM64
	}
	header, is64 := f.OptionalHeader.(*pe.OptionalHeader64)
	if !is64 || f.Machine != machine || header.Subsystem != 2 {
		return fmt.Errorf("Falsches PE-Ziel oder fehlendes GUI-Subsystem: %s", path)
	}
	return nil
}
func ensureElectron(stage, arch string) (electronruntime.Distribution, error) {
	d, err := electronruntime.For(arch)
	if err != nil {
		return d, err
	}
	cache := os.Getenv("LINGUA_ELECTRON_ARCHIVES")
	if cache == "" {
		cache = filepath.Join("build-output", "electron-downloads")
	}
	if err := os.MkdirAll(cache, 0700); err != nil {
		return d, err
	}
	local := filepath.Join(cache, d.Name)
	if err := d.Verify(local); err != nil {
		fmt.Printf("[DOWNLOAD] Electron %s / %s\n", electronruntime.Version, architectureName(arch))
		if err := downloadElectron(d, local); err != nil {
			return d, err
		}
	}
	fmt.Printf("[OK] Electron %s / %s (SHA-256)\n", electronruntime.Version, architectureName(arch))
	return d, d.Copy(local, filepath.Join(stage, d.Name))
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

func writePackage(stage, arch, runtimeArchive string, withSetup bool) error {
	f, err := os.Create(filepath.Join(stage, packageName(arch)))
	if err != nil {
		return err
	}
	w := zip.NewWriter(f)
	names := []string{appName(arch), runtimeArchive, "PORTABLE.txt"}
	if withSetup {
		names = append(names, setupName(arch))
	}
	for _, name := range names {
		path := filepath.Join(stage, name)
		if name == "PORTABLE.txt" {
			path = name
		}
		if err = writePackageEntry(w, path, name, runtimeArchive); err != nil {
			break
		}
	}
	return errors.Join(err, w.Close(), f.Close())
}

func writePackageEntry(w *zip.Writer, path, name, runtimeArchive string) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}
	defer file.Close()
	method := uint16(zip.Deflate)
	if name == runtimeArchive {
		method = zip.Store
	}
	item, err := w.CreateHeader(&zip.FileHeader{Name: name, Method: method})
	if err != nil {
		return err
	}
	_, err = io.Copy(item, file)
	return err
}

func verifyPackage(dir string, manifest map[string]string, arch, runtimeArchive string) error {
	z, err := zip.OpenReader(filepath.Join(dir, packageName(arch)))
	if err != nil {
		return err
	}
	defer z.Close()
	expected := map[string]string{appName(arch): manifest[appName(arch)], runtimeArchive: manifest[runtimeArchive]}
	notice, err := hash("PORTABLE.txt")
	if err != nil {
		return err
	}
	expected["PORTABLE.txt"] = notice
	if checksum := manifest[setupName(arch)]; checksum != "" {
		expected[setupName(arch)] = checksum
	}
	for _, item := range z.File {
		expectedHash, ok := expected[item.Name]
		if !ok {
			return fmt.Errorf("Unerwarteter ZIP-Eintrag: %s", item.Name)
		}
		in, err := item.Open()
		if err != nil {
			return err
		}
		h := sha256.New()
		_, err = io.Copy(h, in)
		if err = errors.Join(err, in.Close()); err != nil {
			return err
		}
		if hex.EncodeToString(h.Sum(nil)) != expectedHash {
			return fmt.Errorf("Paketinhalt stimmt nicht mit der Ausgabedatei überein: %s", item.Name)
		}
		delete(expected, item.Name)
	}
	if len(expected) != 0 {
		return fmt.Errorf("Paketdateien fehlen: %v", expected)
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
func verify(dir string, complete bool, buildArchitectures []string) error {
	files, err := readManifest(dir)
	if err != nil {
		return err
	}
	for _, arch := range buildArchitectures {
		for _, file := range []string{appName(arch), setupName(arch)} {
			if _, ok := files[file]; !ok && file == setupName(arch) && !complete {
				continue
			}
			if err := verifyPE(filepath.Join(dir, file), arch); err != nil {
				return err
			}
			if _, ok := files[file]; !ok {
				return fmt.Errorf("Prüfsumme fehlt: %s", file)
			}
		}
	}
	for _, arch := range buildArchitectures {
		d, err := electronruntime.For(arch)
		if err != nil {
			return err
		}
		if files[d.Name] != d.SHA256 {
			return fmt.Errorf("Die festgelegte Electron-Prüfsumme fehlt: %s", d.Name)
		}
		if files[packageName(arch)] == "" {
			if complete {
				return fmt.Errorf("Paket fehlt: %s", packageName(arch))
			}
		} else if err := verifyPackage(dir, files, arch, d.Name); err != nil {
			return err
		}
	}
	for name, expected := range files {
		got, err := hash(filepath.Join(dir, name))
		if err != nil {
			return err
		}
		if got != expected {
			return fmt.Errorf("Datei stimmt nicht mit Prüfliste überein: %s", name)
		}
	}
	return nil
}
func configure(target string, buildArchitectures []string) error {
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
	names := []string{}
	withSetup := target == "setup" || target == "all" || target == "repair"
	for _, arch := range buildArchitectures {
		out := filepath.Join(stage, appName(arch))
		if err := build(arch, out, "."); err != nil {
			return err
		}
		d, err := ensureElectron(stage, arch)
		if err != nil {
			return err
		}
		names = append(names, appName(arch), d.Name)
		if withSetup {
			raw, err := os.ReadFile(out)
			if err != nil {
				return err
			}
			if err := os.WriteFile(payload, raw, 0600); err != nil {
				return err
			}
			defer os.Remove(payload)
			if err := build(arch, filepath.Join(stage, setupName(arch)), "./cmd/setup", "-tags=installer"); err != nil {
				return err
			}
			names = append(names, setupName(arch))
		}
		if target != "build" && target != "dev" {
			if err := writePackage(stage, arch, d.Name, withSetup); err != nil {
				return err
			}
			names = append(names, packageName(arch))
		}
	}
	var list strings.Builder
	for _, name := range names {
		h, err := hash(filepath.Join(stage, name))
		if err != nil {
			return err
		}
		fmt.Fprintf(&list, "%s  %s\n", h, name)
	}
	if err = os.WriteFile(filepath.Join(stage, "SHA256SUMS.txt"), []byte(list.String()), 0644); err != nil {
		return err
	}
	full := target == "all" || target == "repair"
	if err = verify(stage, full, buildArchitectures); err != nil {
		return err
	}
	if !full {
		// Einzelaktionen erhalten zuvor erzeugte Artefakte im vollständigen Release.
		dest := filepath.Join("build-output", target)
		if err := os.MkdirAll("build-output", 0755); err != nil {
			return err
		}
		return commit(stage, dest)
	}
	return commit(stage, release)
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
		return run("test")
	case "diagnose":
		if err := preflight(); err != nil {
			return err
		}
		if err := verify(release, true, architectures); err != nil {
			return err
		}
		fmt.Println("RELEASE OK: SHA-256, Windows-PE, x64/ARM64 und Portable ZIP")
		return nil
	case "test":
		return goTool([]string{"test", "-count=1", "./..."})
	case "all", "repair", "package", "setup":
		if err := run("test"); err != nil {
			return err
		}
		return configure(action, architectures)
	case "build":
		return configure(action, architectures)
	case "dev-amd64", "dev-arm64":
		return configure("dev", []string{strings.TrimPrefix(action, "dev-")})
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
