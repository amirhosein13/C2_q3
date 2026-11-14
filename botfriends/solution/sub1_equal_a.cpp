#include "botfriends.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
// Subtask 1 idea: all A equal -> MST(W) + (N-1)*A
static vector<int> p;
static int f(int x){while(p[x]!=x)x=p[x]=p[p[x]];return x;}
ll min_cost(int n,int m,vector<ll> A,vector<int> U,vector<int> V,vector<int> W){
	vector<int> id(m);iota(id.begin(),id.end(),0);
	sort(id.begin(),id.end(),[&](int a,int b){return W[a]<W[b];});
	p.resize(n);iota(p.begin(),p.end(),0);
	ll r=(ll)(n-1)*A[0];
	for(int j:id){int u=f(U[j]),v=f(V[j]);if(u!=v)p[u]=v,r+=W[j];}
	return r;
}
