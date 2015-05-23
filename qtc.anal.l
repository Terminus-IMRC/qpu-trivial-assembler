%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <stdint.h>
#include "qtc.h"
#include "qtc_aux.h"
#include "strtol_ex.h"
#include "label_addr.h"

#define error(str, ...) fprintf(stderr, "%s:%d: %d: error: " str, __FILE__, __LINE__, linenum + 1, ## __VA_ARGS__)
#define error_sane(str, ...) fprintf(stderr, "%s:%d: error: " str, __FILE__, __LINE__, ## __VA_ARGS__)

typedef enum {
	REGTYPE1_AO = 0x1,
	REGTYPE1_BO = 0x2,
	REGTYPE1_AB = REGTYPE1_AO | REGTYPE1_BO
} regtype1_t;

typedef enum {
	REGTYPE2_RO = 0x1,
	REGTYPE2_WO = 0x2,
	REGTYPE2_RW = REGTYPE2_RO | REGTYPE2_WO
} regtype2_t;

typedef enum {
	REGTYPE3_REG,
	REGTYPE3_ACC
} regtype3_t;

typedef enum {
	MUX_ = -1,
	MUX_ACC0 = 0,
	MUX_ACC1 = 1,
	MUX_ACC2 = 2,
	MUX_ACC3 = 3,
	MUX_ACC4 = 4,
	MUX_ACC5 = 5,
	MUX_REGA = 6,
	MUX_REGB = 7
} mux_t;

static int linenum = 0, plinenum = 0;
static inst_t inst;
static int cstep = 0;
static _Bool is_touched = 0;
static _Bool is_to_inc_p = 0;
static _Bool is_cond_set = 0;
static _Bool must_be_sig_simm = 0;

static void end_of_line()
{
	if (is_touched) {
		if (!is_cond_set) {
			if (inst.sig == SIG_BRA) {
				error("any cond is specified to bra\n");
				exit(EXIT_FAILURE);
			} else {
				if (inst.op_mul)
					inst.cond_mul = 1;
				else
					inst.cond_add = 1;
			}
		}

		output_inst(inst, stdout);

		plinenum ++;
		reset_inst(&inst);
		cstep = 0;
		is_touched = 0;
		is_cond_set = 0;
		must_be_sig_simm = 0;
	} else if (is_to_inc_p)
		plinenum ++;
	is_to_inc_p = 0;
	linenum ++;
}

static void cond_set(int cond)
{
	if (!is_touched) {
		error("condition code is specified though instruction is not specified\n");
		exit(EXIT_FAILURE);
	} else if (cstep != 0) {
		error("condition code is not specified in first step in the line\n");
		exit(EXIT_FAILURE);
	} else if (is_cond_set) {
		error("condition code is specified more than once\n");
		exit(EXIT_FAILURE);
	}
	is_cond_set = !0;
	if (inst.op_mul)
		inst.cond_mul = cond;
	else
		inst.cond_add = cond;
}

static void bra_cond_set(int cond)
{
	if (!is_touched) {
		error("condition code is specified though instruction is not specified\n");
		exit(EXIT_FAILURE);
	} else if (cstep != 0) {
		error("condition code is not specified in first step in the line\n");
		exit(EXIT_FAILURE);
	} else if (is_cond_set) {
		error("condition code is specified more than once\n");
		exit(EXIT_FAILURE);
	}
	is_cond_set = !0;
	inst.cond_br = cond;
}

#define addr_set(reg, type1, type2, type3, mux) addr_set_backend(reg, REGTYPE1_##type1, REGTYPE2_##type2, REGTYPE3_##type3, mux)
#define small_immed_set(value) { \
	inst.sig = SIG_SIMM; \
	addr_set(((value)), BO, RO, REG, MUX_); \
}

