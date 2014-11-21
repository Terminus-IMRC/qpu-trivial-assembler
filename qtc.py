#!/usr/bin/env python3

import sys
import re
import math

out_lines=['']
labels={}
c=1

addrAw={
	'r0':'100000',
	'r1':'100001',
	'r2':'100010',
	'r3':'100011',
	'nop':'100111',

	'ra0':'000000',
	'ra1':'000001',
	'ra2':'000010',
	'ra3':'000011',
	'ra4':'000100',
	'ra5':'000101',
	'ra6':'000110',
	'ra7':'000111',
	'ra8':'001000',
	'ra9':'001001',
	'ra10':'001010',
	'ra11':'001011',
	'ra12':'001100',
	'ra13':'001101',
	'ra14':'001110',
	'ra15':'001111',
	'ra16':'010000',
	'ra17':'010001',
	'ra18':'010010',
	'ra19':'010011',
	'ra20':'010100',
	'ra21':'010101',
	'ra22':'010110',
	'ra23':'010111',
	'ra24':'011000',
	'ra25':'011001',
	'ra26':'011010',
	'ra27':'011011',
	'ra28':'011100',
	'ra29':'011101',
	'ra30':'011110',
	'ra31':'011111',
	'ACC0':'100000',
	'ACC1':'100001',
	'ACC2':'100010',
	'ACC3':'100011',
	'HOST_INT':'100110',
	'NOP':'100111',
	'UNIFORMS_ADDRESS':'101000',
	'VPM_WRITE':'110000',
	'VPMVCD_RD_SETUP':'110001',
	'VPM_LD_ADDR':'110010',
	'SFU_RECIP':'110100',
	'SFU_RECIPSQRT':'110101',
	'SFU_EXP':'110110',
	'SFU_LOG':'110111'
}

addrBw={
	'r0':'100000',
	'r1':'100001',
	'r2':'100010',
	'r3':'100011',
	'nop':'100111',

	'rb0':'000000',
	'rb1':'000001',
	'rb2':'000010',
	'rb3':'000011',
	'rb4':'000100',
	'rb5':'000101',
	'rb6':'000110',
	'rb7':'000111',
	'rb8':'001000',
	'rb9':'001001',
	'rb10':'001010',
	'rb11':'001011',
	'rb12':'001100',
	'rb13':'001101',
	'rb14':'001110',
	'rb15':'001111',
	'rb16':'010000',
	'rb17':'010001',
	'rb18':'010010',
	'rb19':'010011',
	'rb20':'010100',
	'rb21':'010101',
	'rb22':'010110',
	'rb23':'010111',
	'rb24':'011000',
	'rb25':'011001',
	'rb26':'011010',
	'rb27':'011011',
	'rb28':'011100',
	'rb29':'011101',
	'rb30':'011110',
	'rb31':'011111',
	'ACC0':'100000',
	'ACC1':'100001',
	'ACC2':'100010',
	'ACC3':'100011',
	'HOST_INT':'100110',
	'NOP':'100111',
	'UNIFORMS_ADDRESS':'101000',
	'VPM_WRITE':'110000',
	'VPMVCD_WR_SETUP':'110001',
	'VPM_ST_ADDR':'110010',
	'SFU_RECIP':'110100',
	'SFU_RECIPSQRT':'110101',
	'SFU_EXP':'110110',
	'SFU_LOG':'110111'
}

addrAr={
	'nop':'100111',

	'ra0':'000000',
	'ra1':'000001',
	'ra2':'000010',
	'ra3':'000011',
	'ra4':'000100',
	'ra5':'000101',
	'ra6':'000110',
	'ra7':'000111',
	'ra8':'001000',
	'ra9':'001001',
	'ra10':'001010',
	'ra11':'001011',
	'ra12':'001100',
	'ra13':'001101',
	'ra14':'001110',
	'ra15':'001111',
	'ra16':'010000',
	'ra17':'010001',
	'ra18':'010010',
	'ra19':'010011',
	'ra20':'010100',
	'ra21':'010101',
	'ra22':'010110',
	'ra23':'010111',
	'ra24':'011000',
	'ra25':'011001',
	'ra26':'011010',
	'ra27':'011011',
	'ra28':'011100',
	'ra29':'011101',
	'ra30':'011110',
	'ra31':'011111',
	'UNIFORM_READ':'100000',
	'ELEMENT_NUMBER':'100110',
	'NOP':'100111',
	'VPM_READ':'110000',
	'VPM_LD_BUSY':'110001',
	'VPM_LD_WAIT':'110010'
}

