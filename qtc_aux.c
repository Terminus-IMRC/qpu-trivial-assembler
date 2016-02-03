#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "qtc_aux.h"
#include "print_bin.h"
#include "diskstorage.h"
#include "error.h"

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
	int n_inst, n_label;
	char *label_inst_label, *label_label;
	int len_max_inst_label, len_max_label;

	n_inst = diskstorage_n(&dst_inst);
	n_label = diskstorage_n(&dst_label);
	len_max_inst_label = diskstorage_len_max(&dst_inst_label);
	len_max_label = diskstorage_len_max(&dst_label);

	label_inst_label = malloc(len_max_inst_label + 1);
	if (label_inst_label == NULL) {
		error("failed to allocate label for inst_label\n");
		exit(EXIT_FAILURE);
	}
	label_label = malloc(len_max_label + 1);
	if (label_label == NULL) {
		error("failed to allocate label for label\n");
		exit(EXIT_FAILURE);
	}

	diskstorage_seek(0, &dst_inst);
	diskstorage_seek(0, &dst_inst_label);
	for (i = 0; i < n_inst; i ++) {
		inst_t inst;

		diskstorage_read_next(&inst, sizeof(inst), &dst_inst);
		if (inst.sig == SIG_BRA) {
			int j, sel = -1;
			int addr;
			int len_inst_label = diskstorage_read_next(label_inst_label, len_max_inst_label, &dst_inst_label);
			label_inst_label[len_inst_label] = '\0';
			diskstorage_seek(0, &dst_label);
			for (j = 0; j < n_label; j ++) {
				int len_label = diskstorage_read_next(label_label, len_max_label, &dst_label);
				label_label[len_label] = '\0';
				if ((len_inst_label == len_label) && (!memcmp(label_inst_label, label_label, len_inst_label))) {
					sel = j;
					break;
				}
			}
			if (sel == -1) {
				error("no such label: %s\n", label_inst_label);
			}
			diskstorage_seek(sel, &dst_addr);
			diskstorage_read_next(&addr, sizeof(addr), &dst_addr);

			inst.imm = (int32_t)(addr - 4 - i) * (64 / 8);
			fprintf(fp, ";:%s\n", label_inst_label);
		}
		output_inst(inst, fp);
	}

	free(label_label);
	free(label_inst_label);
}