static void addr_set_backend(int reg, regtype1_t type1, regtype2_t type2, regtype3_t type3, mux_t mux)
{
	if (inst.sig == SIG_BRA) {
		switch(cstep) {
			case 1: /* as a read register */
				if (type2 == REGTYPE2_WO) {
					error("write only register\n");
					exit(EXIT_FAILURE);
				} else if (type1 == REGTYPE1_BO) {
					error("register is file B only\n");
					exit(EXIT_FAILURE);
				} else if (type3 == REGTYPE3_ACC) {
					/* accumulators are passed with REGTYPE2_RW, but they are acutually RO on registers */
					error("an accumulator is passed to bra\n");
					exit(EXIT_FAILURE);
				} else if (reg >= 32) {
					/* TODO: is it right? */
					error("reg >= 32");
					exit(EXIT_FAILURE);
				}
				inst.reg = 1;
				inst.raddr_a = reg;
				break;
			case 2: /* as an add write register */
				if (type2 == REGTYPE2_RO) {
					error("read only register\n");
					exit(EXIT_FAILURE);
				} else if (type1 == REGTYPE1_BO) {
					/* so we do not support ws */
					error("register is file B only\n");
					exit(EXIT_FAILURE);
				}
				inst.waddr_add = reg;
				break;
			case 3: /* as a mul write register */
				if (type2 == REGTYPE2_RO) {
					error("read only register\n");
					exit(EXIT_FAILURE);
				} else if (type1 == REGTYPE1_AO) {
					/* so we do not support ws */
					error("register is file A only\n");
					exit(EXIT_FAILURE);
				}
				inst.waddr_mul = reg;
				break;
			default:
				error("too many registers for bra\n");
				exit(EXIT_FAILURE);
		}
	} else {
		switch (cstep) {
			case 1: /* as a write register */
				if (type2 == REGTYPE2_RO) {
					error("read only register\n");
					exit(EXIT_FAILURE);
				}
				if (inst.op_mul) {
					inst.ws = (type1 == REGTYPE1_AO ? 1 : 0);
					inst.waddr_mul = reg;
				} else {
					inst.ws = (type1 == REGTYPE1_BO ? 1 : 0);
					inst.waddr_add = reg;
				}
				break;
			case 2: /* as a reg A */
				if (inst.sig == SIG_LI) {
					error("load imm instructions do not take any read registers\n");
					exit(EXIT_FAILURE);
				} else if (type2 == REGTYPE2_WO) {
					error("write only register\n");
					exit(EXIT_FAILURE);
				} else if (type1 == REGTYPE1_BO) {
					error("register is file B only\n");
					exit(EXIT_FAILURE);
				}
				if (type3 == REGTYPE3_REG)
					inst.raddr_a = reg;
				if (inst.op_mul)
					inst.mul_a = (type3 == REGTYPE3_ACC ? mux : MUX_REGA);
				else
					inst.add_a = (type3 == REGTYPE3_ACC ? mux : MUX_REGA);
				break;
			case 3: /* as a reg B */
				if (inst.sig == SIG_LI) {
					error("load imm instructions do not take extra read registers\n");
					exit(EXIT_FAILURE);
				} else if (type2 == REGTYPE2_WO) {
					error("write only register\n");
					exit(EXIT_FAILURE);
				} else if (type1 == REGTYPE1_AO) {
					error("register is file A only\n");
					exit(EXIT_FAILURE);
				} else if (must_be_sig_simm && inst.sig != SIG_SIMM) {
					error("immediate must be specified since the third column is -\n");
					exit(EXIT_FAILURE);
				}
				if (type3 == REGTYPE3_REG)
					inst.raddr_b = reg;
				if (inst.op_mul)
					inst.mul_b = (type3 == REGTYPE3_ACC ? mux : MUX_REGB);
				else
					inst.add_b = (type3 == REGTYPE3_ACC ? mux : MUX_REGB);
				break;
		}
	}
}

void process_ambiguous_immed(char *s)
{
	long int num = strtol_ex(s + 1);

	if (!is_touched) {
		error("condition code is specified though instruction is not specified\n");
		exit(EXIT_FAILURE);
	}
	switch (inst.sig) {
		case SIG_ALU:
		case SIG_SIMM:
			if ((-16 > num) || (num > 15)) {
				error("small immediate out of range\n");
				exit(EXIT_FAILURE);
			}
			small_immed_set(num >= 0 ? num : 32 + num);
			break;
		case SIG_LI:
		case SIG_BRA:
			inst.imm = num;
			break;
		default:
			error("immediate is not supported in this sig\n");
			exit(EXIT_FAILURE);
	}
}

