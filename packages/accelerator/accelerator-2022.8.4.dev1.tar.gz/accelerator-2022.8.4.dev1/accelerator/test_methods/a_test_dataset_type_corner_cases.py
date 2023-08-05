# -*- coding: utf-8 -*-
############################################################################
#                                                                          #
# Copyright (c) 2019-2022 Carl Drougge                                     #
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

description = r'''
Verify various corner cases in dataset_type.
'''

from datetime import date, time, datetime
from math import isnan
import json
import sys

from accelerator import subjobs
from accelerator.dispatch import JobError
from accelerator.dataset import Dataset, DatasetWriter
from accelerator.dsutil import typed_writer
from accelerator.compat import PY3
from accelerator.standard_methods import dataset_type
from accelerator import g

options = {'numeric_comma': True}

depend_extra = (dataset_type,)

all_typenames = set(dataset_type.convfuncs)
used_typenames = set()

def used_type(typ):
	if ':' in typ and typ not in all_typenames:
		typ = typ.split(':', 1)[0] + ':*'
	used_typenames.add(typ)

no_default = object()
def verify(name, types, bytes_data, want, default=no_default, want_fail=False, all_source_types=False, **kw):
	todo = [('bytes', bytes_data,)]
	if all_source_types:
		uni_data = [v.decode('ascii') for v in bytes_data]
		todo += [('ascii', uni_data,), ('unicode', uni_data,)]
	for coltype, data in todo:
		dsname = '%s %s' % (name, coltype,)
		_verify(dsname, types, data, coltype, want, default, want_fail, kw)

def _verify(name, types, data, coltype, want, default, want_fail, kw):
	if callable(want):
		check = want
	else:
		def check(got, fromstr, filtered=False):
			want1 = want if isinstance(want, list) else want[typ]
			if filtered:
				want1 = want1[::2]
			assert got == want1, 'Expected %r, got %r from %s.' % (want1, got, fromstr,)
	dw = DatasetWriter(name=name, columns={'data': coltype, 'extra': 'bytes'})
	dw.set_slice(0)
	for ix, v in enumerate(data):
		dw.write(v, b'1' if ix % 2 == 0 else b'skip')
	for sliceno in range(1, g.slices):
		dw.set_slice(sliceno)
	bytes_ds = dw.finish()
	for typ in types:
		opts = dict(column2type=dict(data=typ))
		opts.update(kw)
		if default is not no_default:
			opts['defaults'] = {'data': default}
		try:
			jid = subjobs.build('dataset_type', datasets=dict(source=bytes_ds), options=opts)
		except JobError:
			if want_fail:
				continue
			raise Exception('Typing %r as %s failed.' % (bytes_ds, typ,))
		assert not want_fail, "Typing %r as %s should have failed, but didn't (%s)." % (bytes_ds, typ, jid)
		typed_ds = Dataset(jid)
		got = list(typed_ds.iterate(0, 'data'))
		check(got, '%s (typed as %s from %r)' % (typed_ds, typ, bytes_ds,))
		if opts.get('filter_bad'):
			bad_ds = Dataset(jid, 'bad')
			got_bad = list(bad_ds.iterate(0, 'data'))
			assert got_bad == [b'nah'], "%s should have had a single b'nah', but had %r" % (bad_ds, got_bad,)
		if 'filter_bad' not in opts and not callable(want):
			opts['filter_bad'] = True
			opts['column2type']['extra'] = 'int32_10'
			jid = subjobs.build('dataset_type', datasets=dict(source=bytes_ds), options=opts)
			typed_ds = Dataset(jid)
			got = list(typed_ds.iterate(0, 'data'))
			check(got, '%s (typed as %s from %r with every other line skipped from filter_bad)' % (typed_ds, typ, bytes_ds,), True)
			want_bad = [t for t in bytes_ds.iterate(0) if t[1] == b'skip']
			bad_ds = Dataset(jid, 'bad')
			got_bad = list(bad_ds.iterate(0))
			assert got_bad == want_bad, "Expected %r, got %r from %s" % (want_bad, got_bad, bad_ds,)
		used_type(typ)

