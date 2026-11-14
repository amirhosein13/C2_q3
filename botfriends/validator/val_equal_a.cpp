// Subtask 1: all A[i] are equal.
#include "common_read.h"
int main() {
	registerValidation();
	Input in = readInput();
	for (int i = 1; i < in.N; i++)
		ensuref(in.A[i] == in.A[0], "A[%d] != A[0]", i);
	return 0;
}
