// Subtask 3: N <= 400, M <= 1000.
#include "common_read.h"
int main() {
	registerValidation();
	Input in = readInput();
	ensuref(in.N <= 400, "N=%d > 400", in.N);
	ensuref(in.M <= 1000, "M=%d > 1000", in.M);
	return 0;
}
