// Subtask 4: N <= 3000, M <= 6000.
#include "common_read.h"
int main() {
	registerValidation();
	Input in = readInput();
	ensuref(in.N <= 3000, "N=%d > 3000", in.N);
	ensuref(in.M <= 6000, "M=%d > 6000", in.M);
	return 0;
}
