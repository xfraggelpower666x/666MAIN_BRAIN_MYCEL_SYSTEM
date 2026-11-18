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

func WindowsX64() Distribution {
	return Distribution{"electron-v" + Version + "-win32-x64.zip", "cd1ab0d49c2f76838c0c9ff75afefb4d9d85ca59036691932bf35be8eceba98b"}
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
	return d.VerifyReader(file)
}

func (d Distribution) VerifyReader(file io.Reader) error {
	sum := sha256.New()
	if _, err := io.Copy(sum, file); err != nil {
		return err
	}
	if hex.EncodeToString(sum.Sum(nil)) != d.SHA256 {
		return errors.New("Die Electron-Laufzeit hat eine ungültige Prüfsumme.")
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
	return d.Save(in, target)
}

func (d Distribution) Save(in io.Reader, target string) error {
	if err := os.MkdirAll(filepath.Dir(target), 0700); err != nil {
		return err
	}
	temp, err := os.CreateTemp(filepath.Dir(target), ".electron-*.zip")
	if err != nil {
		return err
	}
	defer os.Remove(temp.Name())
	sum := sha256.New()
	_, err = io.Copy(io.MultiWriter(temp, sum), in)
	if err = errors.Join(err, temp.Close()); err != nil {
		return err
	}
	if hex.EncodeToString(sum.Sum(nil)) != d.SHA256 {
		return errors.New("Die Electron-Laufzeit hat eine ungültige Prüfsumme.")
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
	return d.prepare(cache, func() (*os.File, *io.SectionReader, error) {
		f, err := os.Open(archive)
		if err != nil {
			return nil, nil, fmt.Errorf("Electron-Archiv fehlt. Bitte das portable ZIP vollständig entpacken: %w", err)
		}
		info, err := f.Stat()
		if err != nil {
			_ = f.Close()
			return nil, nil, err
		}
		return f, io.NewSectionReader(f, 0, info.Size()), nil
	})
}

func (d Distribution) PrepareExecutable(executable, cache string) (string, error) {
	return d.prepare(cache, func() (*os.File, *io.SectionReader, error) {
		file, _, archive, err := OpenPayload(executable)
		return file, archive, err
	})
}

func (d Distribution) prepare(cache string, open func() (*os.File, *io.SectionReader, error)) (string, error) {
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
	file, archive, err := open()
	if err != nil {
		return "", err
	}
	defer file.Close()
	if err := d.VerifyReader(archive); err != nil {
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

func unpack(archive *io.SectionReader, dir string) error {
	z, err := zip.NewReader(archive, archive.Size())
	if err != nil {
		return err
	}
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
