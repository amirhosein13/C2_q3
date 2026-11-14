// Global validator: format and constraints of the full problem.
#include "testlib.h"
#include <vector>
using namespace std;

const int MAXN = 200000;
const int MAXM = 500000;
const long long MAXA = 1000000000000LL;
const int MAXW = 1000000000;

vector<int> par;
int root(int x) {
	while (par[x] != x) x = par[x] = par[par[x]];
	return x;
}

int main() {
	registerValidation();
	int N = inf.readInt(1, MAXN, "N");
	inf.readSpace();
	int M = inf.readInt(N - 1, MAXM, "M");
	inf.readEoln();
	for (int i = 0; i < N; i++) {
		if (i) inf.readSpace();
		inf.readLong(1LL, MAXA, "A_i");
	}
	inf.readEoln();
	par.resize(N);
	for (int i = 0; i < N; i++) par[i] = i;
	int comps = N;
	for (int j = 0; j < M; j++) {
		int u = inf.readInt(0, N - 1, "U_j");
		inf.readSpace();
		int v = inf.readInt(0, N - 1, "V_j");
		inf.readSpace();
		inf.readInt(1, MAXW, "W_j");
		inf.readEoln();
		ensuref(u != v, "self-loop at edge %d", j);
		u = root(u); v = root(v);
		if (u != v) par[u] = v, comps--;
	}
	inf.readEof();
	ensuref(comps == 1, "graph is not connected (%d components)", comps);
	return 0;
}
