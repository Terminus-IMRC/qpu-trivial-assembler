#!/usr/bin/env python3

import sys

#Let's cooking!
def mine():
	c=0
	while True:
		try:
			s=input()
		except EOFError:
			break

		c+=1

		tokens=[i.strip() for i in s.split(',')]

		print(tokens)

		insprop=tokens[0].split('.')
		insproplen=len(insprop)

		insb=insprop[0]

		if insb=='alu':
			if insproplen==2 or insproplen==3:
				op=insprop[1]
				if insproplen==3:
					cond=insprop[2]
				else:
					cond='never'
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
			#set same cond for add and mul because they are executed exclusively for now
			outbin(condbin)
			outbin(condbin)
			#I cannot understand why this flag exists. 'never' can be used as cond
			outbin('1')

			#WARNING: write swap is not supported (yet)
			outbin('0')

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

			if opflag:
				outbin(addrAw_str_to_bin(tokens[1]))
				outbin('000000')
				outbin('000')
				outbin(opbin)
			else:
				outbin('000000')
				outbin(addrBw_str_to_bin(tokens[1]))
				outbin(opbin)
				outbin('00000')

			#WARNING: negative int and float immediate is not supported yet
			if tokens[2][0]=='#' and tokens[3][0]=='#':
				if int(tokens[2][1:])!=token[3][1:]:
					sys.exit(sys.argv[0]+': error: %d: different immediates are specified to alu'%(c))
			if tokens[2][0]=='#':
				outbin(imm_str_to_bin(tokens[2][1:]))
				outbin('100111')

				if opflag:
					outbin('110')
					outbin(mux_str_to_bin(tokens[3]))
					outbin('000')
					outbin('000')
				else:
					outbin('000')
					outbin('000')
					outbin('110')
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

		if insb=='li32':
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
			print("%032d"%(int(bin(n)[2:])))

		else:
			sys.exit(sys.argv[0]+': error: %d: invalid instruction name: '%(c)+insb)

		outbin(0, endflag=True)

def outbin(b, endflag=False):
	if endflag:
		print('')
	else:
		print(b, end=' ')

def addrAw_str_to_bin(id):
	if id=='r0':
		return '100000'
	elif id=='r1':
		return '100001'
	elif id=='r2':
		return '100010'
	elif id=='r3':
		return '100011'
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

if __name__=='__main__':
	mine()
