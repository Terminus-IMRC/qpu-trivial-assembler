#ifndef _QTC_H_INCLUDED_
#define _QTC_H_INCLUDED_

#include <stdio.h>

	typedef enum {
		SIG_ALU = 1,
		SIG_PEND = 3,
		SIG_SIMM = 13,
		SIG_LI = 14,
		SIG_BRA = 15,
	} sig_t;

	typedef enum {
		/* bra also uses this as an empty bits */
		ESIG_BRA = 0x0,
		ESIG_LI32 = 0x0,
	} esig_t;

	typedef struct {
		sig_t sig:4;
		union {
			int unpack:4;
			esig_t esig:4;
		};
		int pm:1;
		union {
			int pack:4;
			int cond_br:4;
		};
		union {
			struct {
				int cond_add:3;
				int cond_mul:3;
				int sf:1;
			};
			struct {
				int rel:1;
				int reg:1;
			};
		};
		int ws:1;
		int waddr_add:6;
		int waddr_mul:6;
		/* This cannot be helped since both alu and bra have raddr_a at different bit offset */
		int raddr_a:6;
		union {
			struct {
				int op_mul:3;
				int op_add:5;
				int raddr_b:6;
				int add_a:3;
				int add_b:3;
				int mul_a:3;
				int mul_b:3;
			};
			int imm:32;
			struct {
				int pems:16;
				int pels:16;
			};
			struct {
				int sa:1;
				int semaphore:4;
			};
		};
	} inst_t;

	void reset_inst(inst_t *p);
	void output_inst(inst_t inst, FILE *fp);

#endif /* _QTC_H_INCLUDED_ */
