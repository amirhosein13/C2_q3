#include "botfriends.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
// Prim on D; every time a vertex joins, run Dijkstra from it: O(N M log N) time, O(N+M) memory
ll min_cost(int n,int m,vector<ll> A,vector<int> U,vector<int> V,vector<int> W){
	const ll INF=LLONG_MAX/4;
	vector<vector<pair<int,int>>> g(n);
	for(int j=0;j<m;j++)g[U[j]].push_back({V[j],W[j]}),g[V[j]].push_back({U[j],W[j]});
	vector<ll> key(n,INF),d(n);vector<bool> in(n);key[0]=0;
	ll r=*min_element(A.begin(),A.end());
	for(ll x:A)r-=x;
	for(int it=0;it<n;it++){
		int u=-1;for(int i=0;i<n;i++)if(!in[i]&&(u<0||key[i]<key[u]))u=i;
		in[u]=1;if(it)r+=key[u];
		fill(d.begin(),d.end(),INF);d[u]=0;
		priority_queue<pair<ll,int>,vector<pair<ll,int>>,greater<pair<ll,int>>> q;q.push({0,u});
		while(!q.empty()){
			ll dd=q.top().first;int x=q.top().second;q.pop();
			if(dd!=d[x])continue;
			for(auto&e:g[x])if(dd+e.second<d[e.first])d[e.first]=dd+e.second,q.push({d[e.first],e.first});
		}
		for(int v=0;v<n;v++)if(!in[v])key[v]=min(key[v],d[v]+A[u]+A[v]);
	}
	return r;
}
