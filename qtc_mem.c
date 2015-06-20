#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "qtc_aux.h"
#include "qtc_mem.h"
#include "error.h"

static struct qtc_mem **mems;
static const int mem_membs = 1024;
static int mem_len = 0;
static int minor_count = 0, major_count = 0;

static struct qtc_mem** qtc_mems_alloc(const int membs);
static struct qtc_mem* qtc_mem_alloc();
static void qtc_mem_update_mems(const int membs);

static struct qtc_mem** qtc_mems_alloc(const int membs)
{
	struct qtc_mem **p;

	p = malloc(membs * sizeof(struct qtc_mem*));
	if (p == NULL) {
		error("failed to allocate mems\n");
		exit(EXIT_FAILURE);
	}

	return p;
}

static struct qtc_mem* qtc_mem_alloc()
{
	struct qtc_mem *p;

	p = malloc(mem_membs * sizeof(struct qtc_mem));
	if (p == NULL) {
		error("failed to allocate mem\n");
		exit(EXIT_FAILURE);
	}

	return p;
}

static void qtc_mem_update_mems(const int membs)
{
	int i;
	struct qtc_mem **new_mems;

	for (i = membs; i < mem_len; i ++)
		free(mems[i]);
	new_mems = qtc_mems_alloc(membs);
	for (i = 0; i < ((membs < mem_len) ? membs : mem_len); i ++) {
		new_mems[i] = qtc_mem_alloc();
		memcpy(new_mems[i], mems[i], mem_membs * sizeof(struct qtc_mem));
		free(mems[i]);
	}
	free(mems);
	for (i = mem_len; i < membs; i ++)
		new_mems[i] = qtc_mem_alloc();

	mem_len = membs;
	mems = new_mems;
}

void qtc_mem_init()
{
	static _Bool is_called = 0;

	if (is_called)
		return;
	is_called = !0;

	mem_len = 1;
	mems = qtc_mems_alloc(mem_len);
	mems[0] = qtc_mem_alloc();
}

void qtc_mem_finalize()
{
	int i;
	static _Bool is_called = 0;

	if (is_called)
		return;
	is_called = !0;

	for (i = 0; i < mem_len; i ++)
		free(mems[i]);
	free(mems);
}

void qtc_mem_inqueue(const inst_t inst, char *str)
{
	if (minor_count == mem_membs) {
		qtc_mem_update_mems(mem_len + 1);
		major_count ++;
		minor_count = 0;
	}
	mems[major_count][minor_count].inst = inst;
	mems[major_count][minor_count].str = str;
	minor_count ++;
}

struct qtc_mem qtc_mem_dequeue()
{
	static int dmajor_count = 0, dminor_count = 0;

	if (dminor_count == mem_membs) {
		dmajor_count ++;
		if (dmajor_count > major_count) {
			error("too may dequeues\n");
			exit(EXIT_FAILURE);
		}
		dminor_count = 0;
	}
	if ((dmajor_count == major_count) && (dminor_count >= minor_count)) {
		error("too may dequeues\n");
		exit(EXIT_FAILURE);
	}
	return mems[dmajor_count][dminor_count ++];
}

int qtc_mem_n()
{
	return major_count * mem_membs + minor_count;
}
