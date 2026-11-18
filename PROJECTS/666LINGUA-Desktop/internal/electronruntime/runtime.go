// Package electronruntime verwaltet die festgelegte offizielle Desktop-Laufzeit.
package electronruntime

import (
	"archive/zip"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

const Version = "45.3.2"

type Distribution struct {
	Name, SHA256 string
}

func For(arch string) (Distribution, error) {
	switch arch {
	case "amd64":
		return Distribution{"electron-v" + Version + "-win32-x64.zip", "cd1ab0d49c2f76838c0c9ff75afefb4d9d85ca59036691932bf35be8eceba98b"}, nil
	case "arm64":
		return Distribution{"electron-v" + Version + "-win32-arm64.zip", "89dc2cf11e0913e1b6d2d41f321c4789516548be86be9af0bd607b01d6e610c2"}, nil
	default:
		return Distribution{}, fmt.Errorf("Für diese Architektur ist keine Electron-Laufzeit vorgesehen: %s", arch)
	}
}

func (d Distribution) URL() string {
	return "https://github.com/electron/electron/releases/download/v" + Version + "/" + d.Name
}

func (d Distribution) Verify(path string) error {
	file, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("Electron %s fehlt oder ist nicht lesbar: %w", Version, err)
	}
	defer file.Close()
	sum := sha256.New()
	if _, err := io.Copy(sum, file); err != nil {
		return err
	}
	if hex.EncodeToString(sum.Sum(nil)) != d.SHA256 {
		return fmt.Errorf("Ungültige Electron-Prüfsumme: %s", path)
	}
	return nil
}

func (d Distribution) Copy(source, target string) error {
	if filepath.Clean(source) == filepath.Clean(target) {
		return d.Verify(target)
	}
	if d.Verify(target) == nil {
		return nil
	}
	in, err := os.Open(source)
	if err != nil {
		return fmt.Errorf("Bitte das vollständige 666LINGUA-Paket entpacken. %w", err)
	}
	defer in.Close()
	if err := os.MkdirAll(filepath.Dir(target), 0700); err != nil {
		return err
	}
	temp, err := os.CreateTemp(filepath.Dir(target), ".electron-*.zip")
	if err != nil {
		return err
	}
	defer os.Remove(temp.Name())
	_, err = io.Copy(temp, in)
	if err = errors.Join(err, temp.Close()); err != nil {
		return err
	}
	if err = d.Verify(temp.Name()); err != nil {
		return err
	}
	return os.Rename(temp.Name(), target)
}

func CacheDir() (string, error) {
	base, err := os.UserCacheDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(base, "666SOUNDsDESIGn", "666LINGUA", "electron"), nil
}

func (d Distribution) Prepare(archive, cache string) (string, error) {
	dir := filepath.Join(cache, strings.TrimSuffix(d.Name, ".zip"))
	program := filepath.Join(dir, "electron.exe")
	ready := func() bool {
		stamp, err := os.ReadFile(filepath.Join(dir, ".sha256"))
		if err != nil || string(stamp) != d.SHA256 {
			return false
		}
		for _, name := range []string{"electron.exe", "resources.pak", "icudtl.dat", "locales"} {
			if _, err := os.Stat(filepath.Join(dir, name)); err != nil {
				return false
			}
		}
		return true
	}
	if ready() {
		return program, nil
	}
	if err := d.Verify(archive); err != nil {
		return "", err
	}
	if err := os.MkdirAll(cache, 0700); err != nil {
		return "", err
	}
	stage, err := os.MkdirTemp(cache, ".electron-")
	if err != nil {
		return "", err
	}
	defer os.RemoveAll(stage)
	if err := unpack(archive, stage); err != nil {
		return "", err
	}
	if err := os.WriteFile(filepath.Join(stage, ".sha256"), []byte(d.SHA256), 0600); err != nil {
		return "", err
	}
	if err := os.Rename(stage, dir); err != nil && !ready() {
		return "", fmt.Errorf("Electron-Laufzeit konnte nicht bereitgestellt werden. Ordner prüfen: %s: %w", dir, err)
	}
	if !ready() {
		return "", fmt.Errorf("Electron-Laufzeit ist unvollständig: %s", dir)
	}
	return program, nil
}

func unpack(archive, dir string) error {
	z, err := zip.OpenReader(archive)
	if err != nil {
		return err
	}
	defer z.Close()
	for _, entry := range z.File {
		name := filepath.FromSlash(entry.Name)
		if !filepath.IsLocal(name) || strings.Contains(entry.Name, "\\") {
			return fmt.Errorf("Ungültiger Name in Electron-Archiv: %s", entry.Name)
		}
		path := filepath.Join(dir, name)
		if entry.FileInfo().IsDir() {
			if err := os.MkdirAll(path, 0700); err != nil {
				return err
			}
			continue
		}
		if !entry.Mode().IsRegular() {
			return fmt.Errorf("Ungültiger Dateityp in Electron-Archiv: %s", entry.Name)
		}
		if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
			return err
		}
		if err := unpackFile(entry, path); err != nil {
			return err
		}
	}
	return nil
}

func unpackFile(entry *zip.File, path string) error {
	in, err := entry.Open()
	if err != nil {
		return err
	}
	defer in.Close()
	out, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
	if err != nil {
		return err
	}
	_, err = io.Copy(out, in)
	return errors.Join(err, out.Close())
}
