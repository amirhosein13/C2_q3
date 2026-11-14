#include "botfriends.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
// WRONG: each bot (except one) independently goes to its best merge vertex: sum_i min_v(d(i,v)+A_v) - min A
ll min_cost(int n,int m,vector<ll> A,vector<int> U,vector<int> V,vector<int> W){
	vector<vector<pair<int,int>>> g(n);
	for(int j=0;j<m;j++)g[U[j]].push_back({V[j],W[j]}),g[V[j]].push_back({U[j],W[j]});
	vector<ll> d(A);
	priority_queue<pair<ll,int>,vector<pair<ll,int>>,greater<pair<ll,int>>> q;
	for(int i=0;i<n;i++)q.push({d[i],i});
	while(!q.empty()){
		ll dd=q.top().first;int x=q.top().second;q.pop();
		if(dd!=d[x])continue;
		for(auto&e:g[x])if(dd+e.second<d[e.first])d[e.first]=dd+e.second,q.push({d[e.first],e.first});
	}
	ll s=-*min_element(A.begin(),A.end());
	for(int i=0;i<n;i++)s+=d[i];
	return s;
}
