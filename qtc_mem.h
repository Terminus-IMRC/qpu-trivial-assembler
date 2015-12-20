#ifndef _QTC_MEM_H
#define _QTC_MEM_H

#include <stdint.h>
#include "qtc_aux.h"

	struct qtc_mem {
		inst_t inst;
		char *str;
	};

	void qtc_mem_init();
	void qtc_mem_finalize();
	void qtc_mem_inqueue(const inst_t inst, const char *str);
	void qtc_mem_dequeue_init();
	void qtc_mem_dequeue_finalize();
	struct qtc_mem qtc_mem_dequeue();
	int qtc_mem_n();

#endif /* _QTC_MEM_H */
