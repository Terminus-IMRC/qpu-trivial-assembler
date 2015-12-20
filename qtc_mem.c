#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include "qtc_aux.h"
#include "qtc_mem.h"
#include "error.h"

#define QTC_MEM_TMPDIR "."

static int fd = -1;
static char fd_filename[] = QTC_MEM_TMPDIR "/" "XXXXXX";
static int max_str_len = 0;
static char *mstr = NULL;
static int len = 0;

void qtc_mem_init()
{
	static _Bool is_called = 0;
	mode_t umask_tmp, umask_set;
	int ret;

	if (is_called)
		return;
	is_called = !0;

	umask_set = S_IXUSR | S_IRWXG | S_IRWXO;
	umask_tmp = umask(umask_set);
	fd = mkstemp(fd_filename);
	umask_tmp = umask(umask_tmp);
	if (fd == -1) {
		error("mkstemp: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}
	if(umask_set != umask_tmp) {
		error("set %04o umask but %04o is returned\n", umask_set, umask_tmp);
		exit(EXIT_FAILURE);
	}

	ret = unlink(fd_filename);
	if (ret == -1) {
		error("close: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	ret = ftruncate(fd, 0);
	if (ret == -1) {
		error("ftruncate: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	max_str_len = 0;
	len = 0;
}

void qtc_mem_finalize()
{
	static _Bool is_called = 0;
	int ret;

	if (is_called)
		return;
	is_called = !0;

	ret = close(fd);
	if (ret == -1) {
		error("close: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}
}

void qtc_mem_inqueue(const inst_t inst, const char *str)
{
	int str_len;
	ssize_t rets;

	if (str == NULL)
		str_len = 0;
	else
		str_len = strlen(str);

	rets = write(fd, &inst, sizeof(inst));
	if (rets == -1) {
		error("write: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	rets = write(fd, &str_len, sizeof(str_len));
	if (rets == -1) {
		error("write: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	if (str_len != 0) {
		/* i.e. sans '\0' */
		rets = write(fd, str, str_len);
		if (rets == -1) {
			error("write: %s\n", strerror(errno));
			exit(EXIT_FAILURE);
		}
	}

	if (str_len > max_str_len)
		max_str_len = str_len;

	len ++;
}

void qtc_mem_dequeue_init()
{
	off_t reto;

	reto = lseek(fd, 0, SEEK_SET);
	if (reto == -1) {
		error("lseek: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	mstr = malloc((max_str_len + 1) * sizeof(mstr[0]));
	if (mstr == NULL) {
		error("failed to allocate mstr\n");
		exit(EXIT_FAILURE);
	}

	/* Alea iacta est. */
}

void qtc_mem_dequeue_finalize()
{
	free(mstr);
}

struct qtc_mem qtc_mem_dequeue()
{
	inst_t inst;
	int str_len;
	ssize_t rets;
	struct qtc_mem qm;

	rets = read(fd, &inst, sizeof(inst));
	if (rets == -1) {
		error("read: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	rets = read(fd, &str_len, sizeof(str_len));
	if (rets == -1) {
		error("read: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	if (str_len == 0) {
		rets = read(fd, mstr, str_len);
		if (rets == -1) {
			error("read: %s\n", strerror(errno));
			exit(EXIT_FAILURE);
		}
	}
	mstr[str_len] = '\0';

	qm.inst = inst;
	qm.str = mstr;

	return qm;
}

int qtc_mem_n()
{
	return len;
}
