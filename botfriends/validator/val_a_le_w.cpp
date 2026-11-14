// Subtask 2: max(A) <= min(W).
#include "common_read.h"
int main() {
	registerValidation();
	Input in = readInput();
	long long maxA = *max_element(in.A.begin(), in.A.end());
	for (int j = 0; j < in.M; j++)
		ensuref(maxA <= in.W[j], "max(A)=%lld > W[%d]=%d", maxA, j, in.W[j]);
	return 0;
}
