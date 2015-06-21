#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "qtc_aux.h"
#include "qtc_mem.h"
#include "print_bin.h"
#include "label_addr.h"

void reset_inst(inst_t *p)
{
	(void) memset(p, 0, sizeof(inst_t));
}

void output_inst(inst_t inst, FILE *fp)
{
	print_bin(inst.sig, 4, fp);
	fputc(' ', fp);
	switch (inst.sig) {
		case SIG_BREAK:
		case SIG_ALU:
		case SIG_TSW:
		case SIG_PEND:
		case SIG_WAITSB:
		case SIG_UNLOCKSB:
		case SIG_LTSW:
		case SIG_COVLD:
		case SIG_COLLD:
		case SIG_COLLD_PEND:
		case SIG_TMU0:
		case SIG_TMU1:
		case SIG_AMLD:
		case SIG_SIMM:
			print_bin(inst.unpack, 3, fp);
			fputc(' ', fp);
			print_bin(inst.pm, 1, fp);
			fputc(' ', fp);
			print_bin(inst.pack, 4, fp);
			fputc(' ', fp);
			print_bin(inst.cond_add, 3, fp);
			fputc(' ', fp);
			print_bin(inst.cond_mul, 3, fp);
			fputc(' ', fp);
			print_bin(inst.sf, 1, fp);
			fputc(' ', fp);
			print_bin(inst.ws, 1, fp);
			fputc(' ', fp);
			print_bin(inst.waddr_add, 6, fp);
			fputc(' ', fp);
			print_bin(inst.waddr_mul, 6, fp);
			fputc(' ', fp);
			print_bin(inst.op_mul, 3, fp);
			fputc(' ', fp);
			print_bin(inst.op_add, 5, fp);
			fputc(' ', fp);
			print_bin(inst.raddr_a, 6, fp);
			fputc(' ', fp);
			print_bin(inst.raddr_b, 6, fp);
			fputc(' ', fp);
			print_bin(inst.add_a, 3, fp);
			fputc(' ', fp);
			print_bin(inst.add_b, 3, fp);
			fputc(' ', fp);
			print_bin(inst.mul_a, 3, fp);
			fputc(' ', fp);
			print_bin(inst.mul_b, 3, fp);
			break;
		case SIG_BRA:
			print_bin(inst.esig, 4, fp);
			fputc(' ', fp);
			print_bin(inst.cond_br, 4, fp);
			fputc(' ', fp);
			print_bin(inst.rel, 1, fp);
			fputc(' ', fp);
			print_bin(inst.reg, 1, fp);
			fputc(' ', fp);
			print_bin(inst.raddr_a, 5, fp);
			fputc(' ', fp);
			print_bin(inst.ws, 1, fp);
			fputc(' ', fp);
			print_bin(inst.waddr_add, 6, fp);
			fputc(' ', fp);
			print_bin(inst.waddr_mul, 6, fp);
			fputc(' ', fp);
			print_bin(inst.imm, 32, fp);
			break;
		case SIG_LI:
			print_bin(inst.esig, 3, fp);
			fputc(' ', fp);
			print_bin(inst.pm, 1, fp);
			fputc(' ', fp);
			print_bin(inst.pack, 4, fp);
			fputc(' ', fp);
			print_bin(inst.cond_add, 3, fp);
			fputc(' ', fp);
			print_bin(inst.cond_mul, 3, fp);
			fputc(' ', fp);
			print_bin(inst.sf, 1, fp);
			fputc(' ', fp);
			print_bin(inst.ws, 1, fp);
			fputc(' ', fp);
			print_bin(inst.waddr_add, 6, fp);
			fputc(' ', fp);
			print_bin(inst.waddr_mul, 6, fp);
			fputc(' ', fp);
			switch (inst.esig) {
				case ESIG_LI32:
					print_bin(inst.imm, 32, fp);
					break;
				case ESIG_LIPES:
				case ESIG_LIPEU:
					print_bin(inst.imm >> 16, 16, fp);
					fputc(' ', fp);
					print_bin(inst.imm, 16, fp);
					break;
			}
			break;
	}
	fputc('\n', fp);
}

void output_inst_all(FILE *fp)
{
	int i;
	int n;

	n = qtc_mem_n();
	for (i = 0; i < n; i ++) {
		struct qtc_mem qm = qtc_mem_dequeue();
		if (qm.inst.sig == SIG_BRA) {
			qm.inst.imm = (int32_t)(label_addr_str_to_linenum(qm.str) - 4 - i) * (64 / 8);
			fprintf(fp, ";:%s\n", qm.str);
			free(qm.str);
		}
		output_inst(qm.inst, fp);
	}
}