def test_numbers():
	verify('floats', ['complex32', 'complex64', 'float32', 'float64', 'number'], [b'1.50', b'-inf', b'5e-1'], [1.5, float('-inf'), 0.5], all_source_types=True)
	if options.numeric_comma:
		verify('numeric_comma', ['complex32', 'complex64', 'float32', 'float64', 'number'], [b'1,5', b'1.0', b'9'], [1.5, 42.0, 9.0], '42', numeric_comma=True)
	verify('float32 rounds', ['complex32', 'float32'], [b'1.2'], [1.2000000476837158])
	verify('filter_bad', ['int32_10', 'int64_10', 'bits32_10', 'bits64_10', 'complex32', 'complex64', 'float32', 'float64', 'number'], [b'4', b'nah', b'1', b'0'], [4, 1, 0], filter_bad=True)

	all_source_types = True
	for base, values in (
		(10, (b'27', b'027', b' \r27 '),),
		( 8, (b'33', b'033', b'\t000033'),),
		(16, (b'1b', b'0x1b', b'\r001b',),),
		( 0, (b'27', b'\r033', b'0x1b',),),
	):
		types = ['%s_%d' % (typ, base,) for typ in ('int32', 'int64', 'bits32', 'bits64')]
		verify('base %d' % (base,), types, values, [27, 27, 27], all_source_types=all_source_types)
		types = [typ + 'i' for typ in types]
		if base == 10:
			types += ['float32i', 'float64i']
		values = [v + b'garbage' for v in values]
		verify('base %d i' % (base,), types, values, [27, 27, 27], all_source_types=all_source_types)
		all_source_types = False
	verify('inty numbers', ['number', 'number:int'], [b'42', b'42.0', b'42.0000000', b'43.'], [42, 42, 42, 43])
	if options.numeric_comma:
		verify('inty numbers numeric_comma', ['number', 'number:int'], [b'42', b'42,0', b'42,0000000', b'43,'], [42, 42, 42, 43], numeric_comma=True)

	# Python 2 accepts 42L as an integer, python 3 doesn't. The number
	# type falls back to python parsing, verify this works properly.
	verify('integer with L', ['number'], [b'42L'], [42], want_fail=PY3)

	# tests both that values outside the range are rejected
	# and that None works as a default value for relevant types.
	for typ, values, default in (
		('int32_10', (b'2147483648', b'-2147483648', b'1O',), '123',),
		('int32_16', (b'80000000', b'-80000000', b'1O',), None,),
		('int64_10', (b'36893488147419103231', b'9223372036854775808', b'-9223372036854775808', b'1O',), None,),
		('bits32_10', (b'4294967296', b'8589934591', b'-1', b'1O',), '456',),
		('bits64_10', (b'36893488147419103231', b'18446744073709551616', b'-1', b'1O',), '789',),
	):
		if default is None:
			want = [None] * len(values)
		else:
			want = [int(default)] * len(values)
		verify('nearly good numbers ' + typ, [typ], values, want, default)

	verify('not a number', ['number'], [b'forty two'], [42], want_fail=True)

	verify('strbool', ['strbool'], [b'', b'0', b'FALSE', b'f', b'FaLSe', b'no', b'off', b'NIL', b'NULL', b'y', b'jao', b'well, sure', b' ', b'true'], [False] * 9 + [True] * 5)
	verify('floatbool false', ['floatbool'], [b'0', b'-0', b'1', b'1004', b'0.00001', b'inf', b'-1', b'', b'0.00'], [False, False, True, True, True, True, True, False, False])
	verify('floatbool i', ['floatbooli'], [b'1 yes', b'0 no', b'0.00 also no', b'inf yes', b' 0.01y'], [True, False, False, True, True])
	for typ, smallbig, smallneg, bigbig, bigneg, extra in (
		('floatint32e', 42, 42, 42, 42, 42,),
		('floatint32ei', 42, 42, 42, 42, 1,),
		('floatint32s', 2147483647, -2147483647, 2147483647, -2147483647, 42,),
		('floatint32si', 2147483647, -2147483647, 2147483647, -2147483647, 1,),
		('floatint64e', 10000000000, -2147483648, 42, -2200000000, 42,),
		('floatint64ei', 10000000000, -2147483648, 42, -2200000000, 1,),
		('floatint64s', 10000000000, -2147483648, 9223372036854775807, -2200000000, 42,),
		('floatint64si', 10000000000, -2147483648, 9223372036854775807, -2200000000, 1,),
	):
		verify(typ, [typ], [b'1.99', b'-3000', b'1e10', b'-2147483648', b'1e100', b'-2.2e9', b'-7.89', b'1.half'], [1, -3000, smallbig, smallneg, bigbig, bigneg, -7, extra], '42')
	def check_special(got, fromstr):
		msg = 'Expected [inf, -inf, nan, nan, nan, nan, inf], got %r from %s.' % (got, fromstr,)
		for ix, v in ((0, float('inf')), (1, float('-inf')), (-1, float('inf'))):
			assert got[ix] == v, msg
		for ix in range(2, 6):
			v = got[ix]
			if isinstance(v, complex):
				v = v.real
			assert isnan(v), msg
	verify('special floats', ['complex32', 'complex64', 'float32', 'float64', 'number'], [b'+Inf', b'-inF', b'nan', b'NaN', b'NAN', b'Nan', b'INF'], check_special)
	verify('complex', ['complex32', 'complex64'], [b'0.25-5j', b'-0.5j', b'infj'], [0.25-5j, -0.5j, complex(0, float('inf'))])
	if options.numeric_comma:
		verify('complex numeric_comma', ['complex32', 'complex64'], [b'-0,5+1,5j', b'-0,5+1.5j', b',5j'], [-0.5+1.5j, 42j, 0.5j], '42j', numeric_comma=True)

