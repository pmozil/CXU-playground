#pragma once

#ifndef CXU_RUNTIME_H
#define CXU_RUNTIME_H

#include <stdint.h>

#define STATE_AND_INDEX_CSR 0xBC0

#define MCX_VERSION_BIT 29
#define MCX_VERSION_MASK (0x7 << MCX_VERSION_BIT)
#define MCX_SELECTOR_BIT 0
#define MCX_SELECTOR_MASK 0xFF

// CSR read/write macros
#define csr_read(csr)                                                          \
  ({                                                                           \
    uint32_t __val;                                                            \
    asm volatile("csrr %0, %1" : "=r"(__val) : "i"(csr));                      \
    __val;                                                                     \
  })

#define csr_write(csr, val)                                                    \
  ({ asm volatile("csrw %0, %1" ::"i"(csr), "r"(val)); })

/**
 * Set the CSR to zero
 */
static inline void cxu_csr_clear(void) { csr_write(STATE_AND_INDEX_CSR, 0); }

/**
 * Set the version and selector/index fields
 * @param version: 3-bit value (0-7) for mcx_version
 * @param selector: 8-bit value (0-255) for mcx_selector
 */
static inline void cxu_csr_set_version_and_selector(uint8_t version, uint8_t selector) {
  uint32_t val = csr_read(STATE_AND_INDEX_CSR);

  val &= ~(MCX_VERSION_MASK | MCX_SELECTOR_MASK);

  val |= ((version & 0x7) << MCX_VERSION_BIT) | (selector & 0xFF);

  csr_write(STATE_AND_INDEX_CSR, val);
}

/**
 * Set all 32 bits of the CSR to a custom value
 * @param value: 32-bit value to write
 */
static inline void cxu_csr_set_raw(uint32_t value) { csr_write(STATE_AND_INDEX_CSR, value); }

#endif
