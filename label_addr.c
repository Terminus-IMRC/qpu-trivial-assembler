#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "error.h"

#define HASH_MAX 255

struct node_t {
	char *str;
	int linenum;
	struct node_t *next;
} *nodes[HASH_MAX];

static struct node_t* alloc_node();
static void free_node(struct node_t *p);
static void free_node_recursive(struct node_t *p);
static unsigned int calculate_hash(const char *str);

void label_addr_init()
{
	int i;
	static _Bool is_called = 0;

	if (is_called)
		return;
	is_called = !0;

	for (i = 0; i < HASH_MAX; i ++)
		nodes[i] = NULL;
}

void label_addr_finalize()
{
	int i;
	static _Bool is_called = 0;

	if (is_called)
		return;
	is_called = !0;

	for (i = 0; i < HASH_MAX; i ++)
		if (nodes[i] != NULL)
			free_node_recursive(nodes[i]);
}

void label_addr_add_entry(const char *str, const int linenum)
{
	unsigned int hash;
	struct node_t *p;

	if (str == NULL) {
		error("specified str is NULL\n");
		exit(EXIT_FAILURE);
	}

	p = nodes[hash = calculate_hash(str)];

	if (p == NULL) {
		p = nodes[hash] = alloc_node();
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
	unsigned int hash = calculate_hash(str);
	struct node_t *p = nodes[hash];

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
	free(p);
}

static void free_node_recursive(struct node_t *p)
{
	if (p->next != NULL)
		free_node_recursive(p->next);
	free_node(p);
}

static unsigned int calculate_hash(const char *str)
{
	unsigned int hash = 0;

	while (*str)
		hash += *str++;

	hash %= HASH_MAX;

	return hash;
}
