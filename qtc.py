#!/usr/bin/env python3

import sys
import re

out_lines=['']
labels={}
c=1

addrAw={
	'r0':'100000',
	'r1':'100001',
	'r2':'100010',
	'r3':'100011',
	'nop':'100111',

	'ACC0':'100000',
	'ACC1':'100001',
	'ACC2':'100010',
	'ACC3':'100011',
	'HOST_INT':'100110',
	'NOP':'100111',
	'UNIFORMS_ADDRESS':'101000',
	'VPM_WRITE':'110000',
	'VPMVCD_RD_SETUP':'110001',
	'VPM_LD_ADDR':'110010'
}

addrBw={
	'r0':'100000',
	'r1':'100001',
	'r2':'100010',
	'r3':'100011',
	'nop':'100111',

	'ACC0':'100000',
	'ACC1':'100001',
	'ACC2':'100010',
	'ACC3':'100011',
	'HOST_INT':'100110',
	'NOP':'100111',
	'UNIFORMS_ADDRESS':'101000',
	'VPM_WRITE':'110000',
	'VPMVCD_WR_SETUP':'110001',
	'VPM_ST_ADDR':'110010'
}

addrAr={
	'nop':'100111',

	'UNIFORM_READ':'100000',
	'ELEMENT_NUMBER':'100110',
	'NOP':'100111',
	'VPM_READ':'110000',
	'VPM_LD_BUSY':'110001',
	'VPM_LD_WAIT':'110010'
}

addrBr={
	'nop':'100111',

	'UNIFORM_READ':'100000',
	'QPU_NUMBER':'100110',
	'NOP':'100111',
	'VPM_READ':'110000',
	'VPM_ST_BUSY':'110001',
	'VPM_ST_WAIT':'110010'
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

			opflag=None #True for add and False for mul
			if op=='nop':
				opbin='00000'
				opflag=True
			elif op=='add':
				opbin='01100'
				opflag=True
			elif op=='sub':
				opbin='01101'
				opflag=True
			elif op=='min':
				opbin='10010'
				opflag=True
			elif op=='max':
				opbin='10011'
				opflag=True
			elif op=='and':
				opbin='10100'
				opflag=True
			elif op=='or':
				opbin='10101'
				opflag=True
			elif op=='xor':
				opbin='01110'
				opflag=True
			elif op=='not':
				opbin='10111'
				opflag=True
			elif op=='clz':
				opbin='11000'
				opflag=True
			elif op=='mul24':
				opbin='010'
				opflag=False
			else:
				sys.exit(sys.argv[0]+': error: %d: invalid alu op name: '%(c)+op)

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

			#WARNING: negative int and float immediate is not supported yet
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
				outbin('100111')
				outbin(imm_str_to_bin(tokens[2][1:]))

				if opflag:
					outbin('111')
					outbin(mux_str_to_bin(tokens[3]))
					outbin('000')
					outbin('000')
				else:
					outbin('000')
					outbin('000')
					outbin('111')
					outbin(mux_str_to_bin(tokens[3]))
			elif tokens[3][0]=='#':
				outbin('100111')
				outbin(imm_str_to_bin(tokens[3][1:]))

				if opflag:
					outbin(mux_str_to_bin(tokens[2]))
					outbin('111')
					outbin('000')
					outbin('000')
				else:
					outbin('000')
					outbin('000')
					outbin(mux_str_to_bin(tokens[2]))
					outbin('111')
			else:
				outbin('100111')
				outbin('100111')
				if opflag:
					outbin(mux_str_to_bin(tokens[2]))
					outbin(mux_str_to_bin(tokens[3]))
					outbin('000')
					outbin('000')
				else:
					outbin('000')
					outbin('000')
					outbin(mux_str_to_bin(tokens[2]))
					outbin(mux_str_to_bin(tokens[3]))

		elif insb=='li32':
			if insproplen!=1 and insproplen!=2 and insproplen!=3:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction properties: %d\n'%(c, insproplen))
			else:
				if insproplen==1:
					sf=False
					cond='never'
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

			n=int(tokens[2][1:])
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

def imm_str_to_bin(id):
	n=int(id)
	if not(n>=0 and n<=17):
		sys.exit(sys.argv[0]+': imm_str_to_bin: error: %d: invalid the range of the number: '%(c)+id)
	return "%06d"%(int(bin(n)[2:]))

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

def locate_w_register(id):
	try:
		addrAw[id]
	except KeyError:
		try:
			addrBw[id]
		except KeyError:
			sys.exit(sys.argv[0]+': locate_w_register: error: unknown id: '+id)
		else:
			return 1 #indicates Bw
	else:
		return 0 #indicates Aw

def locate_r_register(id):
	try:
		addrAr[id]
	except KeyError:
		try:
			addrBr[id]
		except KeyError:
			sys.exit(sys.argv[0]+': locate_r_register: error: unknown id: '+id)
		else:
			return 1 #indicates Br
	else:
		return 0 #indicates Ar

if __name__=='__main__':
	mine()