addrBr={
	'nop':'100111',

	'rb0':'000000',
	'rb1':'000001',
	'rb2':'000010',
	'rb3':'000011',
	'rb4':'000100',
	'rb5':'000101',
	'rb6':'000110',
	'rb7':'000111',
	'rb8':'001000',
	'rb9':'001001',
	'rb10':'001010',
	'rb11':'001011',
	'rb12':'001100',
	'rb13':'001101',
	'rb14':'001110',
	'rb15':'001111',
	'rb16':'010000',
	'rb17':'010001',
	'rb18':'010010',
	'rb19':'010011',
	'rb20':'010100',
	'rb21':'010101',
	'rb22':'010110',
	'rb23':'010111',
	'rb24':'011000',
	'rb25':'011001',
	'rb26':'011010',
	'rb27':'011011',
	'rb28':'011100',
	'rb29':'011101',
	'rb30':'011110',
	'rb31':'011111',
	'UNIFORM_READ':'100000',
	'QPU_NUMBER':'100110',
	'NOP':'100111',
	'VPM_READ':'110000',
	'VPM_ST_BUSY':'110001',
	'VPM_ST_WAIT':'110010'
}

opAdd={
	'nop':'00000',
	'fadd':'00001',
	'fsub':'00010',
	'fmin':'00011',
	'fmax':'00100',
	'fminabs':'00101',
	'fmaxabs':'00110',
	'ftoi':'00111',
	'itof':'01000',
	'add':'01100',
	'sub':'01101',
	'shr':'01110',
	'asr':'01111',
	'ror':'10000',
	'shl':'10001',
	'min':'10010',
	'max':'10011',
	'and':'10100',
	'or':'10101',
	'xor':'01110',
	'not':'10111',
	'clz':'11000',
	'v8adds':'11110',
	'v8subs':'11111'
}

opMul={
	'nop':'000',
	'fmul':'001',
	'mul24':'010',
	'v8muld':'011',
	'v8min':'100',
	'v8max':'101',
	'v8adds':'110',
	'v8subs':'111'
}