void extra_sig_set(const char *name, sig_t sig)
{
	name ++;

	if (!is_touched) {
		error("%s option is specified though instruction is not specified\n", name);
		exit(EXIT_FAILURE);
	} else if (cstep != 0) {
		error("%s option is not specified in the first step in the line\n", name);
		exit(EXIT_FAILURE);
	}

	inst.sig = sig;
}

void error_invalid_character(char c)
{
	error("extra character found: %c (%d)\n", c, c);
	exit(EXIT_FAILURE);
}
%}

%option noyywrap

%%

\n|\r|\r\n end_of_line();

^[ \t]*;.*$ puts(yytext);
^[ \t]*!.*$ {
	is_to_inc_p = !0;
	puts(yytext + 1);
}
[ \t]+ ;

alu {
	if (is_touched) {
		error("instruction is specified more than once\n");
		exit(EXIT_FAILURE);
	}
	is_touched = !0;
	inst.sig = SIG_ALU;
}

bra {
	if (is_touched) {
		error("instruction is specified more than once\n");
		exit(EXIT_FAILURE);
	}
	is_touched = !0;
	inst.sig = SIG_BRA;
	inst.esig = ESIG_BRA;
}

li32 {
	if (is_touched) {
		error("instruction is specified more than once\n");
		exit(EXIT_FAILURE);
	}
	is_touched = !0;
	inst.sig = SIG_LI;
	inst.esig = ESIG_LI32;
}

\.nop inst.op_add = 0;
\.fadd inst.op_add = 1;
\.fsub inst.op_add = 2;
\.fmin inst.op_add = 3;
\.fmax inst.op_add = 4;
\.fminabs inst.op_add = 5;
\.fmaxabs inst.op_add = 6;
\.ftoi inst.op_add = 7;
\.itof inst.op_add = 8;
\.add inst.op_add = 12;
\.sub inst.op_add = 13;
\.shr inst.op_add = 14;
\.asr inst.op_add = 15;
\.ror inst.op_add = 16;
\.shl inst.op_add = 17;
\.min inst.op_add = 18;
\.max inst.op_add = 19;
\.and inst.op_add = 20;
\.or inst.op_add = 21;
\.xor inst.op_add = 22;
\.not inst.op_add = 23;
\.clz inst.op_add = 24;
\.v8adds inst.op_add = 30;
\.v8subs inst.op_add = 31;

\.fmul inst.op_mul = 1;
\.mul24 inst.op_mul = 2;
\.v8muld inst.op_mul = 3;
\.v8min inst.op_mul = 4;
\.v8max inst.op_mul = 5;

\.never cond_set(0);
\.always {
	if (!is_touched) {
		error("condition code is specified though instruction is not specified\n");
		exit(EXIT_FAILURE);
	}
	if (inst.sig == SIG_BRA)
		bra_cond_set(15);
	else
		cond_set(1);
}
\.zs cond_set(2);
\.zc cond_set(3);
\.ns cond_set(4);
\.nc cond_set(5);
\.cs cond_set(6);
\.cc cond_set(7);

\.allzs bra_cond_set(0);
\.allzc bra_cond_set(1);
\.anyzs bra_cond_set(2);
\.anyzc bra_cond_set(3);
\.allns bra_cond_set(4);
\.allnc bra_cond_set(5);
\.anyns bra_cond_set(6);
\.anync bra_cond_set(7);
\.allcs bra_cond_set(8);
\.allcc bra_cond_set(9);
\.anycs bra_cond_set(10);
\.anycc bra_cond_set(11);

\.sf {
	if (inst.sig == SIG_BRA) {
		error("set flag option is specified to bra\n");
		exit(EXIT_FAILURE);
	}
	inst.sf = 1;
}

\.rel {
	if (inst.sig != SIG_BRA) {
		error("rel flag option is specified to non-bra\n");
		exit(EXIT_FAILURE);
	}
	inst.rel = 1;
}

