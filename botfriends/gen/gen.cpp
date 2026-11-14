// Generator for "botfriends".
// Usage: gen <type> <N> <M> <amode> <alo> <ahi> <wmode> <wlo> <whi> [<seed-tag>]
//   type : randtree | deeptree | star | binary | path | grid | cluster<K> | multi | pathdec | pathinc | hidchain[rev|shuf]
//   amode: eq (one value for all) | uni | log | hub<K> (K cheap vertices in [1,alo], rest uni [alo,ahi])
//   wmode: uni | log
// pathdec/pathinc: anti-SPFA chain (labels NOT shuffled); A_i = 10^12 - i*alo, W in [1, alo-1], M = N-1.
// All other types: labels and edge order are shuffled; graph is connected; extra edges are random.
#include "testlib.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int N, M;
vector<ll> A;
vector<array<ll, 3>> E;

ll logUni(ll lo, ll hi) {
	double l = log((double)lo), h = log((double)hi);
	ll x = (ll)llround(exp(rnd.next(l, h)));
	return max(lo, min(hi, x));
}
ll pickW(const string& wm, ll lo, ll hi) { return wm == "log" ? logUni(lo, hi) : rnd.next(lo, hi); }

int main(int argc, char* argv[]) {
	registerGen(argc, argv, 1);
	ensuref(argc >= 10, "not enough arguments");
	string type = argv[1];
	N = atoi(argv[2]); M = atoi(argv[3]);
	string am = argv[4]; ll alo = atoll(argv[5]), ahi = atoll(argv[6]);
	string wm = argv[7]; ll wlo = atoll(argv[8]), whi = atoll(argv[9]);
	ensuref(N >= 1 && M >= N - 1, "bad N/M");

	if (type == "pathdec" || type == "pathinc") {
		ll K = alo;
		A.resize(N);
		for (int i = 0; i < N; i++) A[i] = 1000000000000LL - (ll)i * K;
		for (int i = 0; i + 1 < N; i++) E.push_back({i, i + 1, rnd.next(1LL, K - 1)});
		if (type == "pathinc") {
			reverse(A.begin(), A.end());
			for (auto& e : E) e[0] = N - 1 - e[0], e[1] = N - 1 - e[1];
		}
		printf("%d %d\n", N, (int)E.size());
		for (int i = 0; i < N; i++) printf("%lld%c", A[i], i + 1 < N ? ' ' : '\n');
		for (auto& e : E) printf("%lld %lld %lld\n", e[0], e[1], e[2]);
		return 0;
	}

	if (type == "hidchain" || type == "hidchainrev" || type == "hidchainshuf") {
		// anti-SPFA independent of A-order: chain c_0..c_{L-1} (all A = 10^12, weights in [1,K/2]),
		// each c_j has a private source s_j (edge weight 1) with A = 10^12/2 - j*K, so the best
		// distance of every chain vertex keeps improving from farther and farther sources.
		ll K = alo;
		int L = N / 2;
		ensuref(N == 2 * L && M == 2 * L - 1, "hidchain needs N even and M = N-1");
		A.assign(N, 1000000000000LL);
		vector<int> c(L), sid(L);
		for (int j = 0; j < L; j++) c[j] = j, sid[j] = L + j;
		for (int j = 0; j < L; j++) A[sid[j]] = 500000000000LL - (ll)j * K;
		for (int j = 0; j + 1 < L; j++) E.push_back({c[j], c[j + 1], rnd.next(1LL, K / 2)});
		for (int j = 0; j < L; j++) E.push_back({c[j], sid[j], 1});
		vector<int> perm(N);
		iota(perm.begin(), perm.end(), 0);
		if (type == "hidchainrev") for (int i = 0; i < N; i++) perm[i] = N - 1 - i;
		if (type == "hidchainshuf") shuffle(perm.begin(), perm.end());
		vector<ll> B(N);
		for (int i = 0; i < N; i++) B[perm[i]] = A[i];
		printf("%d %d\n", N, (int)E.size());
		for (int i = 0; i < N; i++) printf("%lld%c", B[i], i + 1 < N ? ' ' : '\n');
		for (auto& e : E) printf("%d %d %lld\n", perm[e[0]], perm[e[1]], e[2]);
		return 0;
	}

	// vertex weights
	A.assign(N, 0);
	if (am == "eq") {
		ll c = rnd.next(alo, ahi);
		for (auto& a : A) a = c;
	} else if (am == "uni") {
		for (auto& a : A) a = rnd.next(alo, ahi);
	} else if (am == "log") {
		for (auto& a : A) a = logUni(alo, ahi);
	} else if (am.substr(0, 3) == "hub") {
		int k = atoi(am.c_str() + 3);
		for (auto& a : A) a = rnd.next(alo, ahi);
		for (int t = 0; t < k; t++) A[rnd.next(0, N - 1)] = rnd.next(1LL, alo);
	} else ensuref(false, "bad amode");

	// spanning structure
	vector<int> cl(N, 0);
	int K = 1;
	if (type.substr(0, 7) == "cluster") {
		K = max(1, atoi(type.c_str() + 7));
		for (int i = 0; i < N; i++) cl[i] = i < K ? i : rnd.next(0, K - 1);
	}
	ll wmidHi = wlo + max(0LL, (whi - wlo) / 1000);
	auto edgeW = [&](int u, int v) -> ll {
		if (K > 1) return cl[u] == cl[v] ? rnd.next(wlo, wmidHi) : rnd.next(max(wlo, whi / 2), whi);
		return pickW(wm, wlo, whi);
	};
	auto addE = [&](int u, int v) { E.push_back({u, v, edgeW(u, v)}); };

	if (type == "grid") {
		int R = max(1, (int)sqrt((double)N)), C = (N + R - 1) / R;
		for (int i = 0; i < N; i++) {
			int r = i / C, c = i % C;
			if (c + 1 < C && i + 1 < N) addE(i, i + 1);
			if (i + C < N) addE(i, i + C);
			(void)r;
		}
	} else {
		for (int i = 1; i < N; i++) {
			int p;
			if (type == "randtree" || type == "multi") p = rnd.next(0, i - 1);
			else if (type == "deeptree") p = i - 1 - rnd.next(0, min(i - 1, 3));
			else if (type == "star") p = rnd.next(0, min(i - 1, 2));
			else if (type == "binary") p = (i - 1) / 2;
			else if (type == "path") p = i - 1;
			else if (K > 1) {
				// connect inside cluster if possible, else to a random earlier vertex
				p = -1;
				for (int t = 0; t < 30 && p < 0; t++) { int q = rnd.next(0, i - 1); if (cl[q] == cl[i]) p = q; }
				if (p < 0) p = rnd.next(0, i - 1);
			} else { ensuref(false, "bad type"); p = 0; }
			addE(p, i);
		}
	}
	ensuref((int)E.size() <= M, "M too small for this graph type (%d edges needed)", (int)E.size());
	// extra edges
	vector<pair<int,int>> pool;
	if (type == "multi") { // few distinct pairs, many parallel copies
		for (auto& e : E) pool.push_back({(int)e[0], (int)e[1]});
	}
	while ((int)E.size() < M) {
		if (N < 2) break;
		int u, v;
		if (!pool.empty() && rnd.next(0, 3)) { auto p = pool[rnd.next(0, (int)pool.size() - 1)]; u = p.first; v = p.second; }
		else if (K > 1 && rnd.next(0, 9)) { // mostly intra-cluster
			u = rnd.next(0, N - 1);
			int t = 0; do { v = rnd.next(0, N - 1); } while ((v == u || cl[v] != cl[u]) && ++t < 50);
			if (v == u) continue;
		} else { u = rnd.next(0, N - 1); v = rnd.next(0, N - 2); if (v >= u) v++; }
		addE(u, v);
	}
	ensuref((int)E.size() == M, "could not reach M");

	// shuffle labels and edges
	vector<int> perm(N);
	iota(perm.begin(), perm.end(), 0);
	shuffle(perm.begin(), perm.end());
	vector<ll> B(N);
	for (int i = 0; i < N; i++) B[perm[i]] = A[i];
	shuffle(E.begin(), E.end());
	printf("%d %d\n", N, M);
	for (int i = 0; i < N; i++) printf("%lld%c", B[i], i + 1 < N ? ' ' : '\n');
	for (auto& e : E) {
		int u = perm[e[0]], v = perm[e[1]];
		if (rnd.next(2)) swap(u, v);
		printf("%d %d %lld\n", u, v, e[2]);
	}
	return 0;
}
