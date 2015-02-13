%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <stdint.h>
#include "qtc.h"
#include "strtol_ex.h"
#include "error.h"

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
static _Bool is_cond_set = 0;

static void end_of_line()
{
	linenum ++;

	if (is_touched) {
		if (!is_cond_set) {
			if (inst.op_mul)
				inst.cond_mul = 1;
			else
				inst.cond_add = 1;
		}

		output_inst(inst, stdout);

		plinenum ++;
		reset_inst(&inst);
		cstep = 0;
		is_touched = 0;
		is_cond_set = 0;
	}
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

#define addr_set(reg, type1, type2, type3, mux) addr_set_backend(reg, REGTYPE1_##type1, REGTYPE2_##type2, REGTYPE3_##type3, mux)
#define small_immed_set(value) { \
	inst.sig = SIG_SIMM; \
	addr_set(((value)), BO, RO, REG, MUX_); \
}

static void addr_set_backend(int reg, regtype1_t type1, regtype2_t type2, regtype3_t type3, mux_t mux)
{
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
			} else if (inst.sig == SIG_BRA) {
				error("register additions for branch instruction is not supported (yet)\n");
				exit(EXIT_FAILURE);
			} else if (type2 == REGTYPE2_WO) {
				error("write only register\n");
				exit(EXIT_FAILURE);
			} else if (type1 == REGTYPE1_BO) {
				error("register is file B only\n");
				exit(EXIT_FAILURE);
			}
			inst.raddr_a = reg;
			if (inst.op_mul)
				inst.mul_a = (type3 == REGTYPE3_ACC ? mux : MUX_REGA);
			else
				inst.add_a = (type3 == REGTYPE3_ACC ? mux : MUX_REGA);
			break;
		case 3: /* as a reg B */
			if ((inst.sig == SIG_BRA) || (inst.sig == SIG_LI)) {
				error("load imm instructions and branch instruction do not take extra read registers\n");
				exit(EXIT_FAILURE);
			} else if (type2 == REGTYPE2_WO) {
				error("write only register\n");
				exit(EXIT_FAILURE);
			} else if (type1 == REGTYPE1_AO) {
				error("register is file A only\n");
				exit(EXIT_FAILURE);
			}
			inst.raddr_b = reg;
			if (inst.op_mul)
				inst.mul_b = (type3 == REGTYPE3_ACC ? mux : MUX_REGB);
			else
				inst.add_b = (type3 == REGTYPE3_ACC ? mux : MUX_REGB);
			break;
	}
}

void process_ambiguous_immed(char *s)
{
	long int num = strtol_ex(s);

	if (!is_touched) {
		error("condition code is specified though instruction is not specified\n");
		exit(EXIT_FAILURE);
	}
	switch (inst.sig) {
		case SIG_ALU:
		case SIG_SIMM:
			if ((-16 > num) && (num > 15)) {
				error("small immediate out of range\n");
				exit(EXIT_FAILURE);
			}
			small_immed_set(num >= 0 ? num : 32 + num);
			break;
		case SIG_LI:
		case SIG_BRA:
			inst.imm = num;
			break;
	}
}
%}

%option noyywrap

%%

\n|\r|\r\n end_of_line();

^;.*$ puts(yytext);
^!.*$ puts(yytext);
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
\.always cond_set(1);
\.zs cond_set(2);
\.zc cond_set(3);
\.ns cond_set(4);
\.nc cond_set(5);
\.cs cond_set(6);
\.cc cond_set(7);

\.sf inst.sf = 1;

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

r0|ACC0 addr_set(32, AB, RW, ACC, MUX_ACC0);
r1|ACC1 addr_set(33, AB, RW, ACC, MUX_ACC1);
r2|ACC2 addr_set(34, AB, RW, ACC, MUX_ACC2);
r3|ACC3 addr_set(35, AB, RW, ACC, MUX_ACC3);
r5 addr_set(37, AB, RW, ACC, MUX_ACC5);
ACC5A addr_set(37, AO, WO, REG, MUX_);
ACC5B addr_set(37, BO, WO, REG, MUX_);

