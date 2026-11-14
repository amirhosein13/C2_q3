#include "botfriends.h"
#include <cassert>
#include <cstdio>
#include <vector>
// BEGIN SECRET
#include <string>
// END SECRET

int main() {
	// BEGIN SECRET
	const std::string output_secret = "t0Q7DJE3ZUUOPkegH41vFhj7WvbBJnJu";
	// END SECRET
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

	// BEGIN SECRET
	printf("%s\n", output_secret.c_str());
	printf("OK\n");
	// END SECRET
	printf("%lld\n", result);
	fclose(stdout);
	return 0;
}
