#!/usr/bin/env python3

# Copyright © 2022 erzo <erzo@posteo.de>
# This work is free. You can use, copy, modify, and/or distribute it
# under the terms of the BSD Zero Clause License, see LICENSE or
# https://choosealicense.com/licenses/0bsd/

'''
This is a command line tool to export and import passwords from/to pass (https://www.passwordstore.org/).
The passwords are exported to symmetrically encrypted files so they are independent of your private key.
You can use these exported files for making backups or to copy them to another computer.
'''

__version__ = '1.0.1'

import os
import sys
import subprocess
import datetime
import argparse
import tempfile
import getpass
import enum
import typing

XDG_RUNTIME_DIR = os.environ.get('XDG_RUNTIME_DIR', None)


@enum.unique
class HandleExisting(enum.Enum):
	ASK = 'ask'
	OVERWRITE = 'overwrite'
	SKIP = 'skip'


def ask_for_user_input(prompt: str, options: typing.Mapping[str, str]) -> str:
	HELP = '?'
	prompt += ' [%s] ' % '/'.join(tuple(options.keys()) + (HELP,))
	while True:
		out = input(prompt)
		if out == HELP:
			print('You can choose between the following options:')
			pattern = '    {inp} - {helpstr}'
			for inp, helpstr in options.items():
				print(pattern.format(inp=inp, helpstr=helpstr))
			print(pattern.format(inp=HELP, helpstr='help'))

		elif out in options:
			return out

		else:
			print('Invalid input %r.' % out)


class PrintVersion(argparse.Action):

	def __init__(self, option_strings: typing.Sequence[str], dest: str, **kwargs: typing.Any) -> None:
		kwargs.setdefault('nargs', 0)
		argparse.Action.__init__(self, option_strings, dest, **kwargs)

	def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: typing.Any, option_string: typing.Optional[str] = None) -> typing.NoReturn:
		print_version()


class Gpg:

	GPG_CONFIG = os.path.expanduser('~/.gnupg/gpg-agent.conf')
	GPG_CONFIG_BAK = os.path.expanduser('~/.gnupg/gpg-agent.conf.bak')

	def enable_password_cache(self) -> None:
		os.rename(self.GPG_CONFIG, self.GPG_CONFIG_BAK)
		self.reload_gpg_config()

	def disable_password_cache(self) -> None:
		os.rename(self.GPG_CONFIG_BAK, self.GPG_CONFIG)
		self.reload_gpg_config()

	def reload_gpg_config(self) -> None:
		subprocess.run(['gpgconf', '--kill', 'gpg-agent'])

class Pass:

	PASS_DIR = os.path.expanduser('~/.password-store/')
	GPG_KEY_ID_FILE = os.path.join(PASS_DIR, '.gpg-id')

	def get_gpg_key_id(self) -> str:
		with open(self.GPG_KEY_ID_FILE, 'rt') as f:
			return f.read().rstrip()



class Exporter(Gpg, Pass):

	'''
	Export all passwords saved in pass.
	Each password is written to a separate file encrypted with a symmetric cipher so that
	they can be decrypted on any computer without a private key using `gpg -d <file>`.
	'''

	def main(self, args_list: typing.Optional[typing.Sequence[str]] = None) -> None:
		args = self.parse_args(args_list)
		self.enable_password_cache()
		self.fn_export_password = tempfile.NamedTemporaryFile(dir=XDG_RUNTIME_DIR, mode='wt', delete=False)
		try:
			self.fn_export_password.write(self.ask_for_password())
			self.fn_export_password.close()
			self.export_dir(self.PASS_DIR, args.path)
		finally:
			self.fn_export_password.close()
			subprocess.run(['shred', self.fn_export_password.name])
			os.remove(self.fn_export_password.name)
			self.disable_password_cache()

	def parse_args(self, args_list: typing.Optional[typing.Sequence[str]]) -> argparse.Namespace:
		p = argparse.ArgumentParser(description=self.__doc__)
		p.add_argument('path', nargs='?', default=datetime.datetime.now().strftime('exported-passwords_%Y-%m-%d'), help='directory where to write the exported files')
		p.add_argument('-v', '--version', action=PrintVersion, help='show the version and exit')

		return p.parse_args(args_list)

	def export_dir(self, src: str, dst: str) -> None:
		if not os.path.exists(dst):
			os.makedirs(dst)
		for name in os.listdir(src):
			ffn_src = os.path.join(src, name)
			ffn_dst = os.path.join(dst, name)
			if os.path.isdir(ffn_src):
				self.export_dir(ffn_src, ffn_dst)
			elif os.path.splitext(name)[1].lower() == '.gpg':
				self.export_password(ffn_src, ffn_dst)
				print(ffn_dst)

	def export_password(self, src: str, dst: str) -> None:
		p = subprocess.run(['gpg', '-d', src], capture_output=True, check=True)
		cleartext_password = p.stdout
		p = subprocess.run(['gpg', '-c', '--no-symkey-cache', '--passphrase-file', self.fn_export_password.name, '--pinentry-mode=loopback'], input=cleartext_password, capture_output=True, check=True)
		encrypted_password = p.stdout
		with open(dst, 'bw') as f:
			f.write(encrypted_password)

	def ask_for_password(self) -> str:
		while True:
			passw = getpass.getpass('Please insert a password to encrypt the exported files: ')
			passw2 = getpass.getpass('Please reenter the password: ')
			if passw == passw2:
				return passw
			print('The passwords do not match. Please try again.')


