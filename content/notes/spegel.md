+++
title = "Spegel for p2p docker registries in k3s"
date = 2026-02-16

[taxonomies]
tags = ["kubernetes", "docker"]
+++

[spegel](https://yeet.ellie.wtf/i/e2cec761f3a3353d00bd4ce001a3b3d749d92133721c362a9f39ae585dfbeb63.gif)

I was recently setting up a new k3s cluster for running 
[Atuin](https://atuin.sh). Since I wrote my [last note](/notes/hetzner-k3s/) on 
the subject, a few things have changed!

I definitely need to do a v2 of my post, but in the meantime I learned a bit 
about Spegel, an optional integrated registry included with k3s. 

If server nodes are started with `--embedded-registry`, then they will setup + 
run a Spegel registry. This means they host a local OCI registry on port 6443,
while connecting to a p2p network over port 5001.

In order for upstream registry mirroring to work, you must edit 
`/etc/rancher/k3s/registries.yaml`

For example

```yaml
mirrors:
  docker.io:
  registry.k8s.io:
```

enables mirroring of those two registries. This file is read at startup. You
can enable wildcard mirroring with `"*":`, quoted required.

The p2p routing works in a very similar way to BitTorrent - Spegel also uses a
Kademlia DHT for resolving digests.
