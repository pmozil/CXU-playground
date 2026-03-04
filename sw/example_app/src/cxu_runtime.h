#pragma once

#ifndef CXU_RUNTIME_H
#define CXU_RUNTIME_H

#include <stdint.h>

#define STATE_AND_INDEX_CSR 0xBC0

// CSR read/write macros
#define cxu_csr_read(csr)                                                          \
  ({                                                                           \
    uint32_t __val;                                                            \
    asm volatile("csrr %0, %1" : "=r"(__val) : "i"(csr));                      \
    __val;                                                                     \
  })

#define cxu_csr_write(csr, val)                                                    \
  ({ asm volatile("csrw %0, %1" ::"i"(csr), "r"(val)); })

/**
 * Set the CSR to zero
 */
static inline void cxu_csr_clear(void) { cxu_csr_write(STATE_AND_INDEX_CSR, 0); }

/**
 * Set the version and selector/index fields
 * @param selector: 32-bit value for mcx_selector
 */
static inline void cxu_csr_set_selector(uint32_t selector) {
  cxu_csr_write(STATE_AND_INDEX_CSR, selector);
}

/**
 * Set all 32 bits of the CSR to a custom value
 * @param value: 32-bit value to write
 */
static inline void cxu_csr_set_raw(uint32_t value) { cxu_csr_write(STATE_AND_INDEX_CSR, value); }

#define CXU_INDEX_BITS   16
#define CXU_INDEX_MASK   ((1u << CXU_INDEX_BITS) - 1)

static inline uint32_t cxu_pack_selector_index(uint32_t selector,
                                               uint32_t index)
{
    return (selector << CXU_INDEX_BITS) | (index & CXU_INDEX_MASK);
}

#define CXU_DATA_CSR 0xC00

static inline uint32_t cxu_state_read_word(uint32_t selector,
                                           uint32_t index)
{
    // Set selector + index
    cxu_csr_write(STATE_AND_INDEX_CSR,
                  cxu_pack_selector_index(selector, index));

    // Read data (auto increments internally)
    return cxu_csr_read(CXU_DATA_CSR);
}

static inline void cxu_state_write_word(uint32_t selector,
                                        uint32_t index,
                                        uint32_t value)
{
    // Set selector + index
    cxu_csr_write(STATE_AND_INDEX_CSR,
                  cxu_pack_selector_index(selector, index));

    // Write data (auto increments internally)
    cxu_csr_write(CXU_DATA_CSR, value);
}

static inline void cxu_state_read_block(uint32_t selector,
                                        uint32_t start_index,
                                        uint32_t *buffer,
                                        uint32_t words)
{
    cxu_csr_write(STATE_AND_INDEX_CSR,
                  cxu_pack_selector_index(selector, start_index));

    for (uint32_t i = 0; i < words; i++) {
        buffer[i] = cxu_csr_read(CXU_DATA_CSR);
    }
}

static inline void cxu_state_write_block(uint32_t selector,
                                         uint32_t start_index,
                                         const uint32_t *buffer,
                                         uint32_t words)
{
    cxu_csr_write(STATE_AND_INDEX_CSR,
                  cxu_pack_selector_index(selector, start_index));

    for (uint32_t i = 0; i < words; i++) {
        cxu_csr_write(CXU_DATA_CSR, buffer[i]);
    }
}


#endif
