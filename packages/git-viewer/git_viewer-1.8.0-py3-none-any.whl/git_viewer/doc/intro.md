# Three Executables
`gitl` is the main program, a wrapper around `git log` from which you can select and open commits.
`gitd` is a wrapper around `git diff` using the details view of `gitl`.
`gits` is a wrapper around `git show` using the details view of `gitl`.


# About this help
This help explains how to use git-viewer while it is running.
For a help on it's command line arguments run `gitl --help`, `gits --help` or `gitd --help` respectively.
For more information about git in general see `git help git` and `git help --guides`.

In this program keys with a name longer than one character are wrapped in angular brackets to make it clear whether "esc" is the escape key or the three keys "e", "s" and "c" pressed after one another. For more information on the syntax of key names see the help of the `map` command.
If several keyboard shortcuts are mapped to the same command all alternatives are displayed, separated by a slash (unless you change the setting %help.key-sep%).

You can open a list of all keyboard shortcuts with `help --shortcuts`.
You can open a list of all commands which can be mapped to keys and used in config files with `help --commands`.
You can open a list of all settings which can be set using the `set` command with `help --settings`.
You can jump directly to the help of a command with `link` and pressing the key(s) appearing behind the command.


# How to use this program
When you start gitl you are greeted with the log view.
The log view shows the history of commits with the most recent commit on top.
By default only the current branch is displayed, with `option --log --toggle -- --branches` you can show all branches.

Above the commits are (depending on configuration and the current status of your git repository) additional lines for staged, unstaged, untracked and stashed changes.

You can select a commit (or a line for the other changes above) using `cursor down`, `cursor up`, `search --open`, `select` and variations of those commands, see their help respectively.

Depending on the size of your terminal (and your configuration) a details view may already be visible right or below of the log view.
If it's not you can open it using `go details` or `layout split`. If you want to focus on the log view you can hide the details view with `layout one`.

The details view shows more information for the selected line, including the diff of what has changed.

If log view and details view are visible at the same time you can move the cursor to the details view using `go details`, `go right` or `go toggle`.

In the details view there is no selection by default so that `cursor down` and `cursor up` scroll immediately instead of only when a selected line reaches the border.
It is possible to enable a selection (visual mode) with `visual --toggle` or directly jumping around using `select --next-paragraph` to jump to the next hunk or `select --next-section` to jump to the next file or `search --open` to enter a search term.

You can open the current line in the text editor specified by the EDITOR environment variable with:
- `open --after` to open the line as it was after the current commit
- `open --before` to open the line as it was before the current commit
- `open --before-left` to open the line as it was before the current merge commit on the other branch
- `open --now` to open the line as it is now in the working directory (if lines have been added or removed before the current line since the currently displayed version the selection will be a little or totally off).
vi, vim and nano are supported out of the box, if you want to use another editor you need to tell git-viewer how to jump to a specific line and how to open a file readonly using `add-editor`.

You can disable the visual mode again with `cancel` or `visual --toggle`. This works in the log view, too.

If you have referenced other commits in a commit message using their hash you can directly jump to them using `link`, just like how you can follow links in qutebrowser.
`link` adds a link hint, one or several characters in square brackets, after all recognized hashes. Pressing these keys opens another details view for that commit.

You can copy various information about a commit using `yank`.

You can return to the previous view using `go left` or immediately to the log view with `go log`.

You can open a details view for a corresponding tag using `go tag --toggle --last` or `go tag --toggle --containing`.

You can exit this application using `quit`.


# Line numbers
The line numbers displayed in the details view refer to the version after that commit by default.
You can switch to the line numbers before that commit with `linenumber --toggle`.
In the case of a merge commit this will show two line numbers per line, the left for the left branch, the right for the right branch.

Some lines do not have line numbers because they do not exist in the version that the linenumbers are displayed for.

Line numbers are not available when using `--word-diff` (see command `option`).


# Scrolling through log view is slow
If log view and details view are open at the same time scrolling through the log view is slow because the details view is always updated.
You can avoid that by:
- directly jumping to interesting commit with `search --open`, `search --reverse --open`, `select`, `select --next-tag`, `select --prev-tag`
- disable updating of details view with `set details-view.auto-open!`
- disable visual mode with `visual --toggle`
- disable details view with `layout one` and reenable it with `layout split`
- add `set layout.preferred=one` to your config file using `config.edit` (requires restart or `layout auto`)


# Searching
You can enter a search term with `search --open` for a forward search or `search --reverse --open` for a backward search.
You can also add search flags to specify whether the search is supposed to be case sensitive or insensitive or a regular expression or a literal string.
See the help for `search`.

You can choose a previous search term to reuse with `cursor up` and `cursor down`.
(The automatic insertion of keys mapped to a command may insert too many keys here, if a character is inserted no command is triggered.)
The search terms are not saved on disk, when you quit the program they are forgotten.

