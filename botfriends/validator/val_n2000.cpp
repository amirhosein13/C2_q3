// Subtask 4: N <= 2000, M <= 4000.
#include "common_read.h"
int main() {
	registerValidation();
	Input in = readInput();
	ensuref(in.N <= 2000, "N=%d > 2000", in.N);
	ensuref(in.M <= 4000, "M=%d > 4000", in.M);
	return 0;
}
