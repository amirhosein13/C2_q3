#include "botfriends.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
// Subtask 2 idea: Kruskal on graph edges only, weight W+A_u+A_v (correct when max A <= min W)
static vector<int> p;
static int f(int x){while(p[x]!=x)x=p[x]=p[p[x]];return x;}
ll min_cost(int n,int m,vector<ll> A,vector<int> U,vector<int> V,vector<int> W){
	vector<pair<ll,int>> c;
	for(int j=0;j<m;j++)c.push_back({W[j]+A[U[j]]+A[V[j]],j});
	sort(c.begin(),c.end());
	p.resize(n);iota(p.begin(),p.end(),0);
	ll r=*min_element(A.begin(),A.end());
	for(ll x:A)r-=x;
	for(auto&e:c){int u=f(U[e.second]),v=f(V[e.second]);if(u!=v)p[u]=v,r+=e.first;}
	return r;
}
