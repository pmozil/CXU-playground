#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <uart.h>
#include <console.h>
#include <generated/csr.h>

static char read_key(void)
{
    if(readchar_nonblock()) {
        return readchar();
    }
    return 0;
}

static void prompt(void)
{
    printf("Press any key (or 'q' to quit)...\n");
}

static void help(void)
{
    puts("Hello World App");
    puts("Press any key to print 'Hello World'");
    puts("Press 'q' to quit");
}

int main(void)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
    irq_setmask(0);
    irq_setie(1);
#endif
    uart_init();

    puts("\nHello World App - Built "__DATE__" "__TIME__"\n");
    help();
    prompt();

    while(1) {
        char key = read_key();
        if(key) {
            if(key == 'q' || key == 'Q') {
                printf("\nExiting...\n");
                break;
            }
            printf("Hello World! (Pressed: %c)\n", key);
            prompt();
        }
    }

    return 0;
}
