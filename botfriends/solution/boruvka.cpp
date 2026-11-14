#include "botfriends.h"
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
// Independent correct solution: Boruvka on the complete graph D(i,j)=d(i,j)+A_i+A_j.
// Each round: Dijkstra keeping, at every vertex, the 2 nearest sources from distinct components.
// Candidates per round: vertex meetings (b0+b1), graph edges (bx+w+by), leaf edges (A_i+bx at vertex i).
const ll INF=LLONG_MAX/4;
ll min_cost(int n,int m,vector<ll> A,vector<int> U,vector<int> V,vector<int> W){
	vector<int> st(n+1,0),to(2*m),wt(2*m);
	for(int j=0;j<m;j++)st[U[j]+1]++,st[V[j]+1]++;
	for(int i=0;i<n;i++)st[i+1]+=st[i];
	{vector<int> pos(st.begin(),st.end()-1);
	for(int j=0;j<m;j++){to[pos[U[j]]]=V[j];wt[pos[U[j]]++]=W[j];to[pos[V[j]]]=U[j];wt[pos[V[j]]++]=W[j];}}
	vector<int> comp(n);iota(comp.begin(),comp.end(),0);
	int cnt=n;ll total=0;
	vector<ll> bd(2*n);vector<int> bs(2*n);// slot k of v at index 2v+k; slot 0 is the nearer one
	vector<pair<ll,int>> bestOut(n);vector<int> p(n);
	while(cnt>1){
		fill(bd.begin(),bd.end(),INF);fill(bs.begin(),bs.end(),-1);
		priority_queue<pair<ll,int>,vector<pair<ll,int>>,greater<pair<ll,int>>> q;// (dist, 2*v+slot)
		auto offer=[&](int v,ll dv,int s){
			int c=comp[s],i0=2*v,i1=2*v+1;
			if(bs[i0]>=0&&comp[bs[i0]]==c){if(dv<bd[i0]){bd[i0]=dv;bs[i0]=s;q.push({dv,i0});}return;}
			if(bs[i1]>=0&&comp[bs[i1]]==c){
				if(dv<bd[i1]){bd[i1]=dv;bs[i1]=s;
					if(dv<bd[i0]){swap(bd[i0],bd[i1]);swap(bs[i0],bs[i1]);q.push({bd[i0],i0});}
					q.push({bd[i1],i1});}
				return;}
			if(dv<bd[i0]){bd[i1]=bd[i0];bs[i1]=bs[i0];bd[i0]=dv;bs[i0]=s;q.push({dv,i0});if(bs[i1]>=0)q.push({bd[i1],i1});}
			else if(dv<bd[i1]){bd[i1]=dv;bs[i1]=s;q.push({dv,i1});}
		};
		for(int i=0;i<n;i++)offer(i,A[i],i);
		while(!q.empty()){
			ll dv=q.top().first;int id=q.top().second;q.pop();
			if(dv!=bd[id])continue;
			int v=id>>1,s=bs[id];
			for(int e=st[v];e<st[v+1];e++)offer(to[e],dv+wt[e],s);
		}
		fill(bestOut.begin(),bestOut.end(),make_pair(INF,-1));
		auto consider=[&](int s,int t,ll w){
			int cs=comp[s],ct=comp[t];if(cs==ct)return;
			if(w<bestOut[cs].first)bestOut[cs]={w,t};
			if(w<bestOut[ct].first)bestOut[ct]={w,s};
		};
		for(int i=0;i<n;i++)for(int k=0;k<2;k++)if(bs[2*i+k]>=0)consider(i,bs[2*i+k],A[i]+bd[2*i+k]);
		for(int v=0;v<n;v++)if(bs[2*v+1]>=0)consider(bs[2*v],bs[2*v+1],bd[2*v]+bd[2*v+1]);
		for(int j=0;j<m;j++)for(int x=0;x<2;x++)for(int y=0;y<2;y++){
			int a=2*U[j]+x,b=2*V[j]+y;
			if(bs[a]>=0&&bs[b]>=0)consider(bs[a],bs[b],bd[a]+W[j]+bd[b]);
		}
		iota(p.begin(),p.end(),0);
		function<int(int)> f=[&](int x){while(p[x]!=x)x=p[x]=p[p[x]];return x;};
		for(int c=0;c<n;c++)if(comp[c]==c&&bestOut[c].second>=0){
			int a=f(c),b=f(comp[bestOut[c].second]);
			if(a!=b)p[a]=b,total+=bestOut[c].first,cnt--;
		}
		for(int i=0;i<n;i++)comp[i]=f(comp[i]);
	}
	ll r=total+*min_element(A.begin(),A.end());
	for(ll x:A)r-=x;
	return r;
}