\.break  extra_sig_set(yytext, SIG_BREAK);
\.thread_switch extra_sig_set(yytext, SIG_TSW);
\.program_end extra_sig_set(yytext, SIG_PEND);
\.waitsb extra_sig_set(yytext, SIG_WAITSB);
\.unlocksb extra_sig_set(yytext, SIG_UNLOCKSB);
\.last_thread_switch extra_sig_set(yytext, SIG_LTSW);
\.covload extra_sig_set(yytext, SIG_COVLD);
\.colload extra_sig_set(yytext, SIG_COLLD);
\.colload_and_program_end extra_sig_set(yytext, SIG_COLLD_PEND);
\.tmu0 extra_sig_set(yytext, SIG_TMU0);
\.tmu1 extra_sig_set(yytext, SIG_TMU1);
\.amload extra_sig_set(yytext, SIG_AMLD);

ra0 addr_set(0, AO, RW, REG, MUX_);
ra1 addr_set(1, AO, RW, REG, MUX_);
ra2 addr_set(2, AO, RW, REG, MUX_);
ra3 addr_set(3, AO, RW, REG, MUX_);
ra4 addr_set(4, AO, RW, REG, MUX_);
ra5 addr_set(5, AO, RW, REG, MUX_);
ra6 addr_set(6, AO, RW, REG, MUX_);
ra7 addr_set(7, AO, RW, REG, MUX_);
ra8 addr_set(8, AO, RW, REG, MUX_);
ra9 addr_set(9, AO, RW, REG, MUX_);
ra10 addr_set(10, AO, RW, REG, MUX_);
ra11 addr_set(11, AO, RW, REG, MUX_);
ra12 addr_set(12, AO, RW, REG, MUX_);
ra13 addr_set(13, AO, RW, REG, MUX_);
ra14 addr_set(14, AO, RW, REG, MUX_);
ra15 addr_set(15, AO, RW, REG, MUX_);
ra16 addr_set(16, AO, RW, REG, MUX_);
ra17 addr_set(17, AO, RW, REG, MUX_);
ra18 addr_set(18, AO, RW, REG, MUX_);
ra19 addr_set(19, AO, RW, REG, MUX_);
ra20 addr_set(20, AO, RW, REG, MUX_);
ra21 addr_set(21, AO, RW, REG, MUX_);
ra22 addr_set(22, AO, RW, REG, MUX_);
ra23 addr_set(23, AO, RW, REG, MUX_);
ra24 addr_set(24, AO, RW, REG, MUX_);
ra25 addr_set(25, AO, RW, REG, MUX_);
ra26 addr_set(26, AO, RW, REG, MUX_);
ra27 addr_set(27, AO, RW, REG, MUX_);
ra28 addr_set(28, AO, RW, REG, MUX_);
ra29 addr_set(29, AO, RW, REG, MUX_);
ra30 addr_set(30, AO, RW, REG, MUX_);
ra31 addr_set(31, AO, RW, REG, MUX_);

rb0 addr_set(0, BO, RW, REG, MUX_);
rb1 addr_set(1, BO, RW, REG, MUX_);
rb2 addr_set(2, BO, RW, REG, MUX_);
rb3 addr_set(3, BO, RW, REG, MUX_);
rb4 addr_set(4, BO, RW, REG, MUX_);
rb5 addr_set(5, BO, RW, REG, MUX_);
rb6 addr_set(6, BO, RW, REG, MUX_);
rb7 addr_set(7, BO, RW, REG, MUX_);
rb8 addr_set(8, BO, RW, REG, MUX_);
rb9 addr_set(9, BO, RW, REG, MUX_);
rb10 addr_set(10, BO, RW, REG, MUX_);
rb11 addr_set(11, BO, RW, REG, MUX_);
rb12 addr_set(12, BO, RW, REG, MUX_);
rb13 addr_set(13, BO, RW, REG, MUX_);
rb14 addr_set(14, BO, RW, REG, MUX_);
rb15 addr_set(15, BO, RW, REG, MUX_);
rb16 addr_set(16, BO, RW, REG, MUX_);
rb17 addr_set(17, BO, RW, REG, MUX_);
rb18 addr_set(18, BO, RW, REG, MUX_);
rb19 addr_set(19, BO, RW, REG, MUX_);
rb20 addr_set(20, BO, RW, REG, MUX_);
rb21 addr_set(21, BO, RW, REG, MUX_);
rb22 addr_set(22, BO, RW, REG, MUX_);
rb23 addr_set(23, BO, RW, REG, MUX_);
rb24 addr_set(24, BO, RW, REG, MUX_);
rb25 addr_set(25, BO, RW, REG, MUX_);
rb26 addr_set(26, BO, RW, REG, MUX_);
rb27 addr_set(27, BO, RW, REG, MUX_);
rb28 addr_set(28, BO, RW, REG, MUX_);
rb29 addr_set(29, BO, RW, REG, MUX_);
rb30 addr_set(30, BO, RW, REG, MUX_);
rb31 addr_set(31, BO, RW, REG, MUX_);

