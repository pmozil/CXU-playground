#include "cfu.h"

#include <console.h>
#include <stdio.h>
#include <string.h>

void cxu_demo(void);

void cxu_demo(void) {
  int res = (int)cfu_op(1, 1, 10, 1);

  char buf[100];

  snprintf(buf, 100, "%d\n", res);

  puts(buf);
}
