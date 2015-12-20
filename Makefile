TARGETS := qtc libqtca.a libqtca.so
SRCS_C := qtc_aux.c qtc_mem.c print_bin.c strtol_ex.c label_addr.c
SRCS_MAIN_C := main.c
SRCS_L := qtc.anal.l
CFLAGS := -Wall -Wextra -O2 -g -pipe
ARFLAGS := cr
CC := gcc
LEX := lex
AR := ar
RANLIB := ranlib
RM := rm -f

all:

SRCS_L_C := $(SRCS_L:%.l=%.l.c)
SRCS := $(SRCS_C) $(SRCS_MAIN_C) $(SRCS_L_C)
SRCS_WITHOUT_MAIN := $(SRCS_C) $(SRCS_L_C)
OBJS := $(SRCS:%.c=%.c.o)
OBJS_WITHOUT_MAIN := $(SRCS_WITHOUT_MAIN:%.c=%.c.o)
DEPS := $(SRCS:%.c=%.c.d)
ALLDEPS = $(MAKEFILE_LIST_SANS_DEPS)

.PRECIOUS: $(SRCS_L_C)
.DELETE_ON_ERROR: $(SRCS_L_C)
.DELETE_ON_ERROR: $(DEPS)

VALID_MAKECMDGOALS := all $(TARGETS) %.c.o %.c.d %.l.c clean
NONEED_DEP_MAKECMDGOALS := clean

EXTRA_MAKECMDGOALS := $(filter-out $(VALID_MAKECMDGOALS), $(MAKECMDGOALS))
ifneq '$(EXTRA_MAKECMDGOALS)' ''
  $(error No rule to make target `$(word 1, $(EXTRA_MAKECMDGOALS))')
else
  ifeq '$(filter-out $(NONEED_DEP_MAKECMDGOALS), $(MAKECMDGOALS))' '$(MAKECMDGOALS)'
    sinclude $(DEPS)
	else
    ifneq '$(words $(MAKECMDGOALS))' '1'
      $(error Specify only one target if you want to make target which needs no source code dependency)
    endif
  endif
endif

MAKEFILE_LIST_SANS_DEPS := $(filter-out %.c.d, $(MAKEFILE_LIST))

LINK.o = $(CC) $(LDFLAGS) $(EXTRALDFLAGS) $(TARGET_ARCH)
COMPILE.o = $(CC) $(CFLAGS) $(EXTRACFLAGS) $(CPPFLAGS) $(EXTRACPPFLAGS) $(TARGET_ARCH) -shared
COMPILE.c = $(CC) $(CFLAGS) $(EXTRACFLAGS) $(CPPFLAGS) $(EXTRACPPFLAGS) $(TARGET_ARCH) -c
MKDEP.c = $(CC) $(CFLAGS) $(EXTRACFLAGS) $(CPPFLAGS) $(EXTRACPPFLAGS) $(TARGET_ARCH) -M -MP -MT $<.o -MF $@
LEX.l = $(LEX) $(LFLAGS) $(EXTRALFLAGS) -t

all: $(TARGETS)

qtc: $(OBJS) $(ALLDEPS)
	$(LINK.o) $(OUTPUT_OPTION) $(OBJS) $(LOADLIBES) $(LDLIBS)

libqtca.a: $(OBJS_WITHOUT_MAIN) $(ALLDEPS)
	$(AR) $(ARFLAGS) $@ $(OBJS_WITHOUT_MAIN)
	$(RANLIB) $@

libqtca.so: $(OBJS_WITHOUT_MAIN) $(ALLDEPS)
	$(COMPILE.o) $(OUTPUT_OPTION) $(OBJS_WITHOUT_MAIN) $(LOADLIBES) $(LDLIBS)

%.c.o: %.c $(ALLDEPS)
	$(COMPILE.c) $(OUTPUT_OPTION) $<

%.c.d: %.c $(ALLDEPS)
	$(MKDEP.c) $<

%.l.c: %.l $(ALLDEPS)
	$(RM) $@
	$(LEX.l) $< >$@

.PHONY: clean
clean:
	$(RM) $(TARGETS)
	$(RM) $(OBJS)
	$(RM) $(DEPS)
	$(RM) $(SRCS_L_C)
