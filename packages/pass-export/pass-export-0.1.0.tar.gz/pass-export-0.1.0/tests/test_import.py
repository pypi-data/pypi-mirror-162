#!/usr/bin/env python3

import os
from tempfile import TemporaryDirectory

from pass_export import Importer

PASS_DIR = Importer.PASS_DIR

def mkdir(*path: str) -> str:
	d = os.path.join(*path)
	os.makedirs(d)
	return d

def create_file(*path: str, content: str = '') -> None:
	ffn = os.path.join(*path)
	with open(ffn, 'wt') as f:
		f.write(content)



def test_all() -> None:
	with TemporaryDirectory() as tmpdir:
		p = tmpdir
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '1')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '2')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')

		i = Importer()
		files = set(i.iter_files([tmpdir]))
		assert files == {
			(os.path.join(tmpdir, 'a.gpg'), os.path.join(PASS_DIR, 'a.gpg')),
			(os.path.join(tmpdir, 'b.gpg'), os.path.join(PASS_DIR, 'b.gpg')),
			(os.path.join(tmpdir, '1', 'a.gpg'), os.path.join(PASS_DIR, '1', 'a.gpg')),
			(os.path.join(tmpdir, '1', 'b.gpg'), os.path.join(PASS_DIR, '1', 'b.gpg')),
			(os.path.join(tmpdir, '2', 'a.gpg'), os.path.join(PASS_DIR, '2', 'a.gpg')),
			(os.path.join(tmpdir, '2', 'b.gpg'), os.path.join(PASS_DIR, '2', 'b.gpg')),
		}

def test_one_dir() -> None:
	with TemporaryDirectory() as tmpdir:
		p = tmpdir
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '1')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '2')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')

		i = Importer()
		files = set(i.iter_files([os.path.join(tmpdir, '1')]))
		assert files == {
			(os.path.join(tmpdir, '1', 'a.gpg'), os.path.join(PASS_DIR, 'a.gpg')),
			(os.path.join(tmpdir, '1', 'b.gpg'), os.path.join(PASS_DIR, 'b.gpg')),
		}

def test_two_dirs() -> None:
	with TemporaryDirectory() as tmpdir:
		p = tmpdir
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '1')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '2')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')

		i = Importer()
		files = set(i.iter_files([os.path.join(tmpdir, '1'), os.path.join(tmpdir, '2')]))
		assert files == {
			(os.path.join(tmpdir, '1', 'a.gpg'), os.path.join(PASS_DIR, '1', 'a.gpg')),
			(os.path.join(tmpdir, '1', 'b.gpg'), os.path.join(PASS_DIR, '1', 'b.gpg')),
			(os.path.join(tmpdir, '2', 'a.gpg'), os.path.join(PASS_DIR, '2', 'a.gpg')),
			(os.path.join(tmpdir, '2', 'b.gpg'), os.path.join(PASS_DIR, '2', 'b.gpg')),
		}

def test_dir_and_file() -> None:
	with TemporaryDirectory() as tmpdir:
		p = tmpdir
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '1')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '2')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')

		i = Importer()
		files = set(i.iter_files([os.path.join(tmpdir, '1'), os.path.join(tmpdir, 'b.gpg')]))
		assert files == {
			(os.path.join(tmpdir, '1', 'a.gpg'), os.path.join(PASS_DIR, '1', 'a.gpg')),
			(os.path.join(tmpdir, '1', 'b.gpg'), os.path.join(PASS_DIR, '1', 'b.gpg')),
			(os.path.join(tmpdir, 'b.gpg'), os.path.join(PASS_DIR, 'b.gpg')),
		}
