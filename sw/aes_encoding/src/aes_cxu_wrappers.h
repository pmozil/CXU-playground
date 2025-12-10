#ifndef AES_CXU_WRAPPERS_H
#define AES_CXU_WRAPPERS_H

#include <stdint.h>

#ifdef USE_CXU
#include "cfu.h"
#include "cxu_runtime.h"
#endif

static inline uint32_t pack4_u8(uint8_t b0, uint8_t b1, uint8_t b2, uint8_t b3) {
  return ((uint32_t)b0) | ((uint32_t)b1 << 8) | ((uint32_t)b2 << 16) | ((uint32_t)b3 << 24);
}

static inline void unpack4_u8(uint32_t v, uint8_t *b0, uint8_t *b1, uint8_t *b2, uint8_t *b3) {
  *b0 = (uint8_t)(v & 0xFF);
  *b1 = (uint8_t)((v >> 8) & 0xFF);
  *b2 = (uint8_t)((v >> 16) & 0xFF);
  *b3 = (uint8_t)((v >> 24) & 0xFF);
}

static inline uint8_t gf8_mul_sw(uint8_t a, uint8_t b) {
  uint8_t p = 0;
  for (int i = 0; i < 8; ++i) {
    if (b & 1) p ^= a;
    uint8_t hi = a & 0x80;
    a <<= 1;
    if (hi) a ^= 0x1B;
    b >>= 1;
  }
  return p;
}

static inline uint32_t gf8_mul_vec_sw(uint32_t a4, uint32_t b4) {
  uint8_t a0 = a4 & 0xFF, a1 = (a4 >> 8) & 0xFF, a2 = (a4 >> 16) & 0xFF, a3 = (a4 >> 24) & 0xFF;
  uint8_t b0 = b4 & 0xFF, b1 = (b4 >> 8) & 0xFF, b2 = (b4 >> 16) & 0xFF, b3 = (b4 >> 24) & 0xFF;
  uint32_t r0 = gf8_mul_sw(a0,b0);
  uint32_t r1 = gf8_mul_sw(a1,b1);
  uint32_t r2 = gf8_mul_sw(a2,b2);
  uint32_t r3 = gf8_mul_sw(a3,b3);
  return (r3<<24) | (r2<<16) | (r1<<8) | r0;
}

#ifdef USE_CXU

static inline void gf8_mul_ext_begin() {
  cxu_csr_set_version_and_selector(1, 0);
}

static inline uint8_t gf8_mul(uint8_t a, uint8_t b) {
  int res = cfu_op(0, 0, (int)a, (int)b);
  return (uint8_t)res;
}

static inline void gf8_mul_vec_ext_begin() {
  cxu_csr_set_version_and_selector(1, 1);
}

static inline uint32_t gf8_mul_vec(uint32_t a4, uint32_t b4) {
  int res = cfu_op(0, 0, (int)a4, (int)b4);
  return (uint32_t)res;
}

#else

static inline void gf8_mul_ext_begin() {
}

static inline uint8_t gf8_mul(uint8_t a, uint8_t b) {
  (void)a; (void)b;
  return gf8_mul_sw(a, b);
}

static inline void gf8_mul_vec_ext_begin() {
}

static inline uint32_t gf8_mul_vec(uint32_t a4, uint32_t b4) {
  (void)a4; (void)b4;
  return gf8_mul_vec_sw(a4, b4);
}

#endif

#endif // AES_CXU_WRAPPERS_H
