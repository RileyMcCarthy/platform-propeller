#include <stdio.h>

// Simple implementation that doesn't use floating point printf
int main() {
   // Temporary minimal program while stdio is pared down
   volatile int x = 42;
   printf("Hello, World! x = %d\n", x);
   return x == 42 ? 0 : 1;
}