def test_bytes():
	want = [b'foo', b'\\bar', b'bl\xe4', b'\x00\t \x08', b'a\xa0b\x255\x00']
	for typs, data in (
		(['bytes', 'bytesstrip'], want,),
		(['bytesstrip'], [b'\t\t\t\rfoo\n \x0c', b'\\bar', b'bl\xe4   \x0b', b' \x00\t \x08', b'a\xa0b\x255\x00\n'],),
	):
		verify(typs[0], typs, data, want)

def test_ascii():
	for prefix, data in (
		('ascii', [b'foo', b'\\bar', b'bl\xe4', b'\x00\t \x08'],),
		('asciistrip', [b'\t\t\t\rfoo\n \x0c', b'\\bar', b'bl\xe4   \x0b', b' \x00\t \x08\t'],),
	):
		for encode, want in (
			(None,      ['foo', '\\bar',    'bl\\344', '\x00\t \x08'],),
			('replace', ['foo', '\\bar',    'bl\\344', '\x00\t \x08'],),
			('encode',  ['foo', '\\134bar', 'bl\\344', '\x00\t \x08'],),
			('strict',  ['foo', '\\bar',    None,      '\x00\t \x08'],),
		):
			if encode:
				typ = prefix + ':' + encode
			else:
				typ = prefix
			verify(typ, [typ], data, want, default=None)
	verify(
		'ascii all source types', ['ascii', 'asciistrip'],
		[b'\t\t\t\rfoo\r \x0c', b'\\bar', b' \x00\t \x08\t'],
		{
			'ascii': ['\t\t\t\rfoo\r \x0c', '\\bar', ' \x00\t \x08\t'],
			'asciistrip': ['foo', '\\bar', '\x00\t \x08'],
		},
		all_source_types=True,
	)

def test_unicode():
	data = [b'foo bar\n', b'\tbl\xe5', b'\tbl\xe5a \xe4  ', b'\tbl\xc3\xa5a ', b'\r+AOU-h']
	want = {
		'unicode:utf-8': ['foo bar\n', '既定 ', '既定 ', '\tblåa ', '\r+AOU-h'],
		'unicode:utf-8/strict': ['foo bar\n', '既定 ', '既定 ', '\tblåa ', '\r+AOU-h'],
		'unicode:utf-8/replace': ['foo bar\n', '\tbl\ufffd', '\tbl\ufffda \ufffd  ', '\tblåa ', '\r+AOU-h'],
		'unicode:utf-8/ignore': ['foo bar\n', '\tbl', '\tbla   ', '\tblåa ', '\r+AOU-h'],
		'unicode:iso-8859-1': ['foo bar\n', '\tblå', '\tblåa ä  ', '\tbl\xc3\xa5a ', '\r+AOU-h'],
		'unicode:ascii/replace': ['foo bar\n', '\tbl\ufffd', '\tbl\ufffda \ufffd  ', '\tbl\ufffd\ufffda ', '\r+AOU-h'],
		'unicode:ascii/ignore': ['foo bar\n', '\tbl', '\tbla   ', '\tbla ', '\r+AOU-h'],
		'unicode:utf-7/ignore': ['foo bar\n', '\tbl', '\tbla   ', '\tbla ', '\råh'],
		'unicode:utf-7/replace': ['foo bar\n', '\tbl\ufffd', '\tbl\ufffda \ufffd  ', '\tbl\ufffd\ufffda ', '\råh'],
		'unicodestrip:utf-8': ['foo bar', '既定', '既定', 'blåa', '+AOU-h'],
		'unicodestrip:utf-8/strict': ['foo bar', '既定', '既定', 'blåa', '+AOU-h'],
		'unicodestrip:utf-8/replace': ['foo bar', 'bl\ufffd', 'bl\ufffda \ufffd', 'blåa', '+AOU-h'],
		# strip happens before ignore, so strip+ignore will have one space from '\tbl\xe5a \xe4  '
		'unicodestrip:utf-8/ignore': ['foo bar', 'bl', 'bla ', 'blåa', '+AOU-h'],
		'unicodestrip:iso-8859-1': ['foo bar', 'blå', 'blåa ä', 'bl\xc3\xa5a', '+AOU-h'],
		'unicodestrip:ascii/replace': ['foo bar', 'bl\ufffd', 'bl\ufffda \ufffd', 'bl\ufffd\ufffda', '+AOU-h'],
		'unicodestrip:ascii/ignore': ['foo bar', 'bl', 'bla ', 'bla', '+AOU-h'],
		'unicodestrip:utf-7/ignore': ['foo bar', 'bl', 'bla ', 'bla', 'åh'],
		'unicodestrip:utf-7/replace': ['foo bar', 'bl\ufffd', 'bl\ufffda \ufffd', 'bl\ufffd\ufffda', 'åh'],
	}
	verify('unicode', list(want), data, want, default='既定 ');
	# 既定 is not ascii, so we need a separate default for ascii-like types.
	want = {
		'unicode:ascii/strict': ['foo bar\n', 'standard', 'standard', 'standard', '\r+AOU-h'],
		'unicodestrip:ascii/strict': ['foo bar', 'standard', 'standard', 'standard', '+AOU-h'],
		'unicodestrip:utf-7/strict': ['foo bar', 'standard', 'standard', 'standard', 'åh'],
	}
	verify('unicode with ascii default', list(want), data, want, default='standard');
	verify('utf7 all', ['unicode:utf-7/replace'], [b'a+b', b'a+-b', b'+ALA-'], ['a\ufffd', 'a+b', '°'], all_source_types=True);

