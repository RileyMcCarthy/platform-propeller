#define P2_TARGET_MHZ 200

#include <propeller.h>
#include <sys/p2es_clock.h>
#include <stdio.h>

extern int *    lowerCanary;
uint8_t lib_utility_CRC8(uint8_t *addr, uint16_t len);

int main() {
#if PROPELLER_FRAMEWORK == P2LLVM
    _clkset(_SETFREQ, _CLOCKFREQ);
    _uart_init(DBG_UART_RX_PIN, DBG_UART_TX_PIN, 230400, 0);
#endif
    printf("Hello World!\n");
    printf("CRC8 of 'Hello': 0x%02X\n", lib_utility_CRC8((uint8_t *)lowerCanary, 32));
    while(1) {
        _waitx(CLKFREQ);
        printf("Time1: %u\n", _getms());
    }
}
