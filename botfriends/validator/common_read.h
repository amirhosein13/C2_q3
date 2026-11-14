// Shared reader for subtask validators (format is fully checked by validator.cpp).
#include "testlib.h"
#include <vector>
#include <algorithm>
using namespace std;

struct Input {
	int N, M;
	vector<long long> A;
	vector<int> U, V, W;
};

Input readInput() {
	Input in;
	in.N = inf.readInt(1, 200000, "N");
	inf.readSpace();
	in.M = inf.readInt(0, 500000, "M");
	inf.readEoln();
	in.A.resize(in.N);
	for (int i = 0; i < in.N; i++) {
		if (i) inf.readSpace();
		in.A[i] = inf.readLong(1LL, 1000000000000LL, "A_i");
	}
	inf.readEoln();
	in.U.resize(in.M); in.V.resize(in.M); in.W.resize(in.M);
	for (int j = 0; j < in.M; j++) {
		in.U[j] = inf.readInt(0, in.N - 1, "U_j");
		inf.readSpace();
		in.V[j] = inf.readInt(0, in.N - 1, "V_j");
		inf.readSpace();
		in.W[j] = inf.readInt(1, 1000000000, "W_j");
		inf.readEoln();
	}
	inf.readEof();
	return in;
}