After typing in the search term you can start the search with `activate` or cancel the search with `cancel`.

You can jump to the next search result with `search --next` or the previous with `search --prev`.
What next and previous mean depends on whether you have started the search with `--reverse` or not.
When the end/start is reached this is indicated in the status bar at the bottom of the window.

If you are using the `-G` or `-S` argument for the log this is setup as search term so that you can directly start searching with `search --next`.


# Selection history
After you have searched for something you may want to return to the line where you have started the search.
You can do so with `select --prev-selection`.
The inverse operation is `select --next-selection`.

A line you can return to using `select --prev-selection` is saved every time you open the commit details or you switch the method of selecting a line (go to next/previous line, go to first/last line or next/previous page, search for string, jump to commit, jump to tag, jump to next/previous paragraph, jump to next/previous section, go back in history).

For example, if you move the selection by repeatedly using `cursor down` and/or `cursor up` only the most recent selection is saved.
If you then search for a string and jump through the search results using `search --next` and/or `search --prev` you can return to the point where you have started the search using `select --prev-selection` and back to the most recently visited search result using `select --next-selection`.


# Configuration
You can open the config file with `config.edit`.
For more information see the help of `config.load`.

If you want to see an example you can export the current settings and keybindings with `config.export`.

The location of the config file is determined by one of the Python libraries platformdirs, xdgappdirs or appdirs if they are installed.
If they are not installed and XDG_CONFIG_HOME is not set the config file is put in ~/.config/git-viewer/.

It is possible to cycle through different sets of configuration by creating several config files and mapping `config.load --default-path <otherconfig>` to the same key in each of them:

~/.config/git-viewer/config:

	...
	config.load config_white

~/.config/git-viewer/config_white:

	set color.subtitle="white,bold"
	...

	map C 'config.load --default-path config_yellow'

~/.config/git-viewer/config_yellow:

	set color.subtitle="yellow,bold"
	...

	map C 'config.load --default-path config_magenta'

~/.config/git-viewer/config_magenta:

	set color.subtitle="magenta,bold"
	...

	map C 'config.load --default-path config_white'

--default-path is not needed in the main config file because if config.load is used in a config file the config file to be loaded is assumed to be in the same directory.
But if a key is bound to config.load that config.load is not executed in a config file.
Therefore without the --default-path the config file would be searched in the current working directory.


# Commands
The keys you press are mapped to commands.
These commands are divided into primitive commands and programmable commands.

Primitive commands are executed by the widgets they are passed to
and perform standard user interface actions like moving the cursor.
Programmable commands are Python classes which inherit from api_commands.Command
and perform more specialized actions like opening another view.

Programmable commands are based on Python's shlex and argparse libraries
and therefore have a syntax similar to shell commands.
Arguments are split at spaces.
If an argument contains a space it needs to be wrapped in single or double quotes.
If a positional argument starts with a hyphen you need to explicitly separate
the positional arguments from the optional arguments by inserting a -- in between.
If an optional argument takes a value this value can either be given in a separate
argument or in the same argument separated by an equals sign.
Optional arguments can be abbreviated as long as they are unambiguous.


# How do I add/commit/push changes?
Not from git-viewer. As the name says, this is merely a viewer.
Git offers a good interactive command line interface for this stuff on it's own - no wrapper needed.
But if you want a different interface for that, anyway, you can check out tig.
https://jonas.github.io/tig/

In the following I give a short summary of how to use git's standard command line interface
and a few tips how to use git in general.

First you need to create a new repository with `git init <reponame>` or
clone an existing repository with `git clone --recurse-submodules <url>`.

Add changes with `git add -p [<filename>]`.
In order to add only part of an untracked file you first need to run `git add --intent-to-add <filename>`.

You can undo adding changes with `git reset -p [<filename>]`.

Commit the changes with `git commit`.
Take the time to write a helpful commit message - you'll be thankful later!
The first line should summarize what you have done in this commit.
If the changes cannot be summarized in one short line you have added too many changes at once.
Abort the commit by removing all lines which do not start with a `#`.
Use `git reset -p` or `git reset; git add -p` to split the changes up in two or more commits.

The second line of the commit message should be empty.
If the changes are non-trivial you should add a few more lines explaining
why you have made these changes and why you have made the changes in this way.
If you add the hash of the commit where a bug or TODO flag was added
git-viewer will show the fixing commit in the details view of the flawed commit.
The flawed commit is usually easy to find with `gitl -G '<modified-code>'`
or `gitl -L <linenumber>,+1:<filename>`. A line for the commit message
can easily be copied with `yank "bugfix for type id"`.
I recommend using the full hash instead of a short hash because the number
of characters required to unambiguously identify a commit increases as the repository grows.

git notes are not quite trivial if you want to push them to a remote.
I recommend to create an empty commit instead and write the note into the commit message: `git commit --allow-empty`.

You can push the current branch with `git push`
and a new tag with `git push --tags`.