#Let's cooking!
def mine():
	global labels, c

	while True:
		try:
			s=input()
		except EOFError:
			break

		tokens=[i.strip() for i in s.split(',')]

		if len(tokens)==1 and len(tokens[0])==0:
			continue

		insprop=tokens[0].split('.')
		insproplen=len(insprop)

		insb=insprop[0]

		if insb[0]=='!':
			outbin(insprop[0][1:])
		elif insb[0]==';':
			outbin(s)
			outbin(0, endflag=True)
			continue
		elif insb=='alu':
			if insproplen==2 or insproplen==3 or insproplen==4:
				op=insprop[1]
				if insproplen==3:
					if insprop[2]=='sf':
						sf=True
						cond='always'
					else:
						sf=False
						cond=insprop[2]
				elif insproplen==4:
					sf=True
					if insprop[2]=='sf':
						cond=insprop[3]
					else:
						cond=insprop[2]
				else:
					sf=False
					cond='always'
			else:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction properties: %d'%(c, insproplen))

			if len(tokens)!=4:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction tokens: %d'%(c, len(tokens)))

			if tokens[2][0]=='#' or tokens[3][0]=='#':
				#uses immediate
				outbin('1101')
			else:
				#normal alu
				outbin('0001')

			#packing/unpacking is not supported (yet)
			outbin('000')
			outbin('0')
			outbin('0000')

			(opbin, opflag)=detect_op(op)

			condbin=alucond_str_to_bin(cond)

			if opflag:
				outbin(condbin)
				outbin('000')
			else:
				outbin('000')
				outbin(condbin)

			if sf:
				outbin('1')
			else:
				outbin('0')

			w_location=locate_w_register(tokens[1])
			if w_location==2:
				w_location=0
			if opflag and w_location==0:
				ws=False
			elif opflag and w_location==1:
				ws=True
			elif (not opflag) and w_location==0:
				ws=True
			elif (not opflag) and w_location==1:
				ws=False
			else:
				sys.exit(sys.argv[0]+': error: %d: w_location may be invalid: %d'%(c, w_location))

			if not ws:
				outbin('0')
			else:
				outbin('1')

			if opflag:
				if not ws:
					outbin(addrAw_str_to_bin(tokens[1]))
				else:
					outbin(addrBw_str_to_bin(tokens[1]))
				outbin('100111')
				outbin('000')
				outbin(opbin)
			else:
				outbin('100111')
				if not ws:
					outbin(addrBw_str_to_bin(tokens[1]))
				else:
					outbin(addrAw_str_to_bin(tokens[1]))
				outbin(opbin)
				outbin('00000')

			#WARNING: float immediate is not supported yet
			if tokens[2][0]=='#' and tokens[3][0]=='#':
				if int(tokens[2][1:])!=int(tokens[3][1:]):
					sys.exit(sys.argv[0]+': error: %d: different immediates are specified to alu'%(c))

				outbin('100111')
				outbin(imm_str_to_bin(tokens[2][1:]))

				if opflag:
					outbin('111')
					outbin('111')
					outbin('000')
					outbin('000')
				else:
					outbin('000')
					outbin('000')
					outbin('111')
					outbin('111')
			elif tokens[2][0]=='#':
				if re.match('^r[0-5]$', tokens[3])!=None:
					use_mux=True
				else:
					use_mux=False
					r_location=locate_r_register(tokens[3])
					if r_location==2:
						r_location=0
					if r_location!=0 and r_location!=1:
						sys.exit(sys.argv[0]+': error: %d: r_location may be invalid: %d'%(c, r_location))

				if use_mux:
					outbin('100111')
				else:
					if r_location==0:
						outbin(addrAr_str_to_bin(tokens[3]))
					else:
						outbin(addrBr_str_to_bin(tokens[3]))
				outbin(imm_str_to_bin(tokens[2][1:]))

				if opflag:
					if use_mux:
						outbin(mux_str_to_bin(tokens[3]))
						outbin('111')
					else:
						if r_location==0:
							outbin('110')
							outbin('111')
						else:
							outbin('111')
							outbin('110')
					outbin('000')
					outbin('000')
				else:
					outbin('000')
					outbin('000')
					if use_mux:
						outbin(mux_str_to_bin(tokens[3]))
						outbin('111')
					else:
						if r_location==0:
							outbin('110')
							outbin('111')
						else:
							outbin('111')
							outbin('110')
			elif tokens[3][0]=='#':
				if re.match('^r[0-5]$', tokens[2])!=None:
					use_mux=True
				else:
					use_mux=False
					r_location=locate_r_register(tokens[2])
					if r_location==2:
						r_location=0
					if r_location!=0 and r_location!=1:
						sys.exit(sys.argv[0]+': error: %d: r_location may be invalid: %d'%(c, r_location))

				if use_mux:
					outbin('100111')
				else:
					if r_location==0:
						outbin(addrAr_str_to_bin(tokens[2]))
					else:
						outbin(addrBr_str_to_bin(tokens[2]))
				outbin(imm_str_to_bin(tokens[3][1:]))

				if opflag:
					if use_mux:
						outbin(mux_str_to_bin(tokens[2]))
						outbin('111')
					else:
						if r_location==0:
							outbin('110')
							outbin('111')
						else:
							outbin('111')
							outbin('110')
					outbin('000')
					outbin('000')
				else:
					outbin('000')
					outbin('000')
					if use_mux:
						outbin(mux_str_to_bin(tokens[2]))
						outbin('111')
					else:
						if r_location==0:
							outbin('110')
							outbin('111')
						else:
							outbin('111')
							outbin('110')
			else:
				if re.match('^r[0-5]$', tokens[2])!=None:
					use_mux_2=True
				else:
					use_mux_2=False
					r_location_2=locate_r_register(tokens[2])
					if r_location_2!=0 and r_location_2!=1 and r_location_2!=2:
						sys.exit(sys.argv[0]+': error: %d: r_location_2 may be invalid: %d'%(c, r_location_2))
				if re.match('^r[0-5]$', tokens[3])!=None:
					use_mux_3=True
				else:
					use_mux_3=False
					r_location_3=locate_r_register(tokens[3])
					if r_location_3!=0 and r_location_3!=1 and r_location_3!=2:
						sys.exit(sys.argv[0]+': error: %d: r_location_3 may be invalid: %d'%(c, r_location_3))

				if (not use_mux_2) and (not use_mux_3):
					if r_location_2==2 and r_location_3==2:
						r_location_2=0
						r_location_3=1
					elif r_location_2==2 and r_location_3!=2:
						r_location_2=1-r_location_3
					elif r_location_2!=2 and r_location_3==2:
						r_location_3=1-r_location_2

					if r_location_2==r_location_3:
						sys.exit(sys.argv[0]+': error: %d: attempting to read from the same register file space(A or B)'%(c))

				if use_mux_2:
					outbin('100111')
				else:
					if r_location_2==0:
						outbin(addrAr_str_to_bin(tokens[2]))
					else:
						outbin(addrBr_str_to_bin(tokens[2]))
				if use_mux_3:
					outbin('100111')
				else:
					if r_location_3==0:
						outbin(addrAr_str_to_bin(tokens[3]))
					else:
						outbin(addrBr_str_to_bin(tokens[3]))

				if opflag:
					if use_mux_2 and use_mux_3:
						outbin(mux_str_to_bin(tokens[2]))
						outbin(mux_str_to_bin(tokens[3]))
					elif use_mux_2 and (not use_mux_3):
						if r_location_3==0:
							outbin('111')
							outbin(mux_str_to_bin(tokens[2]))
						else:
							outbin(mux_str_to_bin(tokens[2]))
							outbin('111')
					elif (not use_mux_2) and use_mux_3:
						if r_location_2==0:
							outbin('110')
							outbin(mux_str_to_bin(tokens[3]))
						else:
							outbin(mux_str_to_bin(tokens[3]))
							outbin('110')
					else:
						if r_location_2==0:
							outbin('110')
							outbin('111')
						else:
							outbin('111')
							outbin('110')
					outbin('000')
					outbin('000')
				else:
					outbin('000')
					outbin('000')
					if use_mux_2 and use_mux_3:
						outbin(mux_str_to_bin(tokens[2]))
						outbin(mux_str_to_bin(tokens[3]))
					elif use_mux_2 and (not use_mux_3):
						if r_location_3==0:
							outbin('111')
							outbin(mux_str_to_bin(tokens[2]))
						else:
							outbin(mux_str_to_bin(tokens[2]))
							outbin('111')
					elif (not use_mux_2) and use_mux_3:
						if r_location_2==0:
							outbin('110')
							outbin(mux_str_to_bin(tokens[3]))
						else:
							outbin(mux_str_to_bin(tokens[3]))
							outbin('110')
					else:
						if r_location_2==0:
							outbin('110')
							outbin('111')
						else:
							outbin('111')
							outbin('110')

		elif insb=='li32':
			if insproplen!=1 and insproplen!=2 and insproplen!=3:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction properties: %d\n'%(c, insproplen))
			else:
				if insproplen==1:
					sf=False
					cond='always'
				elif insproplen==2:
					if insprop[1]=='sf':
						sf=True
						cond='always'
					else:
						sf=False
						cond=insprop[1]
				else:
					sf=True
					if insprop[1]=='sf':
						cond=insprop[2]
					else:
						cond=insprop[1]
			if len(tokens)!=3:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction tokens: %d'%(c, len(tokens)))
			if tokens[2][0]!='#':
				sys.exit(sys.argv[0]+': error: %d: argument #3 of li32 must be imm'%(c))

			outbin('1110 000')
			outbin('0')
			outbin('0000')
			condbin=alucond_str_to_bin(cond)
			outbin(condbin)
			outbin('000')
			if sf:
				outbin('1')
			else:
				outbin('0')

			w_location=locate_w_register(tokens[1])
			if w_location==2:
				w_location=0
			if w_location==0:
				ws=False
			elif w_location==1:
				ws=True
			else:
				sys.exit(sys.argv[0]+': error: %d: w_location may be invalid: %d'%(c, w_location))

			if not ws:
				outbin('0')
				outbin(addrAw_str_to_bin(tokens[1]))
			else:
				outbin('1')
				outbin(addrBw_str_to_bin(tokens[1]))

			outbin('100111')

			n=int(tokens[2][1:], 0)
			n=complement_num_32(n)
			outbin("%032d"%(int(bin(n)[2:])))

		elif insb=='lbl':
			if insproplen!=1:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction properties: %d\n'%(c, insproplen))
			if len(tokens)!=2:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction tokens: %d'%(c, len(tokens)))

			labels[tokens[1]]=c

			continue

		elif insb=='brr':
			if insproplen!=2:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction properties: %d\n'%(c, insproplen))
			cond=insprop[1]
			if len(tokens)!=2:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction tokens: %d'%(c, len(tokens)))

			outbin('1111')
			#I do not know with what to fill here
			outbin('0000')

			if cond=='allzs':
				condbin='0000'
			elif cond=='allzc':
				condbin='0001'
			elif cond=='anyzs':
				condbin='0010'
			elif cond=='anyzc':
				condbin='0011'
			elif cond=='allns':
				condbin='0100'
			elif cond=='allnc':
				condbin='0101'
			elif cond=='anyns':
				condbin='0110'
			elif cond=='anync':
				condbin='0111'
			elif cond=='allcs':
				condbin='1000'
			elif cond=='allcc':
				condbin='1001'
			elif cond=='anycs':
				condbin='1010'
			elif cond=='anycc':
				condbin='1011'
			elif cond=='always':
				condbin='1111'
			else:
				sys.exit(sys.argv[0]+': error: %d: unknown branch condition: %s'%(c, cond))
			outbin(condbin)
			outbin('1')
			outbin('0')
			#What is this address? Where to find the information...
			outbin('00000')
			outbin('0')
			outbin('100111')
			outbin('100111')

			outbin(tokens[1])

		elif insb=='program_end':
			if insproplen!=1:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction properties: %d\n'%(c, insproplen))
			if len(tokens)!=1:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction tokens: %d'%(c, len(tokens)))

			outbin('0011')
			outbin('000')
			outbin('0')
			outbin('0000')
			outbin('000')
			outbin('000')
			outbin('0')
			outbin('0')
			outbin('100111')
			outbin('100111')
			outbin('000')
			outbin('00000')
			outbin('100111')
			outbin('100111')
			outbin('110')
			outbin('110')
			outbin('111')
			outbin('111')

		else:
			sys.exit(sys.argv[0]+': error: %d: invalid instruction name: '%(c)+insb)

		outbin(0, endflag=True)
		c+=1
	outbin(0, finishflag=True)