def test_datetimes():
	# These use the libc functions, so may only work for dates after 1900.
	# They also use the python datetime classes to verify valid dates,
	# so on Python < 3.6 they will accept various invalid dates if strptime
	# does. So we only try nearly-good dates on Python 3.6+.
	todo = [
		('date YYYYMMDD', 'date:%Y%m%d', [b'20190521', b'19700101', b'1970-01-01', b'1980', b'nah'], [date(2019, 5, 21), date(1970, 1, 1), date(1945, 6, 20), date(1945, 6, 20), date(1945, 6, 20)], '19450620', True,),
		('date spacy YYYYMMDD', 'date: %Y %m %d', [b'20190521', b'   1970 01\n\n\n01', b'1970\t1 1    ', b'70 0 0', b'1981'], [date(2019, 5, 21), date(1970, 1, 1), date(1970, 1, 1), date(1945, 6, 20), date(1945, 6, 20)], '1945 6 20', False,),
		('date YYYYblahMMDD', 'date:%Yblah%m%d', [b'2019blah0521', b'1970blah0101', b'1970blah-01-01', b'1980blah', b'nah'], [date(2019, 5, 21), date(1970, 1, 1), date(1945, 6, 20), date(1945, 6, 20), date(1945, 6, 20)], '1945blah0620', True,),
		('datetime hhmmYYMMDD', 'datetime:%H%M%y%m%d', [b'1852190521', b'0000700101', b'today'], [datetime(2019, 5, 21, 18, 52), datetime(1970, 1, 1), datetime(1978, 1, 1)], '0000780101', False,),
		('datetime YYYYMMDD HHMMSS.mmmmmm', 'datetime:%Y%m%d %H%M%S.%f', [b'20190521 185206.123', b'19700203040506.000007', b'19700203040506.-00007', b'today'], [datetime(2019, 5, 21, 18, 52, 6, 123000), datetime(1970, 2, 3, 4, 5, 6, 7), datetime(1978, 1, 1), datetime(1978, 1, 1)], '19780101 000000.0', True,),
		('time HH:MM', 'time:%H:%M', [b'03:14', b'18:52', b'25:10'], [time(3, 14), time(18, 52), time(0, 42)], '00:42', True,),
		('time HHMMpercentfSS', 'time:%H%M%%f%S', [b'0314%f00', b'1852%f09', b'1938%f60'], [time(3, 14), time(18, 52, 9), time(0, 42, 18)], '0042%f18', False,),
		('time HHMM mmm.SS', 'time:%H%M %f.%S', [b'03149.00', b'1852456.09', b'1938   123456.44', b'1938123456.60', b'1852456   .09', b'1852456    .09'], [time(3, 14, 0, 900000), time(18, 52, 9, 456000), time(19, 38, 44, 123456), time(0, 42, 18), time(18, 52, 9, 456000), time(0, 42, 18)], '004200.18', False,),
		('date MMDD', 'date:%m%d', [b'0101', b'1020', b'nah'], [date(1970, 1, 1), date(1970, 10, 20), date(1970, 6, 20)], '0620', False,),
		('datetime YY', 'datetime:%y', [b'70', b'2000', b'19'], [datetime(1970, 1, 1, 0, 0, 0), None, datetime(2019, 1, 1, 0, 0, 0)], None, False,),
		('datetime mmmmmmDD', 'datetime:%f%d', [b'00030030', b'00000006', b'00003003', b'99999999', b'99999911'], [datetime(1970, 1, 30, microsecond=300), datetime(1970, 1, 6), datetime(1970, 1, 3, microsecond=30), None, datetime(1970, 1, 11, microsecond=999999)], None, False,),
		('datetime mmmmmm.DD', 'datetime:%f.%d', [b'30.30', b'0.06', b'00030.03', b'999999.99', b'999999.11'], [datetime(1970, 1, 30, microsecond=300000), datetime(1970, 1, 6), datetime(1970, 1, 3, microsecond=300), None, datetime(1970, 1, 11, microsecond=999999)], None, False,),
		('datetime mmmmmmpercentfpercentDD', 'datetime:%f%%f%%%d', [b'30%f%30', b'0%f%06', b'00030%f%03', b'999999%f%99', b'999999%f%11'], [datetime(1970, 1, 30, microsecond=300000), datetime(1970, 1, 6), datetime(1970, 1, 3, microsecond=300), None, datetime(1970, 1, 11, microsecond=999999)], None, False,),
		('datetime unix.f', 'datetime:%s.%f', [b'30.30', b'1558662853.847211', b''], [datetime(1970, 1, 1, 0, 0, 30, 300000), datetime(2019, 5, 24, 1, 54, 13, 847211), datetime(1970, 1, 1, microsecond=100000)], '0.1', False,),
		('datetime java', 'datetime:%J', [b'0', b'1558662853847', b'', b'-2005'], [datetime(1970, 1, 1), datetime(2019, 5, 24, 1, 54, 13, 847000), datetime(1970, 1, 1, 0, 0, 0, 1000), datetime(1969, 12, 31, 23, 59, 57, 995000)], '1', False,),
		('datetime java blahbluh', 'datetime:blah%Jbluh', [b'blah0bluh', b'blah   30000bluh', b'bla0bluh', b'blah0blu', b'blah-2005bluh'], [datetime(1970, 1, 1), datetime(1970, 1, 1, 0, 0, 30), datetime(1970, 1, 1, 0, 0, 0, 1000), datetime(1970, 1, 1, 0, 0, 0, 1000), datetime(1969, 12, 31, 23, 59, 57, 995000)], 'blah1bluh', False,),
	]
	if sys.version_info >= (3, 6):
		todo.extend((
			('nearly good date YYYY-MM-DD', 'date:%Y-%m-%d', [b'2019-02-29', b'1970-02-31', b'1980-06-31', b'1992-02-29'], [None, None, None, date(1992, 2, 29)], None, False,),
			('nearly good datetime YYYY-MM-DD', 'datetime:%Y-%m-%d', [b'2019-02-29', b'1970-02-31', b'1980-06-31', b'1992-02-29'], [None, None, None, datetime(1992, 2, 29)], None, False,),
		))
	for name, typ, data, want, default, all_source_types in todo:
		verify(name, [typ], data, want, default, all_source_types=all_source_types)
		if default is not None:
			if typ.endswith('%f') or typ.endswith('%J'):
				idata = [v + b'abc123' for v in data]
				default += 'a2'
			else:
				idata = [v + b'1868' for v in data]
				default += '42'
			verify(name + ' i', [typ.replace(':', 'i:', 1)], idata, want, default)
	# Timezone tests. I hope all systems accept the :Region/City syntax.
	verify('tz a', ['datetime:%Y-%m-%d %H:%M'], [b'2020-09-30 11:44'], [datetime(2020, 9, 30, 11, 44)])
	verify('tz b', ['datetime:%Y-%m-%d %H:%M'], [b'2020-09-30 11:44'], [datetime(2020, 9, 30, 11, 44)], timezone='UTC')
	verify('tz c', ['datetime:%Y-%m-%d %H:%M'], [b'2020-09-30 13:44', b'2020-02-22 12:44'], [datetime(2020, 9, 30, 11, 44), datetime(2020, 2, 22, 11, 44)], timezone=':Europe/Stockholm')

