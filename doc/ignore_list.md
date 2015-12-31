ignore list
===========

## Introduction

___Ignore List___ is a feature that allows you to specify which files and directories to sync and
which not to sync.

## Usage

This section discusses how to write an ignore list file and tell `onedrive-d` to use it.

### Ignore List File

The default ignore list is stored as a file in `~/.onedrive/ignore_list_v4.txt`. You can add more
lists with `onedrive-pref` utility.

### Specify what to ignore

The rules follow [`.gitignore` format](http://git-scm.com/docs/gitignore) but with a few caveats.

Here is a quick reference guide:

__(0) Each line contains a single rule. Lines starting with '#' are comments.__

__(1) Rules are case-INsensitive to conform to NTFS naming rules.__

__(2) To ignore an item (i.e., either a file or a directory) called `foo` in ANY directory, add line:__

```bash
foo
```

__(3) To ignore a directory called `foo` in ANY directory, add line:__

```sh
foo/
```

___NOTE: all items under the directory will also be ignored and negation rule (see below) will NOT work.___

__(4) To ignore an item called `foo` in root, add line:__

```sh
/foo
```

__(5) To ignore an item called `foo` under directory `/Documents` (path relative to local OneDrive repository), add__

```sh
/Documents/foo
```

__(6) Use single wildcard `*` to match zero or more characters in that path. The matched part will not consist of more than one directory.__

```sh
# Ignore any files or directories whose names end with ".swp"
*.swp

# Ignore any files or directories in /Documents whose name end with ".swp"
/Documents/*.swp
# This rule is equivalent to "Documents/*.swp"
```

__(7) Use double stars `**` to mean "whatever can be matched".__

For example, the rule

```
/Documents/**/resume.txt
```

ignores all items called `resume.txt` under `/Documents` directory, such as `/Documents/resume.txt`, `/Documents/temp/resume.txt`, `/Documents/foo/bar/resume.txt`, etc.

__(8) When a rule contains any `/` except for `/` as the end character, it is automatically relative to root of local OneDrive repository.__

For example,

```sh
Documents/*.swp
```

is equivalent to

```sh
/Documents/*.swp
```

However, the rule

```sh
build/
```

matches any directory called `build` in OneDrive repository because the slash is at the end.

__(9) If you want to ignore anything inside, say `path-ignored/` directory, but want to keep a file called `keep` in it, use negation rule, which starts with an exclamation mark.__

```sh
path-ignored/**
!path-ignored/keep
```

This way, files like `/path-ignored/oops` will be ignored but `/path-ignored/keep` will NOT.

Note that if you have a rule to ignore the directory `path-ignored/`, then `onedrive-d` will NOT touch anything in that directory, and therefore, in this case the rule `!path-ignored/keep` will not take effect.

__(10) For files starting with a hashtag `#`, instead of writing a rule like, say, '\#test' (`.gitignore` format), write it like__

```sh
[#]test
```
This is where ignore list differs from `.gitignore` (probably because of [this bug](https://github.com/zb3/zgitignore/issues/2)).

Also note that if the line starts with a `#`, it will be ignored as comments.

__(11) You can also embed regular expressions in the rule via `{}`. You can use `\}` to pass `}` to regex and `\\` to pass `\`.__

For example,

```sh
# the following rule can match "aaa1256oobbii888"
aaa{12(34|56|78)oo(aa|bb|dd)ii}888

# the following rule can match "aaa#00ffff888"
aaa{#[0-9a-f]{3,6\}}888
```

Read [this document](https://github.com/zb3/zgitignore) for more about this feature.

__(12) You may want to have a look at the ignore list used for testing `onedrive-d`, which is at
`onedrive_d/tests/data/ignore_list.txt`.__

## License

The source code locates at `onedrive_d.common.path_filter` and the unit test is in
`tests.common.test_path_filter`. It is based on
[zgitignore](https://github.com/zb3/zgitignore) library under MIT license.