class Importer(Pass):

	'''
	Import one or more passwords into pass.
	Each password is given in a separate, encrypted file.
	Each of these files can be decrypted with `gpg -d` and the same password.
	'''

	_is_password_set = False

	def main(self, args_list: typing.Optional[typing.Sequence[str]] = None) -> None:
		args = self.parse_args(args_list)
		self.handle_existing: HandleExisting = args.handle_existing
		self.gpg_id = self.get_gpg_key_id()
		self.fn_password = tempfile.NamedTemporaryFile(dir=XDG_RUNTIME_DIR, mode='wt', delete=False)
		self.fn_password.close()
		try:
			for name, ffn in self.iter_files(args.path):
				self.import_password(name, ffn)
		finally:
			subprocess.run(['shred', self.fn_password.name])
			os.remove(self.fn_password.name)

	def parse_args(self, args_list: typing.Optional[typing.Sequence[str]]) -> argparse.Namespace:
		p = argparse.ArgumentParser(description=self.__doc__)
		p.add_argument('path', nargs='+', help='directory or gpg files to be imported')
		p.add_argument('-v', '--version', action=PrintVersion, help='show the version and exit')
		p.add_argument('-f', '--force', dest='handle_existing', action='store_const', const=HandleExisting.OVERWRITE, help='overwrite existing passwords')
		p.add_argument('-s', '--skip', dest='handle_existing', action='store_const', const=HandleExisting.SKIP, help='skip passwords which are already existing')
		p.add_argument('--ask', dest='handle_existing', action='store_const', const=HandleExisting.ASK, help='ask what to do if passwords are already existing')

		return p.parse_args(args_list)


	def iter_files(self, paths: typing.Sequence[str]) -> typing.Iterator[typing.Tuple[str, str]]:
		assert isinstance(paths, (tuple, list))
		assert len(paths) > 0
		if len(paths) == 1 and os.path.isdir(paths[0]):
			p = paths[0]
			for fn in os.listdir(p):
				src = os.path.join(p, fn)
				dst = os.path.join(self.PASS_DIR, fn)
				yield from self.recursive_iter_files(src, dst)
		else:
			for p in paths:
				src = p
				dst = os.path.join(self.PASS_DIR, os.path.split(p)[1])
				yield from self.recursive_iter_files(src, dst)

	def recursive_iter_files(self, src: str, dst: str) -> typing.Iterator[typing.Tuple[str, str]]:
		if os.path.isdir(src):
			for fn in os.listdir(src):
				yield from self.recursive_iter_files(os.path.join(src, fn), os.path.join(dst, fn))
		else:
			yield src, dst

	def ask_for_password(self, prompt: str) -> str:
		out = getpass.getpass(prompt)
		if not out:
			print('canceled by user')
			sys.exit(1)
		return out

	def set_password(self, password: str) -> None:
		with open(self.fn_password.name, 'wt') as f:
			f.write(password)
		self._is_password_set = True

	def import_password(self, src: str, dst: str) -> None:
		if os.path.exists(dst):
			if self.handle_existing is HandleExisting.SKIP:
				return
			elif self.handle_existing is HandleExisting.OVERWRITE:
				pass
			else:
				if not self.ask_to_overwrite(dst):
					return
			os.remove(dst)

		password = self.get_password_to_be_imported(src)
		os.makedirs(os.path.split(dst)[0], exist_ok=True)
		p = subprocess.run(['gpg', '-e', '-r', self.gpg_id, '-o', dst, '--compress-algo=none', '--batch'], input=password, check=True)
		print(f'imported {src}')

	def get_password_to_be_imported(self, src: str) -> bytes:
		if not self._is_password_set:
			self.set_password(self.ask_for_password('Please insert password to decrypt %s: ' % src))

		while True:
			p = subprocess.run(['gpg', '-d', '--no-symkey-cache', '--passphrase-file', self.fn_password.name, '--pinentry-mode=loopback', '--', src], capture_output=True, check=False)
			if p.returncode == 0:
				return p.stdout

			print(p.stderr.decode())
			self.set_password(self.ask_for_password('Wrong password for %s. Please try again: ' % src))

	def ask_to_overwrite(self, dst: str) -> bool:
		inp = ask_for_user_input(f'{dst} exists already. Do you want to overwrite it?', {
			'y' : 'yes',
			'n' : 'no',
			'a' : 'yes for all',
			'q' : 'no for all',
		})
		if inp == 'y':
			return True
		elif inp == 'n':
			return False
		elif inp == 'a':
			self.handle_existing = HandleExisting.OVERWRITE
			return True
		elif inp == 'q':
			self.handle_existing = HandleExisting.SKIP
			return False

		assert False


def print_version() -> typing.NoReturn:
	print(__version__)
	sys.exit(0)

def main_export(args_list: typing.Optional[typing.Sequence[str]] = None) -> None:
	e = Exporter()
	e.main(args_list)

def main_import(args_list: typing.Optional[typing.Sequence[str]] = None) -> None:
	i = Importer()
	i.main(args_list)

def main(args_list: typing.Optional[typing.Sequence[str]] = None) -> None:
	if args_list is None:
		args_list = sys.argv[1:]
		name = sys.argv[0]
	else:
		name = __file__

	if not args_list:
		print('missing argument: export or import', file=sys.stderr)
		sys.exit(1)

	cmd = args_list[0]
	if cmd == 'export':
		main_export(args_list[1:])
	elif cmd == 'import':
		main_import(args_list[1:])
	elif cmd == '-h' or cmd == '--help':
		print(__doc__.lstrip('\n'))
		print(f'{name} export --help')
		print(f'{name} import --help')
	elif cmd == '-v' or cmd == '--version':
		print_version()
	else:
		print('invalid arguments', file=sys.stderr)
		print('the first argument must be either "export" or "import"', file=sys.stderr)


if __name__ == '__main__':
	main()