def test_filter_bad_across_types():
	columns={
		'bytes': 'bytes',
		'float64': 'bytes',
		'int32_10': 'ascii',
		'json': 'unicode',
		'number:int': 'unicode',
		'unicode:utf-8': 'bytes',
	}
	# all_good, *values
	# Make sure all those types (except bytes) can filter other lines,
	# and be filtered by other lines. And that several filtering values
	# is not a problem (line 11).
	data = [
		[True,  b'first',    b'1.1', '1',  '"a"',   '001', b'ett',],
		[True,  b'second',   b'2.2', '2',  '"b"',   '02',  b'tv\xc3\xa5',],
		[True,  b'third',    b'3.3', '3',  '["c"]', '3.0', b'tre',],
		[False, b'fourth',   b'4.4', '4',  '"d"',   '4.4', b'fyra',],       # number:int bad
		[False, b'fifth',    b'5.5', '-',  '"e"',   '5',   b'fem',],        # int32_10 bad
		[False, b'sixth',    b'6.b', '6',  '"f"',   '6',   b'sex',],        # float64 bad
		[False, b'seventh',  b'7.7', '7',  '{"g"}', '7',   b'sju',],        # json bad
		[False, b'eigth',    b'8.8', '8',  '"h"',   '8',   b'\xa5\xc3tta',],# unicode:utf-8 bad
		[True,  b'ninth',    b'9.9', '9',  '"i"',   '9',   b'nio',],
		[True,  b'tenth',    b'10',  '10', '"j"',   '10',  b'tio',],
		[False, b'eleventh', b'11a', '1-', '"k",',  '1,',  b'elva',],       # float64, int32_10 and number:int bad
		[True,  b'twelfth',  b'12',  '12', '"l"',   '12',  b'tolv',],
	]
	want_bad = [tuple(l[1:]) for l in data if not l[0]]
	dw = DatasetWriter(name="filter bad across types", columns=columns, allow_missing_slices=True)
	cols_to_check = ['int32_10', 'bytes', 'json', 'unicode:utf-8']
	if PY3:
		# z so it sorts last.
		dw.add('zpickle', 'pickle')
		cols_to_check.append('zpickle')
		for ix in range(len(data)):
			data[ix].append({ix})
	dw.set_slice(0)
	want = []
	def add_want(ix):
		v = data[ix]
		want.append((int(v[3]), v[1], json.loads(v[4]), v[6].decode('utf-8'),))
		if PY3:
			want[-1] = want[-1] + (v[7],)
	for ix, v in enumerate(data):
		if v[0]:
			add_want(ix)
		dw.write(*v[1:])
	source_ds = dw.finish()
	# Once with just filter_bad, once with some defaults too.
	defaults = {}
	for _ in range(2):
		jid = subjobs.build(
			'dataset_type',
			datasets=dict(source=source_ds),
			options=dict(column2type={t: t for t in columns}, filter_bad=True, defaults=defaults),
		)
		typed_ds = Dataset(jid)
		got = list(typed_ds.iterate(0, cols_to_check))
		assert got == want, "Expected %r, got %r from %s (from %r%s)" % (want, got, typed_ds, source_ds, ' with defaults' if defaults else '')
		bad_ds = Dataset(jid, 'bad')
		got_bad = list(bad_ds.iterate(0, sorted(columns)))
		assert got_bad == want_bad, "Expected %r, got %r from %s (from %r%s)" % (want_bad, got_bad, bad_ds, source_ds, ' with defaults' if defaults else '')
		# make more lines "ok" for the second lap
		if not defaults:
			want_bad.pop(0) # number:int
			want_bad.pop(1) # float64
			want_bad.pop(1) # json
		defaults = {'number:int': '0', 'float64': '0', 'json': '"replacement"'}
		add_want(3)
		add_want(5)
		data[6][4] = '"replacement"'
		add_want(6)
		want.sort() # adding them out of order, int32_10 sorts correctly.

