+++
title = "Advancing bookmarks with jj"
date = 2026-05-13

[taxonomies]
tags = ["jj"]
+++

A bunch of people read my [post about using jj](@/notes/jj-getting-started.md) yesterday! 

In that note I pointed out that I found jj not automatically moving bookmarks 
when a new commit is created to be really frustrating.

Well... turns out there is a really simple command that will do that! It's not 
automatic, but it's better than manually moving the bookmark

```
jj bookmark advance

# or for short

jj b a
```

So you can make a new commit, run `jj b a`, and then push.
