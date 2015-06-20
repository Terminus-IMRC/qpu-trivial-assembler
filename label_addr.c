#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "error.h"

struct node_t {
	char *str;
	int linenum;
	struct node_t *next;
} *node_orig;

static struct node_t* alloc_node();
static void free_node(struct node_t *p);
static void free_node_recursive(struct node_t *p);

void label_addr_init()
{
	static _Bool is_called = 0;

	if (is_called)
		return;
	is_called = !0;

	node_orig = NULL;
}

void label_addr_finalize()
{
	static _Bool is_called = 0;

	if (is_called)
		return;
	is_called = !0;

	if (node_orig != NULL)
		free_node_recursive(node_orig);
}

void label_addr_add_entry(const char *str, const int linenum)
{
	struct node_t *p;

	if (str == NULL) {
		error("specified str is NULL\n");
		exit(EXIT_FAILURE);
	}

	p = node_orig;

	if (p == NULL) {
		p = node_orig = alloc_node();
	} else {
		struct node_t *p_prev;
		do {
			if (!strcmp(str, p->str)) {
				error("duplicate label (was on line %d): %s\n", p->linenum, str);
				exit(EXIT_FAILURE);
			}
			p_prev = p;
		} while ((p = p->next) != NULL);
		p = p_prev->next = alloc_node();
	}

	p->str = strdup(str);
	if (p->str == NULL) {
		error("strdup: %s", strerror(errno));
		exit(EXIT_FAILURE);
	}
	p->linenum = linenum;
	p->next = NULL;
}

int label_addr_str_to_linenum(const char *str)
{
	struct node_t *p = node_orig;

	while (p != NULL) {
		if (!strcmp(str, p->str))
			return p->linenum;
		p = p->next;
	}

	error("label is not found: %s\n", str);
	exit(EXIT_FAILURE);
}

static struct node_t* alloc_node()
{
	struct node_t *p = malloc(sizeof(struct node_t));

	if (p == NULL) {
		error("failed to malloc struct node_t");
		exit(EXIT_FAILURE);
	}

	return p;
}

static void free_node(struct node_t *p)
{
	free(p->str);
	free(p);
}

static void free_node_recursive(struct node_t *p)
{
	if (p->next != NULL)
		free_node_recursive(p->next);
	free_node(p);
}
