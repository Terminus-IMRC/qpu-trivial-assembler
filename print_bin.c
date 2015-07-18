#include <stdio.h>

void print_bin(unsigned int bin, int width, FILE *fp)
{
	unsigned int mask;

	if (width == 0)
		return;

	mask = (1 << (width - 1));

	do
		fputc(bin & mask ? '1' : '0', fp);
	while ((mask >>= 1));
}