def test_rename():
	def mk(name, **kw):
		dw = DatasetWriter(name='rename_' + name, **kw)
		dw.add('a', 'ascii')
		dw.add('b', 'bytes')
		dw.add('c', 'unicode', none_support=True)
		dw.get_split_write()('0', b'1', '2')
		return dw.finish()
	plain = mk('plain')
	with_hashlabel = mk('with_hashlabel', hashlabel='a')

	# Rename all, with some name hidden. Untyped a remains visible.
	jid = subjobs.build(
		'dataset_type',
		column2type=dict(b='int32_10', c='int64_10', d='number'),
		rename=dict(a='b', b='c', c='d'),
		source=plain,
	)
	typed_ds = jid.dataset()
	coltypes = sorted((name, col.type, col.none_support) for name, col in typed_ds.columns.items())
	assert coltypes == [('a', 'ascii', False), ('b', 'int32', False), ('c', 'int64', False), ('d', 'number', True)], coltypes
	assert list(typed_ds.iterate(None)) == [('0', 0, 1, 2)]

	# Rename hashlabel a => b, c untouched except for rehashing
	jid = subjobs.build(
		'dataset_type',
		column2type=dict(b='int32_10'),
		rename=dict(a='b'),
		source=with_hashlabel,
	)
	typed_ds = jid.dataset()
	coltypes = sorted((name, col.type, col.none_support) for name, col in typed_ds.columns.items())
	assert coltypes == [('b', 'int32', False), ('c', 'unicode', True)], coltypes
	assert list(typed_ds.iterate(None)) == [(0, '2')]
	assert typed_ds.hashlabel == 'b'

	# Discard hashlabel
	jid = subjobs.build(
		'dataset_type',
		column2type=dict(b='int32_10'),
		rename=dict(a=None),
		source=with_hashlabel,
	)
	typed_ds = jid.dataset()
	coltypes = sorted((name, col.type, col.none_support) for name, col in typed_ds.columns.items())
	assert coltypes == [('b', 'int32', False), ('c', 'unicode', True)], coltypes
	assert list(typed_ds.iterate(None)) == [(1, '2')]
	assert typed_ds.hashlabel == None