r0|acc0 addr_set(32, AB, RW, ACC, MUX_ACC0);
r1|acc1 addr_set(33, AB, RW, ACC, MUX_ACC1);
r2|acc2 addr_set(34, AB, RW, ACC, MUX_ACC2);
r3|acc3 addr_set(35, AB, RW, ACC, MUX_ACC3);
r4 addr_set(0, AB, RO, ACC, MUX_ACC4);
r5 addr_set(37, AB, RW, ACC, MUX_ACC5);
acc5a addr_set(37, AO, WO, REG, MUX_);
acc5b addr_set(37, BO, WO, REG, MUX_);

uniform_read addr_set(32, AB, RW, REG, MUX_);
varying_read addr_set(35, AB, RO, REG, MUX_);
tmu_noswap addr_set(36, AB, WO, REG, MUX_);
element_number addr_set(38, AO, RO, REG, MUX_);
qpu_number addr_set(38, BO, RO, REG, MUX_);
host_int addr_set(38, AB, WO, REG, MUX_);
nop addr_set(39, AB, RW, REG, MUX_);
uniforms_address addr_set(40, AB, WO, REG, MUX_);
x_pixel_coord addr_set(41, AO, RO, REG, MUX_);
y_pixel_coord addr_set(41, AB, RO, REG, MUX_);
quad_x addr_set(41, AO, WO, REG, MUX_);
quad_y addr_set(41, BO, WO, REG, MUX_);
ms_flags addr_set(42, AO, RW, REG, MUX_);
rev_flag addr_set(42, BO, RW, REG, MUX_);
tlb_stencil_setup addr_set(43, AB, WO, REG, MUX_);
tlb_z addr_set(44, AB, WO, REG, MUX_);
tlb_colour_ms addr_set(45, AB, WO, REG, MUX_);
tlb_colour_all addr_set(46, AB, WO, REG, MUX_);
tlb_alpha_mask addr_set(47, AB, WO, REG, MUX_);
vpm_read addr_set(48, AB, RO, REG, MUX_);
vpm_write addr_set(48, AB, WO, REG, MUX_);
vpm_ld_busy addr_set(49, AO, RO, REG, MUX_);
vpm_st_busy addr_set(49, BO, RO, REG, MUX_);
vpmvcd_rd_setup addr_set(49, AO, WO, REG, MUX_);
vpmvcd_wr_setup addr_set(49, BO, WO, REG, MUX_);
vpm_ld_wait addr_set(50, AO, RO, REG, MUX_);
vpm_st_wait addr_set(50, BO, RO, REG, MUX_);
vpm_ld_addr addr_set(50, AO, WO, REG, MUX_);
vpm_st_addr addr_set(50, BO, WO, REG, MUX_);
mutex_acquire addr_set(51, AB, RO, REG, MUX_);
mutex_release addr_set(51, AB, WO, REG, MUX_);
sfu_recip addr_set(52, AB, WO, REG, MUX_);
sfu_recipsqrt addr_set(53, AB, WO, REG, MUX_);
sfu_exp addr_set(54, AB, WO, REG, MUX_);
sfu_log addr_set(55, AB, WO, REG, MUX_);
tmu0_s addr_set(56, AB, WO, REG, MUX_);
tmu0_t addr_set(57, AB, WO, REG, MUX_);
tmu0_r addr_set(58, AB, WO, REG, MUX_);
tmu0_b addr_set(59, AB, WO, REG, MUX_);
tmu1_s addr_set(60, AB, WO, REG, MUX_);
tmu1_t addr_set(61, AB, WO, REG, MUX_);
tmu1_r addr_set(62, AB, WO, REG, MUX_);
tmu1_b addr_set(63, AB, WO, REG, MUX_);

