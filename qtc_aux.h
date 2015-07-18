#ifndef _QTC_AUX_H_
#define _QTC_AUX_H_

#include <stdio.h>

	typedef enum {
		SIG_BREAK = 0,
		SIG_ALU = 1,
		SIG_TSW = 2,
		SIG_PEND = 3,
		SIG_WAITSB = 4,
		SIG_UNLOCKSB = 5,
		SIG_LTSW = 6,
		SIG_COVLD = 7,
		SIG_COLLD = 8,
		SIG_COLLD_PEND = 9,
		SIG_TMU0 = 10,
		SIG_TMU1 = 11,
		SIG_AMLD = 12,
		SIG_SIMM = 13,
		SIG_LI = 14,
		SIG_BRA = 15,
	} sig_t;

	typedef enum {
		/* bra also uses this as an empty bits */
		ESIG_BRA = 0x0,
		ESIG_LI32 = 0x0,
		ESIG_LIPES = 0x1,
		ESIG_LIPEU = 0x3,
	} esig_t;

	typedef struct {
		sig_t sig:4;

		unsigned int unpack:4;
		esig_t esig:4;

		unsigned int pm:1;

		unsigned int pack:4;
		unsigned int cond_br:4;

		unsigned int cond_add:3;
		unsigned int cond_mul:3;
		unsigned int sf:1;

		unsigned int rel:1;
		unsigned int reg:1;

		unsigned int ws:1;
		unsigned int waddr_add:6;
		unsigned int waddr_mul:6;

		unsigned int op_mul:3;
		unsigned int op_add:5;
		unsigned int raddr_a:6;
		unsigned int raddr_b:6;
		unsigned int add_a:3;
		unsigned int add_b:3;
		unsigned int mul_a:3;
		unsigned int mul_b:3;

		unsigned int imm:32;

		unsigned int pems:16;
		unsigned int pels:16;

		unsigned int sa:1;
		unsigned int semaphore:4;
	} inst_t;

	void reset_inst(inst_t *p);
	void output_inst(inst_t inst, FILE *fp);
	void output_inst_all(FILE *fp);

#endif /* _QTC_AUX_H_ */
