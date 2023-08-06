if HAVE_LOCAL_LIBFCRYPTO
AM_CPPFLAGS = \
	-I$(top_srcdir)/include \
	-I$(top_srcdir)/common \
	@LIBCERROR_CPPFLAGS@ 

noinst_LTLIBRARIES = libfcrypto.la

libfcrypto_la_SOURCES = \
	libfcrypto_definitions.h \
	libfcrypto_extern.h \
	libfcrypto_error.c libfcrypto_error.h \
	libfcrypto_libcerror.h \
	libfcrypto_rc4_context.c libfcrypto_rc4_context.h \
	libfcrypto_serpent_context.c libfcrypto_serpent_context.h \
	libfcrypto_support.c libfcrypto_support.h \
	libfcrypto_types.h \
	libfcrypto_unused.h
endif

MAINTAINERCLEANFILES = \
	Makefile.in

distclean: clean
	/bin/rm -f Makefile

splint:
	@echo "Running splint on libfcrypto ..."
	-splint -preproc -redef $(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES) $(AM_CPPFLAGS) $(libfcrypto_la_SOURCES)

