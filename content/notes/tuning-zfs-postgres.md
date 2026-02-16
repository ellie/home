+++
title = "Tuning ZFS for Postgres"
date = 2023-09-01

[taxonomies]
tags = []
+++

- recordsize=128 not that bad, actually
- preferring a scan to index for some reason. `random_page_cost = 1` sorted that
	- worked after running analyze and a couple of queries