def test_filter_bad_with_rename_and_chain():
	dw = DatasetWriter(name="filter bad with rename", allow_missing_slices=True)
	dw.add('a', 'ascii')
	dw.add('b', 'bytes')
	dw.add('c', 'unicode')
	dw.set_slice(0)
	dw.write('0', b'1', '2')
	dw.write('9', B'A', 'B')
	dw.write('C', B'D', 'E')
	source_ds = dw.finish()
	jid = subjobs.build(
		'dataset_type',
		column2type=dict(b='int32_10', c='int64_16', d='int32_16'),
		filter_bad=True,
		rename=dict(a='b', b='c', c='d'),
		source=source_ds,
	)
	typed_ds = jid.dataset()
	coltypes = sorted((name, col.type) for name, col in typed_ds.columns.items())
	assert coltypes == [('b', 'int32'), ('c', 'int64'), ('d', 'int32')], coltypes
	assert list(typed_ds.iterate(0)) == [(0, 1, 2), (9, 10, 11)]
	bad_ds = jid.dataset('bad')
	coltypes = sorted((name, col.type) for name, col in bad_ds.columns.items())
	assert coltypes == [('b', 'ascii'), ('c', 'bytes'), ('d', 'unicode')], coltypes
	assert list(bad_ds.iterate(0)) == [('C', b'D', 'E')]

	dw = DatasetWriter(name="filter bad with rename chain", allow_missing_slices=True, previous=source_ds)
	dw.add('a', 'ascii')
	dw.add('b', 'ascii')
	dw.add('c', 'ascii')
	dw.set_slice(0)
	dw.write('3', '4', '5')
	dw.write('6', '7', 'eight')
	source_ds = dw.finish()
	jid = subjobs.build(
		'dataset_type',
		column2type=dict(a='number', b='int32_10', c='int64_10'),
		defaults=dict(a='8'),
		filter_bad=True,
		rename=dict(a='b', b='c', c='a'),
		source=source_ds,
	)
	typed_ds = jid.dataset()
	coltypes = sorted((name, col.type) for name, col in typed_ds.columns.items())
	assert coltypes == [('a', 'number'), ('b', 'int32'), ('c', 'int64')], coltypes
	assert list(typed_ds.iterate(0)) == [(2, 0, 1), (5, 3, 4), (8, 6, 7)]
	bad_ds = jid.dataset('bad')
	coltypes = sorted((name, col.type) for name, col in bad_ds.columns.items())
	assert coltypes == [('a', 'unicode'), ('b', 'ascii'), ('c', 'bytes')], coltypes
	assert list(bad_ds.iterate(0)) == [('B', '9', b'A'), ('E', 'C', b'D')]

def test_None():
	types = {
		'bool': 'floatbool',
		'complex32': 'complex32', 'complex64': 'complex64',
		'float32': 'float32', 'float64': 'float64',
		'int32': 'int32_10', 'int64': 'int64_10',
		'number': 'number',
		'date': 'date:%Y-%m-%d',
		'datetime': 'datetime:%Y-%m-%dT%H:%M:%S',
		'time': 'time:%H:%M:%S',
		'ascii': 'ascii:strict', 'unicode': 'unicode:utf-8',
	}
	values = {
		'bool': b'-1',
		'date': b'2022-07-08',
		'datetime': b'2022-07-08T22:23:24',
		'time': b'22:23:24',
		'ascii': b'text',
		'unicode': b'\xe5\xad\x97',
	}
	values = {k: values.get(k, b'%d' % (ix,)) for ix, k in enumerate(sorted(types))}
	want_values = {
		'bool': True,
		'date': date(2022, 7, 8),
		'datetime': datetime(2022, 7, 8, 22, 23, 24),
		'time': time(22, 23, 24),
		'ascii': 'text',
		'unicode': '字',
	}
	want_values = {k: want_values.get(k, ix) for ix, k in enumerate(sorted(types))}
	def test(name, dw_kw, type_kw, write_lines, want_none_count):
		dw = DatasetWriter(name=name, allow_missing_slices=True, **dw_kw)
		for typ in types:
			dw.add(typ, 'bytes', none_support=True)
		dw.set_slice(0)
		for d in write_lines:
			dw.write(**d)
		source_ds = dw.finish()
		ds = subjobs.build(
			'dataset_type',
			source=source_ds,
			column2type=types,
			**type_kw
		).dataset()
		for colname, value in want_values.items():
			want = [value] + [None] * want_none_count
			assert list(ds.iterate(0, colname)) == want, colname
		return source_ds
	# One line with good values, one with Nones
	prev = test('None values', {}, {}, [values, dict.fromkeys(values, None)], 1)
	# One line with bad values (plus the previous ds)
	test('bad None values', {'previous': prev}, {'defaults': dict.fromkeys(values, None)}, [dict.fromkeys(values, b'\xff')], 2)

