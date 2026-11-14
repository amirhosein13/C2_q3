#include "botfriends.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
// Exhaustive: Dijkstra over multisets of bot positions (the literal process). Tiny N only.
ll min_cost(int n,int m,vector<ll> A,vector<int> U,vector<int> V,vector<int> W){
	map<vector<int>,ll> D;
	priority_queue<pair<ll,vector<int>>,vector<pair<ll,vector<int>>>,greater<pair<ll,vector<int>>>> q;
	vector<int> s(n,1);D[s]=0;q.push({0,s});
	while(!q.empty()){
		ll d=q.top().first;vector<int> c=q.top().second;q.pop();
		if(D[c]!=d)continue;
		if(accumulate(c.begin(),c.end(),0)==1)return d;
		auto rel=[&](const vector<int>&x,ll nd){auto it=D.find(x);if(it==D.end()||nd<it->second){D[x]=nd;q.push({nd,x});}};
		for(int v=0;v<n;v++)if(c[v]>=2){auto x=c;x[v]--;rel(x,d+A[v]);}
		for(int j=0;j<m;j++){
			if(c[U[j]]){auto x=c;x[U[j]]--;x[V[j]]++;rel(x,d+W[j]);}
			if(c[V[j]]){auto x=c;x[V[j]]--;x[U[j]]++;rel(x,d+W[j]);}
		}
	}
	return -1;
}
