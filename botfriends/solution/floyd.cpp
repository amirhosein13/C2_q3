#include "botfriends.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
// O(N^3) Floyd-Warshall + O(N^2) Prim on D(i,j)=d+A_i+A_j
ll min_cost(int n,int m,vector<ll> A,vector<int> U,vector<int> V,vector<int> W){
	const ll INF=LLONG_MAX/4;
	vector<vector<ll>> d(n,vector<ll>(n,INF));
	for(int i=0;i<n;i++)d[i][i]=0;
	for(int j=0;j<m;j++){d[U[j]][V[j]]=min(d[U[j]][V[j]],(ll)W[j]);d[V[j]][U[j]]=d[U[j]][V[j]];}
	for(int k=0;k<n;k++)for(int i=0;i<n;i++)if(d[i][k]<INF)for(int j=0;j<n;j++)d[i][j]=min(d[i][j],d[i][k]+d[k][j]);
	vector<ll> key(n,INF);vector<bool> in(n);key[0]=0;
	ll r=*min_element(A.begin(),A.end());
	for(ll x:A)r-=x;
	for(int it=0;it<n;it++){
		int u=-1;for(int i=0;i<n;i++)if(!in[i]&&(u<0||key[i]<key[u]))u=i;
		in[u]=1;if(it)r+=key[u];
		for(int v=0;v<n;v++)if(!in[v])key[v]=min(key[v],d[u][v]+A[u]+A[v]);
	}
	return r;
}
