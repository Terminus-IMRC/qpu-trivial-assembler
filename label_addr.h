#ifndef _LABEL_ADDR_H_
#define _LABEL_ADDR_H_

	void label_addr_init();
	void label_addr_finalize();

	void label_addr_add_entry(const char *str, const int linenum);
	int label_addr_str_to_linenum(const char *str);

#endif /* _LABEL_ADDR_H_ */
