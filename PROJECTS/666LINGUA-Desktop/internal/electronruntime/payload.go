package electronruntime

import (
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"os"
)

// Electron liegt als unverändertes ZIP hinter dem Windows-Programm. Der
// Trailer gibt die Grenzen an, ohne die ganze EXE in den Speicher zu laden.
const payloadMagic = "666LINGUA-EZIP01"
const trailerSize = len(payloadMagic) + 8

var ErrNoPayload = errors.New("Keine eingebettete Electron-Laufzeit vorhanden.")

func AppendPayload(program, archive, output string) error {
	exe, err := os.Open(program)
	if err != nil {
		return err
	}
	defer exe.Close()
	zipFile, err := os.Open(archive)
	if err != nil {
		return err
	}
	defer zipFile.Close()
	out, err := os.OpenFile(output, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0755)
	if err != nil {
		return err
	}
	err = writePayload(out, exe, zipFile)
	if err = errors.Join(err, out.Close()); err != nil {
		_ = os.Remove(output)
	}
	return err
}

func writePayload(out io.Writer, exe, archive io.Reader) error {
	if _, err := io.Copy(out, exe); err != nil {
		return err
	}
	size, err := io.Copy(out, archive)
	if err != nil {
		return err
	}
	trailer := [trailerSize]byte{}
	copy(trailer[:], payloadMagic)
	binary.LittleEndian.PutUint64(trailer[len(payloadMagic):], uint64(size))
	_, err = out.Write(trailer[:])
	return err
}

func OpenPayload(path string) (file *os.File, stub, archive *io.SectionReader, err error) {
	file, err = os.Open(path)
	if err != nil {
		return nil, nil, nil, err
	}
	info, err := file.Stat()
	if err == nil {
		stub, archive, err = readPayload(file, info.Size())
	}
	if err != nil {
		_ = file.Close()
		return nil, nil, nil, err
	}
	return file, stub, archive, nil
}

func readPayload(file io.ReaderAt, size int64) (*io.SectionReader, *io.SectionReader, error) {
	if size <= int64(trailerSize) {
		return nil, nil, ErrNoPayload
	}
	end := size - int64(trailerSize)
	trailer := [trailerSize]byte{}
	if _, err := file.ReadAt(trailer[:], end); err != nil {
		return nil, nil, err
	}
	if string(trailer[:len(payloadMagic)]) != payloadMagic {
		return nil, nil, ErrNoPayload
	}
	length := binary.LittleEndian.Uint64(trailer[len(payloadMagic):])
	if length == 0 || length >= uint64(end) {
		return nil, nil, fmt.Errorf("Ungültige Größe der eingebetteten Electron-Laufzeit.")
	}
	offset := end - int64(length)
	return io.NewSectionReader(file, 0, offset), io.NewSectionReader(file, offset, int64(length)), nil
}
