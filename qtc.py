#!/usr/bin/env python3

import sys
import re

out_lines=['']
labels={}
c=1

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
			if insproplen==2 or insproplen==3:
				op=insprop[1]
				if insproplen==3:
					cond=insprop[2]
				else:
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
			if opflag:
				outbin(condbin)
				outbin('000')
			else:
				outbin('000')
				outbin(condbin)
			outbin('1')

			#WARNING: write swap is not supported (yet)
			outbin('0')

			if opflag:
				outbin(addrAw_str_to_bin(tokens[1]))
				outbin('100111')
				outbin('000')
				outbin(opbin)
			else:
				outbin('100111')
				outbin(addrBw_str_to_bin(tokens[1]))
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
			if insproplen!=1:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction properties: %d\n'%(c, insproplen))
			if len(tokens)!=3:
				sys.exit(sys.argv[0]+': error: %d: invalid the number of the instruction tokens: %d'%(c, len(tokens)))
			if tokens[2][0]!='#':
				sys.exit(sys.argv[0]+': error: %d: argument #3 of li32 must be imm'%(c))

			outbin('1110 000')
			outbin('0')
			outbin('0000')
			outbin('000')
			outbin('000')
			outbin('0')
			outbin('0')

			outbin(addrAw_str_to_bin(tokens[1]))
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
	if id=='r0':
		return '100000'
	elif id=='r1':
		return '100001'
	elif id=='r2':
		return '100010'
	elif id=='r3':
		return '100011'
	elif id=='nop':
		return '100111'
	else:
		sys.exit(sys.argv[0]+': addrAw_str_to_bin: error: %d: unknown id: '%(c)+id)

def addrBw_str_to_bin(id):
	if id=='r0':
		return '100000'
	elif id=='r1':
		return '100001'
	elif id=='r2':
		return '100010'
	elif id=='r3':
		return '100011'
	elif id=='nop':
		return '100111'
	else:
		sys.exit(sys.argv[0]+': addrBw_str_to_bin: error: %d: unknown id: '%(c)+id)

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

if __name__=='__main__':
	mine()
