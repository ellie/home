+++
title = "Saving macOS disk space with mole"
date = 2026-08-19

[taxonomies]
tags = []
+++

Since running agents in a bunch of workspaces, I've been running out of storage on my mac FAR more often.

Granted, this is largely due to `cargo` being such a hog, and I need to run `cargo clean` more than I do.

But it's also due to years of accumulated cruft, all over my machine

`mole` is a pretty neat CLI that can find and clear leftover data

> 🐹 Clean, uninstall, analyze, optimize, and monitor your Mac.

Just 

```
brew install mole
```

and then

```
mole
```

It saved me 30gb