def test_column_discarding():
	dw = DatasetWriter(name='column discarding')
	dw.add('a', 'bytes')
	dw.add('b', 'bytes')
	dw.add('c', 'bytes')
	w = dw.get_split_write()
	w(b'a', b'b', b'c')
	source = dw.finish()

	# Discard b because it's not typed
	ac_implicit = subjobs.build(
		'dataset_type',
		source=source,
		column2type=dict(a='ascii', c='ascii'),
		discard_untyped=True,
	).dataset()
	assert sorted(ac_implicit.columns) == ['a', 'c'], '%s: %r' % (ac_implicit, sorted(ac_implicit.columns),)
	assert list(ac_implicit.iterate(None)) == [('a', 'c',)], ac_implicit

	# Discard b explicitly
	ac_explicit = subjobs.build(
		'dataset_type',
		source=source,
		column2type=dict(a='ascii', c='ascii'),
		rename=dict(b=None),
	).dataset()
	assert sorted(ac_explicit.columns) == ['a', 'c'], '%s: %r' % (ac_explicit, sorted(ac_explicit.columns),)
	assert list(ac_explicit.iterate(None)) == [('a', 'c',)], ac_explicit

	# Discard c by overwriting it with b. Keep untyped b.
	ac_bASc = subjobs.build(
		'dataset_type',
		source=source,
		column2type=dict(a='ascii', c='ascii'),
		rename=dict(b='c'),
	).dataset()
	assert sorted(ac_bASc.columns) == ['a', 'b', 'c'], '%s: %r' % (ac_bASc, sorted(ac_bASc.columns),)
	assert list(ac_bASc.iterate(None)) == [('a', b'b', 'b',)], ac_bASc

	# Discard c by overwriting it with b. Also type b as a different type.
	abc_bASc = subjobs.build(
		'dataset_type',
		source=source,
		column2type=dict(a='ascii', b='strbool', c='ascii'),
		rename=dict(b='c'),
	).dataset()
	assert sorted(abc_bASc.columns) == ['a', 'b', 'c'], '%s: %r' % (abc_bASc, sorted(abc_bASc.columns),)
	assert list(abc_bASc.iterate(None)) == [('a', True, 'b',)], abc_bASc

def test_rehash_with_empty_slices():
	dw = DatasetWriter(name='rehash with empty slices', hashlabel='a')
	dw.add('a', 'ascii')
	dw.add('b', 'ascii')
	w = dw.get_split_write()
	w('a', '42')
	w('42', 'b')
	source = dw.finish()
	hashfunc = typed_writer('int32').hash
	def verify_hashing(caption, want_values, **kw):
		ds = subjobs.build(
			'dataset_type',
			source=source,
			column2type=dict(a='int32_10'),
			caption=caption,
			**kw
		).dataset()
		got_values = set()
		for sliceno in range(g.slices):
			for got in ds.iterate(sliceno):
				assert hashfunc(got[0]) % g.slices == sliceno
				assert got not in got_values
				got_values.add(got)
		assert want_values == got_values
	verify_hashing('with discard', {(42, 'b',)}, filter_bad=True)
	# using defaults uses some different code paths
	verify_hashing('with default=0 (probably two slices)', {(0, '42',), (42, 'b',)}, defaults=dict(a='0'))
	verify_hashing('with default=42 (one slice)', {(42, '42',), (42, 'b',)}, defaults=dict(a='42'))

def synthesis():
	test_bytes()
	test_ascii()
	test_unicode()
	test_numbers()
	test_datetimes()
	test_None()
	test_column_discarding()
	test_rehash_with_empty_slices()
	test_rename()

	verify('json', ['json'],
		[b'null', b'[42, {"a": "b"}]', b'\r  {  "foo":\r"bar" \r   }\t ', b'nope'],
		[None, [42, {'a': 'b'}], {'foo': 'bar'}, ['nah']],
		default='["nah"]', all_source_types=True,
	)

	test_filter_bad_across_types()
	test_filter_bad_with_rename_and_chain()

	for t in (all_typenames - used_typenames):
		print(t)
