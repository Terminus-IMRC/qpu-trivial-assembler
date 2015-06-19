#include <stdio.h>
#include <string.h>
#include "qtc_aux.h"
#include "print_bin.h"

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