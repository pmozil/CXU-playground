#include "cfu.h"
#include "cxu_runtime.h"

#include <console.h>
#include <stdio.h>
#include <string.h>

#define CXU_SELECTOR 1
#define STATE_INDEX  3

void cxu_state_demo(void)
{
    char buf[128];

    // -------------------------------------------------
    // 1. Initialize state index
    // -------------------------------------------------

    cxu_state_write_word(CXU_SELECTOR, STATE_INDEX, 100);

    uint32_t before = cxu_state_read_word(CXU_SELECTOR, STATE_INDEX);

    snprintf(buf, sizeof(buf), "State before: %u\n", before);
    puts(buf);

    // -------------------------------------------------
    // 2. Trigger CXU instruction
    //    (This will add 10 to selected state index)
    // -------------------------------------------------

    int res = (int)cfu_op(0, 0, 0, 0);

    snprintf(buf, sizeof(buf), "CXU returned: %d\n", res);
    puts(buf);

    // -------------------------------------------------
    // 3. Read updated state
    // -------------------------------------------------

    uint32_t after = cxu_state_read_word(CXU_SELECTOR, STATE_INDEX);

    snprintf(buf, sizeof(buf), "State after: %u\n", after);
    puts(buf);
}
