#include "botfriends.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
// WRONG: everybody walks to the vertex with minimum A and merges there
ll min_cost(int n,int m,vector<ll> A,vector<int> U,vector<int> V,vector<int> W){
	vector<vector<pair<int,int>>> g(n);
	for(int j=0;j<m;j++)g[U[j]].push_back({V[j],W[j]}),g[V[j]].push_back({U[j],W[j]});
	int r=min_element(A.begin(),A.end())-A.begin();
	vector<ll> d(n,LLONG_MAX/4);d[r]=0;
	priority_queue<pair<ll,int>,vector<pair<ll,int>>,greater<pair<ll,int>>> q;q.push({0,r});
	while(!q.empty()){
		ll dd=q.top().first;int x=q.top().second;q.pop();
		if(dd!=d[x])continue;
		for(auto&e:g[x])if(dd+e.second<d[e.first])d[e.first]=dd+e.second,q.push({d[e.first],e.first});
	}
	ll s=(ll)(n-1)*A[r];
	for(int i=0;i<n;i++)s+=d[i];
	return s;
}
