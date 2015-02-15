#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>
#include <errno.h>
#include "error.h"

long int strtol_ex(const char *nptr)
{
	int i, base = 0;
	char *str;
	long int num;

	str = malloc(strlen(nptr) * sizeof(char));
	if (str == NULL) {
		error("failed to malloc str\n");
		exit(EXIT_FAILURE);
	}

	i = 0;
	do {
		if ((!isdigit(*nptr)) && (!isxdigit(*nptr)) && (!isspace(*nptr)) && *nptr != 'x' && *nptr != '-' && *nptr != '\0') {
			error("invalid character: %c (%d)\n", *nptr, *nptr);
			free(str);
			exit(EXIT_FAILURE);
		}
		if(!isspace(*nptr))
			str[i ++] = *nptr;
	} while (*nptr++);
	str[i] = '\0';

	if (!strncmp(str, "0b", 2)) {
		base = 2;
		i = 2;
	} else
		i= 0;

	errno = 0;
	num = strtoul(str + i, NULL, base);

	if ((errno == ERANGE && (num == LONG_MAX || num == LONG_MIN)) || (errno != 0 && num == 0)) {
		error("strtoul: %s\n", strerror(errno));
		free(str);
		exit(EXIT_FAILURE);
	}

	free(str);

	return num;
}
