#!/usr/bin/env python3

import os
from tempfile import TemporaryDirectory
import typing

from pass_export import Exporter

def mkdir(*path: str) -> str:
	d = os.path.join(*path)
	os.makedirs(d)
	return d

def create_file(*path: str, content: str = '') -> None:
	ffn = os.path.join(*path)
	with open(ffn, 'wt') as f:
		f.write(content)



def test_iter_files() -> None:
	with TemporaryDirectory() as tmpdir:
		p = tmpdir
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '1')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(p, 'i')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')
		p = mkdir(tmpdir, '2')
		create_file(p, 'a.gpg')
		create_file(p, 'b.gpg')

		out_dir = 'test'
		files: typing.Set[typing.Tuple[str, str]] = set()

		e = Exporter()
		e.export_password = lambda src, dst: files.add((src, dst))  # type: ignore [assignment]  # bug in mypy, see issue #708
		e.export_dir(tmpdir, out_dir)
		assert files == {
			(os.path.join(tmpdir, 'a.gpg'), os.path.join(out_dir, 'a.gpg')),
			(os.path.join(tmpdir, 'b.gpg'), os.path.join(out_dir, 'b.gpg')),
			(os.path.join(tmpdir, '1', 'a.gpg'), os.path.join(out_dir, '1', 'a.gpg')),
			(os.path.join(tmpdir, '1', 'b.gpg'), os.path.join(out_dir, '1', 'b.gpg')),
			(os.path.join(tmpdir, '1', 'i', 'a.gpg'), os.path.join(out_dir, '1', 'i', 'a.gpg')),
			(os.path.join(tmpdir, '1', 'i', 'b.gpg'), os.path.join(out_dir, '1', 'i', 'b.gpg')),
			(os.path.join(tmpdir, '2', 'a.gpg'), os.path.join(out_dir, '2', 'a.gpg')),
			(os.path.join(tmpdir, '2', 'b.gpg'), os.path.join(out_dir, '2', 'b.gpg')),
		}
