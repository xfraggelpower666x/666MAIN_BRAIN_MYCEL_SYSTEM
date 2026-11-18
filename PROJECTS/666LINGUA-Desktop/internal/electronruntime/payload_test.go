package electronruntime

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"errors"
	"io"
	"os"
	"path/filepath"
	"testing"
)

func TestBundledRuntime(t *testing.T) {
	var data bytes.Buffer
	z := zip.NewWriter(&data)
	for _, name := range []string{"electron.exe", "resources.pak", "icudtl.dat", "locales/en.pak"} {
		file, err := z.Create(name)
		if err != nil {
			t.Fatal(err)
		}
		if _, err := io.WriteString(file, name); err != nil {
			t.Fatal(err)
		}
	}
	if err := z.Close(); err != nil {
		t.Fatal(err)
	}
	sum := sha256.Sum256(data.Bytes())
	distribution := Distribution{"fixture.zip", hex.EncodeToString(sum[:])}
	var bundled bytes.Buffer
	original := []byte("fixture-program")
	if err := writePayload(&bundled, bytes.NewReader(original), bytes.NewReader(data.Bytes())); err != nil {
		t.Fatal(err)
	}
	stub, archive, err := readPayload(bytes.NewReader(bundled.Bytes()), int64(bundled.Len()))
	if err != nil {
		t.Fatal(err)
	}
	prefix, err := io.ReadAll(stub)
	if err != nil || !bytes.Equal(prefix, original) {
		t.Fatalf("Fehler im Programmabschnitt: %q, %v", prefix, err)
	}
	target := filepath.Join(t.TempDir(), distribution.Name)
	if err := distribution.Save(archive, target); err != nil {
		t.Fatal(err)
	}
	if err := distribution.Verify(target); err != nil {
		t.Fatal(err)
	}
	portable := filepath.Join(t.TempDir(), "portable.exe")
	if err := os.WriteFile(portable, bundled.Bytes(), 0600); err != nil {
		t.Fatal(err)
	}
	cache := t.TempDir()
	executable, err := distribution.PrepareExecutable(portable, cache)
	if err != nil {
		t.Fatal(err)
	}
	got, err := os.ReadFile(executable)
	if err != nil || string(got) != "electron.exe" {
		t.Fatalf("Laufzeit konnte nicht aus der EXE geladen werden: %s, %v", got, err)
	}
	bundled.Bytes()[len(original)] ^= 1
	if err := os.WriteFile(portable, bundled.Bytes(), 0600); err != nil {
		t.Fatal(err)
	}
	if _, err := distribution.PrepareExecutable(portable, t.TempDir()); err == nil {
		t.Fatal("Manipuliertes Archiv wurde akzeptiert")
	}
	binary.LittleEndian.PutUint64(bundled.Bytes()[bundled.Len()-8:], ^uint64(0))
	if _, _, err := readPayload(bytes.NewReader(bundled.Bytes()), int64(bundled.Len())); err == nil {
		t.Fatal("Ungültige Archivgrenze wurde akzeptiert")
	}
	if _, _, err := readPayload(bytes.NewReader(original), int64(len(original))); !errors.Is(err, ErrNoPayload) {
		t.Fatalf("Uneingebettete EXE falsch erkannt: %v", err)
	}
}
