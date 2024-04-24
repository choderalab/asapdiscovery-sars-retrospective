So it looks like using local dask on lilac is working.

I can forward the dask output with something like 
```bash
ssh -o ServerAliveInterval=120 -A -L 8001:localhost:9000 lilac ssh -L 9000:127.0.0.1:8787 -N lt18
```
and then open a browser on my local machine to `localhost:8001` to see the dask dashboard.

Now I'm checking PR #1005 to see if that will make multipose docking work sufficiently to get some results.

