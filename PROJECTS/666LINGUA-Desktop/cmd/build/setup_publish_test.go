package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestPublishSetupKeepsEarlierOutputWhenReplacementFails(t *testing.T) {
	dir := t.TempDir()
	stage := filepath.Join(dir, "stage")
	dest := filepath.Join(dir, "setup")
	for _, folder := range []string{stage, dest, dest + ".previous"} {
		if err := os.Mkdir(folder, 0700); err != nil {
			t.Fatal(err)
		}
	}
	for _, name := range []string{setupName, portableName, "SHA256SUMS.txt"} {
		if err := os.WriteFile(filepath.Join(stage, name), []byte("new"), 0600); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(filepath.Join(dest, name), []byte("old"), 0600); err != nil {
			t.Fatal(err)
		}
	}
	if err := publishSetup(stage, dest); err != nil {
		t.Fatal(err)
	}
	next, err := filepath.Glob(filepath.Join(dir, "setup-neu-*", "setup"))
	if err != nil || len(next) != 1 {
		t.Fatalf("Ausweichordner: %v, %v", next, err)
	}
	for _, name := range []string{setupName, portableName, "SHA256SUMS.txt"} {
		newData, newErr := os.ReadFile(filepath.Join(next[0], name))
		oldData, oldErr := os.ReadFile(filepath.Join(dest, name))
		if newErr != nil || oldErr != nil || string(newData) != "new" || string(oldData) != "old" {
			t.Fatalf("%s: neue oder alte Ausgabe beschädigt (%v / %v)", name, newErr, oldErr)
		}
	}
}
