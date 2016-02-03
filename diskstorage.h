#ifndef _DISKSTORAGE_H_
#define _DISKSTORAGE_H_

	typedef struct {
		int fd;
		int len_max;
		int n;
	} diskstorage_stat_t;

	void diskstorage_init(diskstorage_stat_t *dstp);
	void diskstorage_finalize(diskstorage_stat_t *dstp);
	void diskstorage_append(void *data, int len, diskstorage_stat_t *dstp);
	void diskstorage_seek(const int n, diskstorage_stat_t *dstp);
	int diskstorage_read_next(void *data, int maxlen, diskstorage_stat_t *dstp);
	int diskstorage_n(diskstorage_stat_t *dstp);
	int diskstorage_len_max(diskstorage_stat_t *dstp);

	diskstorage_stat_t dst_inst, dst_inst_label, dst_label, dst_addr;

#endif /* _DISKSTORAGE_H_ */