def outbin(b, endflag=False, finishflag=False):
	global out_lines, labels

	if finishflag:
		for i in labels.items():
			for j in range(len(out_lines)):
				out_lines[j]=re.sub(' '+re.escape(i[0])+' ', ' '+re.escape(int_to_32binstr(8*(-4+(i[1]-(j+1)))))+' ', out_lines[j])
		for i in range(len(out_lines)-1):
			print(out_lines[i])
	elif endflag:
		out_lines.append('')
	else:
		out_lines[len(out_lines)-1]+=b+' '

def addrAw_str_to_bin(id):
	try:
		addr=addrAw[id]
	except KeyError:
		sys.exit(sys.argv[0]+': addrAw_str_to_bin: error: %d: unknown id: '%(c)+id)

	return addr

def addrBw_str_to_bin(id):
	try:
		addr=addrBw[id]
	except KeyError:
		sys.exit(sys.argv[0]+': addrBw_str_to_bin: error: %d: unknown id: '%(c)+id)
	
	return addr

def addrAr_str_to_bin(id):
	try:
		addr=addrAr[id]
	except KeyError:
		sys.exit(sys.argv[0]+': addrAr_str_to_bin: error: %d: unknown id: '%(c)+id)
	
	return addr

def addrBr_str_to_bin(id):
	try:
		addr=addrBr[id]
	except KeyError:
		sys.exit(sys.argv[0]+': addrBr_str_to_bin: error: %d: unknown id: '%(c)+id)
	
	return addr

