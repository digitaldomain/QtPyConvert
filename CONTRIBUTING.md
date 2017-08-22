Contributing to ``qt_py_convert``
=================================

The ``qt_py_convert`` package consists of a core ddg api, gui, and a suite of nodes and graphs.

All features and bugfixes for this package must be accompanied by a test reproducing the bug, or
describing the intended behavior of the feature.  These tests should generally be coded first, and
checked in as a separate and prior commit.

Development should be done in branches, ideally named with the corresponding bug or feature ticket,
and be restricted to the scope of that ticket.  The changes should consist of many understandable
and related commits.


Checkin style
-------------

Commit messages must be formatted roughly according to git standards.  In particular, the subject
line is not to be too long, is to be in the imperative mood and active voice, and is to start with a
verb and end with no period.  For example::

   add test for feature xxx

Here is a list of suggested standard verbs for starting off your commit subject line::

   add update repro fix implement remove

Here are the rules for commit messages:

   1. Separate subject from body with a blank line
   2. Limit the subject line to 72 characters
   3. Do not end the subject line with a period
   4. Use the imperative mood in the subject line
   5. Wrap the body at 100 characters
   6. Use the body to explain *what* and *why* vs. *how*

Precise and correct spelling, punctuation, and grammar are expected in all code and VCS artifacts.

For further reading about why this is important, see:

https://chris.beams.io/posts/git-commit


Code style
----------

All ``python`` code must pass the DD lint critical level.  Ensure you check your code before commit
with:

~~~
make ddlint
~~~


Developer Cycle
---------------

After you have a ticket for your work, start from a suitable branch-off point (normally the
up-to-date ``master`` branch in this package).

~~~
# ensure we are up-to-date
git checkout master
git pull

# start a new branch for our development
git checkout -b ticket_12345
~~~

You can optionally add a *short* description by seperating the words with ``-``s. For example:

~~~
git checkout -b ticket_12345-fix-foo-bar
~~~


Within this branch, stage up commits.  Commit frequently!  Smaller commits with a small subtask
is good coding practice.

From time-to-time, you may wish to rebase your development against master in order to stay current:

~~~
# ensure your local repo is clean, eg. either commit or stash, then:
git checkout master
git pull

# go back to our ticket and rebase
git checkout ticket_12345
git rebase master
# at this point, hopefully everything will cleanly reapply, but you may need to resolve some
# conflicts.  in any case, you will probably immediately wish to rerun your test suites.
~~~

When you are happy with your work and ready to propose merging of it, you should push this branch
to the origin repository and contact the maintainers with the pull request.

~~~
git push origin ticket_12345
~~~

Your ticket branch must also update the ``CHANGELOG.md`` in the ``Unreleased`` section at the
top of that document.

Please read about the role and format of the CHANGELOG document at:

http://keepachangelog.com/en/0.3.0


Merging for Maintainers
-----------------------

A feature branch ready for merging should pass all tests and conformance requirements.  It should
generally be rebased against the maintenence branch into which it is being merged, so that the
branch applies cleanly.  You may want to check this in a separate branch with a pattern like:

~~~
# checkout candidate branch for merging
git checkout ticket_12345

# branch off so we can test whether it will apply cleanly
git checkout -b ticket_12345_merge

# rebase against maintenance branch (here master, might be another branch):
git rebase master

# do clean install and run test suite.
# if anything fails here, or we have a conflict in the rebase, we probably want to kick this back.
make clean; make install; make ddtest; make ddlint
~~~

Merging should be done so to force a merge with the ``--no-ff`` (no fast-forward) option:

~~~
git merge --no-ff ticket_12345
~~~

Only now should the version in the manifest be updated in preparation for release.  For example, if
we now go to version 1.23.4, we would make the one-line change in the package manifest, then commit
this change with the commit message of the form ``version 1.23.4``, and tag it in the release
branch:

~~~
# make edit to version line in manifest:
vi manifest.yaml

# do commit of this change
git commit -a -m 'version 1.23.4'

# tag
git tag -a '1.23.4' -m 'version 1.23.4'
~~~

### Interacting with svn ###

Currently we are transitioning to ``git`` from ``svn``.  Until that transition is complete,
maintainers are responsible for keeping the two in sync.  This is generally quite easy, and once
it is going, you really only need to duplicate a bit of add/remove to the svn repo as files in
the git repo add/remove/change names.

We won't attempt to use the git-svn tools here.  Instead, it isn't much work to do the two VCS sync
manually.  Let's begin with aligning the two repositories initially.

Because ``svn`` tracks files in every subdirectory under the repo, it is easiest to first checkout
the ``svn`` branch:

~~~
svn co $DD_SVN_ROOT/software/packages/ddg/trunk ddg
~~~

Next, git clone the (presumably synced) repo from origin to a temporary place, eg:

~~~
mkdir /var/tmp/git_temp
cd /var/tmp/git_temp
git clone git@dd-git.d2.com:pipeline/ddg.git
cd /path/to/svn/repository/ddg
rsync -av /var/tmp/git_temp/ddg/.git .
~~~

At which point (if the svn and git repo are the same branch and have been kept in sync), we should
have a clean svn repo and a clean git repo in the same place:

~~~
# should report clean
svn stat

# should also report clean
git status
~~~

From now on it is suggested that any time you wish to commit back to svn, you do the merging like
normal, and then commit back branch merges to svn:

~~~
# we have just done our due-diligence and have a clean branch for merging:
git merge --no-ff ticket_12345

# now we keep svn largely in sync on the entire branch
svn ci -m 'fix the node memory leak on parameter rename (#12345)'
~~~

The downside here is that we lose blame history with svn, as well as the individual commits.
This doesn't seem so bad considering git records all this and is the primary VCS anyway.


