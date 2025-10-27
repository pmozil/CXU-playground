// The donut code with fixed-point arithmetic; no sines, cosines, square roots,
// or anything. a1k0n 2020 Code from:
// https://gist.github.com/a1k0n/80f48aa8911fffd805316b8ba8f48e83 For more info:
// - https://www.a1k0n.net/2011/07/20/donut-math.html
// - https://www.youtube.com/watch?v=DEqXNfs_HhY

#include "cfu.h"
#include "cxu_runtime.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <console.h>

//
// ACCELERATED VERSION
//
// using these two Custom Instructions
//    added via CFU (Custom Function Unit)
//
// #define mult_shift_10(a, b) ((int)cfu_op(0, 0, (a), (b)))
// #define cfu_mul(a, b) ((int)cfu_op(0, 0, (a), (b)))

int mult_shift_10(int a, int b) {
    cxu_csr_set_version_and_selector(1, 0);
    int res = cfu_op(0, 0, (a), (b));
    cxu_csr_clear();
}

int cfu_mul(int a, int b) {
    cxu_csr_set_version_and_selector(1, 1);
    int res = cfu_op(0, 0, (a), (b));
    cxu_csr_clear();
}


#define R(mul, shift, x, y)                                                    \
  _ = x;                                                                       \
  x -= cfu_mul(mul, y) >> shift;                                                \
  y += cfu_mul(mul, _) >> shift;                                                \
  _ = 3145728 - cfu_mul(x, x) - cfu_mul(y, y) >> 11;                             \
  x = cfu_mul(x, _) >> 10;                                                      \
  y = cfu_mul(y, _) >> 10;

static signed char b[1760], z[1760];

#ifdef OPT_LINK_CODE_IN_SRAM
void donut(void) __attribute__((section(".ramtext")));
#else
void donut(void);
#endif

void donut(void) {
  int sA = 1024, cA = 0, sB = 1024, cB = 0, _;
  puts("\nPress any key to exit.  Accelerated version.\n");
  for (;;) {
    memset(b, 32, 1760);  // text buffer
    memset(z, 127, 1760); // z buffer
    int sj = 0, cj = 1024;
    for (int j = 0; j < 90; j++) {
      int si = 0, ci = 1024; // sine and cosine of angle i
      for (int i = 0; i < 324; i++) {
        int R1 = 1, R2 = 2048, K2 = 5120 * 1024;

        int x0 = cfu_mul(R1, cj) + R2, x1 = mult_shift_10(ci, x0),
            x2 = mult_shift_10(cA, sj), x3 = mult_shift_10(si, x0),
            x4 = cfu_mul(R1, x2) - mult_shift_10(sA, x3), x5 = mult_shift_10(sA, sj),
            x6 = K2 + (cfu_mul(R1, x5) << 10) + cfu_mul(cA, x3),
            x7 = mult_shift_10(cj, si), x8 = cfu_mul(cB, x1) - cfu_mul(sB, x4),
            x = 40 + cfu_mul(30, x8) / x6, x9 = cfu_mul(cB, x4) + cfu_mul(sB, x1),
            y = 12 + cfu_mul(15, x9) / x6;
        int xx = mult_shift_10(cj, sB);
        int N = (-cfu_mul(cA, x7) - cB * ((-mult_shift_10(sA, x7)) + x2) -
                     cfu_mul(ci, xx) >>
                 10) -
                    x5 >>
                7;

        int o = x + cfu_mul(80, y);
        signed char zz = (x6 - K2) >> 15;
        if (22 > y && y > 0 && x > 0 && 80 > x && zz < z[o]) {
          z[o] = zz;
          b[o] = ".,-~:;=!*#$@"[N > 0 ? N : 0];
        }
        R(5, 8, ci, si) // rotate i
      }
      R(9, 7, cj, sj) // rotate j
    }
    for (int k = 0; 1761 > k; k++)
      putchar(k % 80 ? b[k] : 10);
    R(5, 7, cA, sA);
    R(5, 8, cB, sB);
    if (readchar_nonblock()) {
      getchar();
      break;
    }
    puts("\x1b[25A");
  }
}