def imm_str_to_bin(id):
	if re.match('^[0-9][0-9]*$', id)!=None or re.match('^-[0-9][0-9]*$', id)!=None:
		n=int(id)
		if not(n>=-16 and n<=15):
			sys.exit(sys.argv[0]+': imm_str_to_bin: error: %d: invalid the range of the number: '%(c)+id)
		s=int_to_6binstr(n)
		return s
	elif re.match('^[0-9][0-9]*\.0$', id)!=None:
		tn=re.sub('\.0$', '', id)
		if re.search('[^0-9]', tn)!=None:
			sys.exit(sys.argv[0]+': imm_str_to_bin: error: %d: invalid the format of the float number: '%(c)+id)
		tnn=int(tn)
		if not (tnn>=1 and tnn<=128):
			sys.exit(sys.argv[0]+': imm_str_to_bin: error: %d: invalid the range of the float number: '%(c)+id)
		elif log2(tnn)!=math.floor(log2(tnn)):
			sys.exit(sys.argv[0]+': imm_str_to_bin: error: %d: specified float number is not the factorial of 2: '%(c)+id)

		n=32+int(log2(tnn))
		return "%06d"%(int(bin(n)[2:]))
	else:
		sys.exit(sys.argv[0]+': imm_str_to_bin: error: %d: invalid the format of small immediate: '%(c)+id)

