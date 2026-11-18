package main

import (
	"os"
	"path/filepath"
	"syscall"
)

func (m Memory) lock() (func(), error) {
	if err := os.MkdirAll(m.root, 0700); err != nil {
		return nil, err
	}
	f, err := os.OpenFile(filepath.Join(m.root, ".lock"), os.O_CREATE|os.O_RDWR, 0600)
	if err != nil {
		return nil, err
	}
	if err = syscall.Flock(int(f.Fd()), syscall.LOCK_EX); err != nil {
		f.Close()
		return nil, err
	}
	return func() { _ = f.Close() }, nil
}
