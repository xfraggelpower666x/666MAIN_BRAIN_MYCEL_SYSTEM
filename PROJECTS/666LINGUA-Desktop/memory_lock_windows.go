package main

import "lingua666/internal/win"

func (m Memory) lock() (func(), error) { return win.LearningLock() }