#-{0,1}(0[box]){0,1}[0-9a-fA-F \t]+ process_ambiguous_immed(yytext);
#1\.0 small_immed_set(32);
#2\.0 small_immed_set(33);
#4\.0 small_immed_set(34);
#8\.0 small_immed_set(35);
#16\.0 small_immed_set(36);
#32\.0 small_immed_set(37);
#64\.0 small_immed_set(38);
#128\.0 small_immed_set(39);
#1(\.0){0,1}\/256(\.0){0,1} small_immed_set(40);
#1(\.0){0,1}\/128(\.0){0,1} small_immed_set(41);
#1(\.0){0,1}\/64(\.0){0,1} small_immed_set(42);
#1(\.0){0,1}\/32(\.0){0,1} small_immed_set(43);
#1(\.0){0,1}\/16(\.0){0,1} small_immed_set(44);
#1(\.0){0,1}\/8(\.0){0,1} small_immed_set(45);
#1(\.0){0,1}\/4(\.0){0,1} small_immed_set(46);
#1(\.0){0,1}\/2(\.0){0,1} small_immed_set(47);
#vrr5 small_immed_set(48);
#vr1 small_immed_set(49);
#vr2 small_immed_set(50);
#vr3 small_immed_set(51);
#vr4 small_immed_set(52);
#vr5 small_immed_set(53);
#vr6 small_immed_set(54);
#vr7 small_immed_set(55);
#vr8 small_immed_set(56);
#vr9 small_immed_set(57);
#vr10 small_immed_set(58);
#vr11 small_immed_set(59);
#vr12 small_immed_set(60);
#vr13 small_immed_set(61);
#vr14 small_immed_set(62);
#vr15 small_immed_set(63);

- {
	if ((inst.sig == SIG_ALU) && (cstep == 2)) {
		must_be_sig_simm = !0;
		if (inst.op_mul)
			inst.mul_a = MUX_REGB;
		else
			inst.add_a = MUX_REGB;
	} else
		error_invalid_character(*yytext);
}

:.+$ {
	switch (cstep) {
		case 0:
			label_addr_add_entry(yytext + 1, plinenum);
			break;
		case 4:
			if (inst.sig == SIG_BRA) {
				inst.rel = 1; /* set automatically! */
				inst.imm = (int32_t)(label_addr_str_to_linenum(yytext + 1) - 4 - plinenum) * (64 / 8);
				break;
			}
		default:
			error("unexpected label appearance\n");
			exit(EXIT_FAILURE);
	}
}

, {
	cstep ++;
}

. error_invalid_character(*yytext);

%%

void qtc_assemble_file(FILE *fp)
{
	YY_BUFFER_STATE state;

	label_addr_init();
	reset_inst(&inst);

	yyin = fp;
	state = yy_create_buffer(yyin, YY_BUF_SIZE);
	if (state == NULL) {
		error_sane("yy_create_buffer returned NULL\n");
		exit(EXIT_FAILURE);
	}
	yy_switch_to_buffer(state);
	yylex();
	yy_delete_buffer(state);

	label_addr_finalize();
}

void qtc_assemble_string(const char *str)
{
	YY_BUFFER_STATE state;

	label_addr_init();
	reset_inst(&inst);

	state = yy_scan_string(str);
	if (state == NULL) {
		error_sane("yy_scan_string returned NULL\n");
		exit(EXIT_FAILURE);
	}
	yylex();
	yy_delete_buffer(state);

	label_addr_finalize();
}