UNIFORM_READ addr_set(32, AB, RW, REG, MUX_);
VARYING_READ addr_set(35, AB, RO, REG, MUX_);
TMU_NOSWAP addr_set(36, AB, WO, REG, MUX_);
ELEMENT_NUMBER addr_set(38, AO, RO, REG, MUX_);
QPU_NUMBER addr_set(38, BO, RO, REG, MUX_);
HOST_INT addr_set(38, AB, WO, REG, MUX_);
UNIFORMS_ADDRESS addr_set(40, AB, WO, REG, MUX_);
X_PIXEL_COORD addr_set(41, AO, RO, REG, MUX_);
Y_PIXEL_COORD addr_set(41, AB, RO, REG, MUX_);
QUAD_X addr_set(41, AO, WO, REG, MUX_);
QUAD_Y addr_set(41, BO, WO, REG, MUX_);
MS_FLAGS addr_set(42, AO, RW, REG, MUX_);
REV_FLAG addr_set(42, BO, RW, REG, MUX_);
TLB_STENCIL_SETUP addr_set(43, AB, WO, REG, MUX_);
TLB_Z addr_set(44, AB, WO, REG, MUX_);
TLB_COLOUR_MS addr_set(45, AB, WO, REG, MUX_);
TLB_COLOUR_ALL addr_set(46, AB, WO, REG, MUX_);
TLB_ALPHA_MASK addr_set(47, AB, WO, REG, MUX_);
VPM_READ addr_set(48, AB, RO, REG, MUX_);
VPM_WRITE addr_set(48, AB, WO, REG, MUX_);
VPM_LD_BUSY addr_set(49, AO, RO, REG, MUX_);
VPM_ST_BUSY addr_set(49, BO, RO, REG, MUX_);
VPM_RD_SETUP addr_set(49, AO, WO, REG, MUX_);
VPM_WR_SETUP addr_set(49, BO, WO, REG, MUX_);
VPM_LD_WAIT addr_set(50, AO, RO, REG, MUX_);
VPM_ST_WAIT addr_set(50, BO, RO, REG, MUX_);
VPM_LD_ADDR addr_set(50, AO, WO, REG, MUX_);
VPM_ST_ADDR addr_set(50, BO, WO, REG, MUX_);
MUTEX_ACQUIRE addr_set(51, AB, RO, REG, MUX_);
MUTEX_RELEASE addr_set(51, AB, WO, REG, MUX_);
SFU_RECIP addr_set(52, AB, WO, REG, MUX_);
SFU_RECIPSQRT addr_set(53, AB, WO, REG, MUX_);
SFU_EXP addr_set(54, AB, WO, REG, MUX_);
SFU_LOG addr_set(55, AB, WO, REG, MUX_);
TMU0_S addr_set(56, AB, WO, REG, MUX_);
TMU0_T addr_set(57, AB, WO, REG, MUX_);
TMU0_R addr_set(58, AB, WO, REG, MUX_);
TMU0_B addr_set(59, AB, WO, REG, MUX_);
TMU1_S addr_set(60, AB, WO, REG, MUX_);
TMU1_T addr_set(61, AB, WO, REG, MUX_);
TMU1_R addr_set(62, AB, WO, REG, MUX_);
TMU1_B addr_set(63, AB, WO, REG, MUX_);

#-{0,1}(0[box]){0,1}[0-9a-fA-F]+ process_ambiguous_immed(yytext);
#1\.0 small_immed_set(32);
#2\.0 small_immed_set(33);
#4\.0 small_immed_set(34);
#8\.0 small_immed_set(35);
#16\.0 small_immed_set(36);
#32\.0 small_immed_set(37);
#64\.0 small_immed_set(38);
#128\.0 small_immed_set(39);
#1(\.0){0,1}/256(\.0){0,1} small_immed_set(40);
#1(\.0){0,1}/128(\.0){0,1} small_immed_set(41);
#1(\.0){0,1}/64(\.0){0,1} small_immed_set(42);
#1(\.0){0,1}/32(\.0){0,1} small_immed_set(43);
#1(\.0){0,1}/16(\.0){0,1} small_immed_set(44);
#1(\.0){0,1}/8(\.0){0,1} small_immed_set(45);
#1(\.0){0,1}/4(\.0){0,1} small_immed_set(46);
#1(\.0){0,1}/2(\.0){0,1} small_immed_set(47);
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

, {
	cstep ++;
}

. {
	error("extra character found: %c (%d)\n", *yytext, *yytext);
	exit(EXIT_FAILURE);
}

%%

int main()
{
	FILE *yyin = stdin;

	reset_inst(&inst);

	yylex();

	return 0;
}
