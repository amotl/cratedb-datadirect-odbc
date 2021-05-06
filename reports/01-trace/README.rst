##########
Trace logs
##########


*****
About
*****

This folder contains trace logs of particular spots of the test suite as well
as corresponding comparison reports in form of diff files.

To produce those, the ``executemany`` strategy and the ``fast_executemany``
strategy have been invoked on each driver (``ddpsql`` vs. ``psqlodbc``).

Example::

	pytest -k "cratedb and ddpsql and many and fast" -vvv
	pytest -k "cratedb and ddpsql and many and not fast" -vvv


***********
Comparisons
***********


Sanitizing filter
=================

This is a small helper program for trimming log files before comparison::

	cat ddpsql-executemany-regular.log | ./sanitize.sh

Diff helper
===========

This is a small helper program for comparing pairs of log files::

	./compare.sh ddpsql > ddpsql.diff
	./compare.sh psqlodbc > psqlodbc.diff

Display diff reports
====================

It is recommended to apply some color::

	cat ddpsql.diff | colordiff
	cat psqlodbc.diff | colordiff
