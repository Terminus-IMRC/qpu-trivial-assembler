#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include "diskstorage.h"
#include "error.h"

/*
 * +--------------------+---------+--------------------+---------+-----+
 * | length of entry #1 | data #1 | length of entry #2 | data #2 | ... |
 * +--------------------+---------+--------------------+---------+-----+
 * Length does NOT involve itself.
 */

void diskstorage_init(diskstorage_stat_t *dstp)
{
	int fd;
	int umask_set, umask_orig;
	char filename[] = "tmp-qtc-XXXXXX";
	int ret;

	umask_set = S_IXUSR | S_IRWXG | S_IRWXO;
	umask_orig = umask(umask_set);
	fd = mkstemp(filename);
	umask(umask_orig);
	if (fd == -1) {
		error("mkstemp: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	ret = unlink(filename);
	if (ret == -1) {
		error("unlink: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	ret = ftruncate(fd, 0);
	if (ret == -1) {
		error("ftruncate: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	dstp->fd = fd;
	dstp->len_max = 0;
}

void diskstorage_finalize(diskstorage_stat_t *dstp)
{
	int fd = dstp->fd;
	int ret;

	ret = close(fd);
	if (ret == -1) {
		error("close: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	dstp->fd = -1;
	dstp->len_max = 0;
}

void diskstorage_append(void *data, int len, diskstorage_stat_t *dstp)
{
	int fd = dstp->fd;
	int len_max = dstp->len_max;
	off_t reto;
	ssize_t retss;

	if (len == 0) {
		error("len == 0\n");
		exit(EXIT_FAILURE);
	}

	reto = lseek(fd, 0, SEEK_END);
	if (reto == (off_t) -1) {
		error("lseek: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	retss = write(fd, &len, sizeof(len));
	if (retss == -1) {
		error("write: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}
	if (retss != sizeof(len)) {
		error("short write\n");
		exit(EXIT_FAILURE);
	}

	retss = write(fd, data, len);
	if (retss == -1) {
		error("write: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}
	if (retss != len) {
		error("short write\n");
		exit(EXIT_FAILURE);
	}

	if (len > len_max) {
		len_max = len;
		dstp->len_max = len_max;
	}

	dstp->n ++;
}

void diskstorage_seek(const int n, diskstorage_stat_t *dstp)
{
	int i;
	int fd = dstp->fd;
	int len;
	int len_max = dstp->len_max;
	ssize_t retss;
	off_t reto;

	reto = lseek(fd, 0, SEEK_SET);
	if (reto == (off_t) -1) {
		error("lseek: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	for (i = 0; i < n; i ++) {
		retss = read(fd, &len, sizeof(len));
		if (retss == -1) {
			error("read: %s\n", strerror(errno));
			exit(EXIT_FAILURE);
		}
		if (retss != sizeof(len)) {
			error("short read\n");
			exit(EXIT_FAILURE);
		}

		if (len > len_max) {
			error("len exceeds len_max\n");
			exit(EXIT_FAILURE);
		}

		reto = lseek(fd, len, SEEK_CUR);
		if (reto == -1) {
			error("lseek: %s\n", strerror(errno));
			exit(EXIT_FAILURE);
		}
	}
}

int diskstorage_read_next(void *data, int maxlen, diskstorage_stat_t *dstp)
{
	int fd = dstp->fd;
	int len;
	ssize_t retss;

	retss = read(fd, &len, sizeof(len));
	if (retss == -1) {
		error("read: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}
	if (retss != sizeof(len)) {
		error("short read\n");
		exit(EXIT_FAILURE);
	}

	if (len > maxlen) {
		error("len exceeds maxlen\n");
		exit(EXIT_FAILURE);
	}

	retss = read(fd, data, len);
	if (retss == -1) {
		error("read: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}
	if (retss != len) {
		error("short read\n");
		exit(EXIT_FAILURE);
	}

	return len;
}

int diskstorage_n(diskstorage_stat_t *dstp)
{
	return dstp->n;
}

int diskstorage_len_max(diskstorage_stat_t *dstp)
{
	return dstp->len_max;
}
