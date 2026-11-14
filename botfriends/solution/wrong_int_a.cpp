#include "botfriends.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
// WRONG: A stored in int (overflow / truncation for A > 2^31-1)
static vector<int> p;
static int f(int x){while(p[x]!=x)x=p[x]=p[p[x]];return x;}
ll min_cost(int n,int m,vector<ll> A0,vector<int> U,vector<int> V,vector<int> W){
	vector<int> A(A0.begin(),A0.end());vector<vector<pair<int,int>>> g(n);
	for(int j=0;j<m;j++)g[U[j]].push_back({V[j],W[j]}),g[V[j]].push_back({U[j],W[j]});
	vector<ll> d(A.begin(),A.end());vector<int> o(n);
	priority_queue<pair<ll,int>,vector<pair<ll,int>>,greater<pair<ll,int>>> q;
	for(int i=0;i<n;i++)o[i]=i,q.push({d[i],i});
	while(!q.empty()){
		ll dd=q.top().first;int u=q.top().second;q.pop();
		if(dd!=d[u])continue;
		for(auto&e:g[u])if(d[u]+e.second<d[e.first])d[e.first]=d[u]+e.second,o[e.first]=o[u],q.push({d[e.first],e.first});
	}
	vector<tuple<ll,int,int>> c;
	for(int i=0;i<n;i++)if(o[i]!=i)c.emplace_back(A[i]+d[i],i,o[i]);
	for(int j=0;j<m;j++)if(o[U[j]]!=o[V[j]])c.emplace_back(d[U[j]]+W[j]+d[V[j]],o[U[j]],o[V[j]]);
	sort(c.begin(),c.end());
	p.resize(n);iota(p.begin(),p.end(),0);
	ll r=*min_element(A.begin(),A.end());
	for(ll x:A)r-=x;
	for(auto&t:c){int u=f(get<1>(t)),v=f(get<2>(t));if(u!=v)p[u]=v,r+=get<0>(t);}
	return r;
}
