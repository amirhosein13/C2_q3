#include "botfriends.h"
#include <cassert>
#include <cstdio>
#include <vector>

int main() {
	int N, M;
	assert(2 == scanf("%d %d", &N, &M));
	std::vector<long long> A(N);
	for (int i = 0; i < N; i++)
		assert(1 == scanf("%lld", &A[i]));
	std::vector<int> U(M), V(M), W(M);
	for (int j = 0; j < M; j++)
		assert(3 == scanf("%d %d %d", &U[j], &V[j], &W[j]));
	fclose(stdin);

	long long result = min_cost(N, M, A, U, V, W);

	printf("%lld\n", result);
	fclose(stdout);
	return 0;
}