def mux_str_to_bin(id):
	if id=='r0':
		return '000'
	elif id=='r1':
		return '001'
	elif id=='r2':
		return '010'
	elif id=='r3':
		return '011'
	elif id=='r4':
		return '100'
	elif id=='r5':
		return '101'
	else:
		sys.exit(sys.argv[0]+': mux_str_to_bin: error: %d: unknown id: '%(c)+id)

def alucond_str_to_bin(cond):
	if cond=='never':
		condbin='000'
	elif cond=='always':
		condbin='001'
	elif cond=='zs':
		condbin='010'
	elif cond=='zc':
		condbin='011'
	elif cond=='ns':
		condbin='100'
	elif cond=='nc':
		condbin='101'
	elif cond=='cs':
		condbin='110'
	elif cond=='cc':
		condbin='111'
	else:
		sys.exit(sys.argv[0]+': cond_str_to_bin: error: unknown id: '+cond)

	return condbin

def int_to_32binstr(n):
	if n<0:
		s=bin(complement_num_32(n))[3:]
	else:
		s=bin(n)[2:]
	b="%032d"%(int(s))
	if n<0:
		b='1'+b[1:]
	else:
		b='0'+b[1:]

	return b

def complement_num_32(n):
	if n<0:
		n=-n
		n-=1
		s="%032d"%(int(bin(n)[2:]))
		for i in range(32):
			if s[i]=='0':
				s=s[:i]+'1'+s[i+1:]
			else:
				s=s[:i]+'0'+s[i+1:]
		return int(s, 2)
	else:
		return n

def int_to_6binstr(n):
	if n<0:
		s=bin(complement_num_6(n))[3:]
	else:
		s=bin(n)[2:]
	b="%06d"%(int(s))
	if n<0:
		b='1'+b[1:]
	else:
		b='0'+b[1:]

	return b

def complement_num_6(n):
	if n<0:
		n=-n
		n-=1
		s="%06d"%(int(bin(n)[2:]))
		for i in range(6):
			if s[i]=='0':
				s=s[:i]+'1'+s[i+1:]
			else:
				s=s[:i]+'0'+s[i+1:]
		return int(s, 2)
	else:
		return n

def locate_w_register(id):
	res=0
	except_on_A=False

	try:
		addrAw[id]
	except KeyError:
		except_on_A=True
	else:
		res+=1

	try:
		addrBw[id]
	except KeyError:
		if except_on_A:
			sys.exit(sys.argv[0]+': locate_w_register: error: unknown id: '+id)
	else:
		res+=2

	res-=1
	return res #0=Aw, 1=Bw, 2=both

def locate_r_register(id):
	res=0
	except_on_A=False

	try:
		addrAr[id]
	except KeyError:
		except_on_A=True
	else:
		res+=1

	try:
		addrBr[id]
	except KeyError:
		if except_on_A:
			sys.exit(sys.argv[0]+': locate_r_register: error: unknown id: '+id)
	else:
		res+=2

	res-=1
	return res #0=Ar, 1=Br, 2=both

def detect_op(id):
	#opflag is True for add and False for mul

	try:
		opAdd[id]
	except KeyError:
		pass
	else:
		return (opAdd[id], True)

	try:
		opMul[id]
	except KeyError:
		sys.exit(sys.argv[0]+': detect_op: error: invalid alu op name: '+id)
	else:
		return (opMul[id], False)

def log2(n):
	return math.log(n)/math.log(2)

if __name__=='__main__':
	mine()
