###########
psykorebase
###########

Easily perform merge-based rebases, i.e. rebases that don't alter history.

You can read the full rationale behind this idea here:

* http://tech.novapost.fr/merging-the-right-way-en.html
* http://tech.novapost.fr/psycho-rebasing-en.html


*****
What?
*****

As a summary:

* ``git checkout topic && git merge master`` is the wrong way to merge.
  Get ready for bad things to happen.

* ``git checkout topic && git rebase master`` is better but:

  * it alters history. It is safe from merge conflicts but doesn't guarantee
    that merged code works. You are losing some intermediate states of your
    work.

  * it is incompatible with branches you already pushed to shared repository.

``psykorebase``:

* mimics the "rebase" workflow, but only using merges, no history alteration.
  It replays "topic" changes on top of "master" in "topic" branch (just like
  rebase), without deleting "topic" changes.

* preserves all states of your code.

* is compatible with pushed branches.

* the main (and only?) counterpart is that there are more entries in history.
  There are more commits and more merges. Is that a drawback? If you look
  carefully, things are clear and clean. But some developers don't like it...


*******
Install
*******

Currently developped against Python 2.7.x.
Supports only Git for now.

.. code-block:: sh

   sudo pip install https://github.com/benoitbryon/psykorebase/archive/master.tar.gz#egg=psykorebase

Uninstall with ``sudo pip uninstall psykorebase``.


*****
Usage
*****

Git
===

Current, in-development prototype
---------------------------------

``psykorebase MASTER [TOPIC]`` performs a "psycho-rebase" of TOPIC branch on
top of MASTER. Where TOPIC is optional and defaults to current branch.

Example:

.. code-block:: sh

   git checkout master && git pull --rebase origin master  # Update master.
   git checkout topic && psykorebase master  # Psykorebase topic on top of master.

Planned usage (in development)
------------------------------

The default, issues one merge for each (new) commit in topic branch:

``git checkout topic && psykorebase master``.

The quick'n'dirty, issues one big merge which includes all (new) commits from
topic branch (merges heads):

``git checkout topic && psykorebase --fast master``

The default is safer, the ``--fast`` works well when there are poor chances of
problems.
