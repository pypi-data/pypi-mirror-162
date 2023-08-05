############################################################################
#                                                                          #
# Copyright (c) 2020-2022 Carl Drougge                                     #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#  http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
#                                                                          #
############################################################################

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from traceback import print_exc
from datetime import datetime
import errno
from argparse import RawTextHelpFormatter
import os
import sys

from accelerator.colourwrapper import colour
from accelerator.setupfile import encode_setup
from accelerator.compat import FileNotFoundError, url_quote
from accelerator.unixhttp import call
from .parser import name2job, JobNotFound, ArgumentParser

def show(url, job, show_output):
	print(job.path)
	print('=' * len(job.path))
	setup = job.json_load('setup.json')
	setup.pop('_typing', None)
	setup.starttime = str(datetime.fromtimestamp(setup.starttime))
	if 'endtime' in setup:
		setup.endtime = str(datetime.fromtimestamp(setup.endtime))
	print(encode_setup(setup, as_str=True))
	if job.datasets:
		print()
		print('datasets:')
		for ds in job.datasets:
			print('   ', ds.quoted)
	try:
		post = job.json_load('post.json')
	except FileNotFoundError:
		print(colour('WARNING: Job did not finish', 'job/warning'))
		post = None
	if post and post.subjobs:
		print()
		print('subjobs:')
		for sj in sorted(post.subjobs):
			print('   ', sj)
	if post and post.files:
		print()
		print('files:')
		for fn in sorted(post.files):
			print('   ', job.filename(fn))
	if post and not call(url + '/job_is_current/' + url_quote(job)):
		print(colour('Job is not current', 'job/info'))
	print()
	out = job.output()
	if show_output:
		if out:
			print('output (use --just-output/-O to see only the output):')
			print(out)
			if not out.endswith('\n'):
				print()
		else:
			print(job, 'produced no output')
			print()
	elif out:
		print('%s produced %d bytes of output, use --output/-o to see it' % (job, len(out),))
		print()

def show_source(job, pattern='*'):
	import tarfile
	from fnmatch import fnmatch
	with tarfile.open(job.filename('method.tar.gz'), 'r:gz') as tar:
		members = [info for info in tar.getmembers() if info.isfile() and fnmatch(info.path, pattern)]
		for ix, info in enumerate(members, 1):
			if len(members) > 1:
				print(info.path)
				print('=' * len(info.path))
			data = tar.extractfile(info).read()
			has_nl = data.endswith(b'\n')
			while data:
				data = data[os.write(1, data):]
			if not has_nl:
				os.write(1, b'\n')
			if ix < len(members):
				os.write(1, b'\n')

def main(argv, cfg):
	descr = 'show setup.json, dataset list, etc for jobs'
	parser = ArgumentParser(
		prog=argv.pop(0),
		description=descr,
		formatter_class=RawTextHelpFormatter,
	)
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-o', '--output', action='store_true', help='show job output')
	group.add_argument('-O', '--just-output', action='store_true', help='show only job output')
	group.add_argument('-P', '--just-path', action='store_true', help='show only job path')
	group.add_argument('-s', '--source', action='store_true', help='show source used to produce job')
	group.add_argument('-S', '--source-file', metavar='PATTERN', help='show specified file(s) from source used to produce job')
	parser.add_argument(
		'jobid',
		nargs='+', metavar='jobid/jobspec',
		help='jobid is just a jobid.\n' +
		     'you can also use path, method or :urdlist:[entry].\n' +
		     'path is to a jobdir (with setup.json in it).\n' +
		     'method is the latest (current) job with that method (i.e\n' +
		     'the latest finished job with current source code).\n' +
		     ':urdlist:[entry] looks up jobs in urd. details are in the\n' +
		     'urd help, except here entry defaults to -1 and you can\'t\n' +
		     'list things (no .../ or .../since/x).\n' +
		     'you can use spec~ or spec~N to go back N current jobs\n' +
		     'with that method or spec^ or spec^N to follow .previous'
	)
	args = parser.parse_intermixed_args(argv)
	res = 0
	for path in args.jobid:
		try:
			job = name2job(cfg, path)
			if args.just_output:
				out = job.output()
				if out:
					print(out, end='' if out.endswith('\n') else '\n')
			elif args.just_path:
				print(job.path)
			elif args.source:
				show_source(job)
			elif args.source_file:
				show_source(job, args.source_file)
			else:
				show(cfg.url, job, args.output)
		except JobNotFound as e:
			print(e)
			res = 1
		except Exception as e:
			if isinstance(e, OSError) and e.errno == errno.EPIPE:
				raise
			print_exc(file=sys.stderr)
			print("Failed to show %r" % (path,), file=sys.stderr)
			res = 1
	return res
