// -*- coding: utf-8 -*-
// Header file generated automatically by cslug.
// Do not modify this file directly as your changes will be overwritten.

#ifndef QUEUE_H
#define QUEUE_H

#include "_queue.h"

// queue.c
void Q_append(Queue *queue, ptrdiff_t arg);
ptrdiff_t Q_consume(Queue *queue);
ptrdiff_t Q_consume_later(Queue *queue);
ptrdiff_t Q_contains(Queue *queue, ptrdiff_t arg);
ptrdiff_t Q_is_empty(Queue *queue);
void Q_appends(Queue * queue, ptrdiff_t * args, ptrdiff_t len_args);
void Q_add(Queue * queue, ptrdiff_t arg);
ptrdiff_t Q_len(Queue * queue);

#endif
