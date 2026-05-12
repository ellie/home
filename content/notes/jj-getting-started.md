+++
title = "Getting started with jj"
date = 2026-05-12

[taxonomies]
tags = ["jj"]
+++

Over the past few weeks, I have been using jj! This is not the first time I have 
tried it, but it is the first time it has stuck.

For years, my git workflow has used "make a change, then `git commit --amend
--no-edit && git push --force-with-lease`", while on a branch. This meant that my
changes would be up to date on the remote with very little latency. PRs would
rarely be more than a small number of commits, usually 1, and I would try to
keep them as small as possible.

Since working with agents, I have found myself switching branch much more
frequently. Because of this, I either have to `git stash`, or make some silly
little wip commit to stop my changes from stepping on each other.

Enter our new hero, `jj`! The model here is a bit different. I will not write a
huge manual because there are plenty of those, and they are better than anything
I would whack into my notes with little thought.

Suffice to say, the main thing that appeals to me is that my changes are always
committed. Every edit automatically amends the most recent commit, and a push
will overwrite the remote (or, in jj speak, move it "sideways").

Editing a change is easy, no checkout/rebase dance. It's as if someone took my
preferred git workflow and built a tool around it. I am unsure why it took me so
long to figure this out.

Just a braindump really. I will probably publish more notes as I learn more
things.

## Workflow

When making a change, my workflow is

```
jj new main

<do some coding>

jj describe -m 'feat: something really cool'
jj git push -c @
```

Done. Merge PR, repeat.

> [!NOTE]
> In jj, we talk about changes more than commits. A change is a constantly
> evolving commit. And "@" refers to the current change

## Starting a new change
Before doing some work, you should start a change. All of the edits you are 
about to make will live here

```
jj new main
```

This makes your commit (change vs commit is real and confusing when you're new) 
on top of main (the commit with the bookmark main). If you want to make a new 
change that is the child of your current, just run `jj new`.

## Describing a change

You're probably used to adding some changes to your staging area, then
committing them with a message. Well with jj, your changes are already added.
But your change probably does not have a description! (like a commit message)

```
jj describe -m 'hello i am a message'
```

You can also describe a change when you make it, with

```
jj new -m "hello i am a message"
```

## Pushing a commit to a new branch
If you're on a change, you're happy with it, and you want it on github so some
agent can roast your (claude's) code?

Easy.

```
jj git push -c @
```

Aka "use git to push the current commit". It will automatically create a branch,
push that to the remote. You can actually do this over and over again while
making changes, and it will automatically translate the jj magic into a git
amend and force push.

I am excited for jj to get its own protocol and host though.

## Editing a commit
If you want to jump back and edit an existing change? Easy

```
jj edit <change-id>
```

This is where things start to feel powerful me, and also where the existing 
mental model I try to tack this onto starts to break. There's no checkout,
rebase, etc to fuck about with.

> [!NOTE]
> jj has changes AND commits. If we recall that it constantly evolves a commit,
> rather than having a staging area, then we can think of the change as the
> stable id, and the commit id as the one that changes with each edit

## Undoing things
Pretty much anything you do in jj is stored in the op log. If you do a thing,
and it messes up? `jj undo` to the rescue.

## More git stuff

jj is still piggybacking on top of git, mostly. They have made it easy to
convert an existing repo, and also integrate with github
 
```
# Create a jj repo inside of a git repo
jj git init

# Fetch from the remote (github etc)
jj git fetch

# Push
jj git push

# Clone
jj git clone
```

## Okay where are the branches

There aren't any! Not in the way you are used to. jj uses "bookmarks", or, a
string that you can attach to a commit. When you push a change, it automatically
creates a bookmark for you - eg, `push-refrefref`


```
# bookmark the current change with a name
jj bookmark create <name>

# move a bookmark to a new commit
jj bookmark set <name> -r <commit>

# other things exist just use --help
```

The main frustration I have is that bookmarks do not move when I create a new
change.

From the glossary
> Unlike in Git, there is no concept of a "current bookmark"; bookmarks do not 
> move when you create a new commit. Bookmarks do automatically follow the 
> commit if it gets rewritten.

I'll write up something else about rebasing and editing and all the fun stuff
later

---

Note: writing this in Vim has been super annoying, because I have `jj` bound to
`<esc>`.
