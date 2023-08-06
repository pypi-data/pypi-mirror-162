# AWS Profile Utility

The `awsprofile` utility can be used to simplify working with a large number of profiles. This utility reads from `~/.aws/credentials` and `~/.aws/awsprofile` to list profiles.

## Install

```bash
pip install xawsprofile
```

## Usage

```bash
# list profiles
awsprofile list

# set profile to profile1 and set alias
eval $(awsprofile set profile1 --alias p1)

# list regions
awsprofile list-regions
```

## Bash Completion

This utility includes the following bash completions:

### Select Profile

`ap` (aws profile) - `ap {TAB}{TAB}` then select a profile, hit `{ENTER}`

```bash
$ ap prof{TAB}{TAB}
profile1     profile2
```

### Select Region

`ar` (aws region) - `ar {TAB}{TAB}`, then select a region, hit `{ENTER}`

```bash
$ ar us-{TAB}{TAB}
us-east-1     us-west-1
```

### Setup Bash Completion

```bash
# add to your .bash_profile
eval "$(awsprofile completion bash)"
```

## Commands

### List Profiles

`list` - list profiles

```bash
$ awsprofile list
profile1
profile2
```

### Set Profile

`set` - set the current profile using exported environment variables

```bash
$ eval(awsprofile set profile1)

# set profile and set alias
$ eval(awsprofile set profile1 --alias p1)
```

### Get Profile

`get` - get the full profile name

```bash
$ awsprofile get profile1
company-A-profile1
```

### List Regions

`list-regions` - list AWS regions

### Configure

`config` - configure awsprofiles

This currently supports `cwd` to configure the current working directory with a filter.

```bash
# filter only profiles-* and remove `profiles-` prefix
awsprofile config cwd --match 'profiles-(.*)`
```

### Console

`console` - open AWS console using the current/specified profile

```bash
awsprofile set profile1
awsprofile console

# or

awsprofile console --profile-name profile1
```

### Locate CWD File

`locate-cwd-file` - locate the `.awsprofile` used by traversing up from the current working directory

## Customizations

### Aliases

To set an alias, update `~/.aws/awsprofile` or use `awsprofile set ... --alias ...` or use `ap {profile} {alias}`.

```bash
eval $(awsprofile set profile1 --alias p1)

ap profile1 p1
```

### Bash Prompt

If you prefer to update your prompt to display the current AWS profile and region as an interactive prompt, you can update your `PS1` as follows:

```bash
export OLDPS1=$PS1
export PS1='${AWS_PROFILE} (${AWS_DEFAULT_REGION})> '
```

You can reset your prompt after by either running `export PS1=$OLDPS1` to reset the change, or by reloading your shell.

### Naming Rules

To simplify the profile names, rules can be applied when `awsprofile list` is run.

* global: ~/.aws/awsprofile
* working directory: {workdir}/.awsprofile (this overrides anything in global, as well as traverse up the directory tree to locate the `.awsprofile` file)

```text
# rename blah-* by removing "blah-" (ex: blah-test would be just test)
[naming cleanup-blah]
match = blah-(.*)
replace = \1

# hide test-*
[naming hide-test]
match = test-(.*)
visible = false

# hide all but test-*
[naming hide-others]
match = test-(.*)
negate = true
visible = false

# only applies to {workdir}/.awsprofile
[naming]
inherit_global = true
```

### Tips

#### Rules

* `awsprofile config cwd --match 'profiles-(.*)` will setup the current working directory to filter only `profiles-*` as well as strip `profiles-` from the profile names. This generates a `.awsprofile` in the current working directory.

* `awsprofile config cwd-rule --name filter1 --match 'some-prefix-(.*)'`: remove `some-prefix-` from all profiles

#### EKS KubeConfig

Add a kubeconfig context using `aws eks update-kubeconfig` with a name of `{PROFILE_ALIAS}/{CLUSTER_NAME}`

```bash
# add to ~/.zshrc
eval "$(awsprofile completion zsh)"

function akc {
  PROFILE=$1
  CLUSTER_NAME=$2
  FULL_PROFILE=$(awsprofile get $PROFILE)
  aws eks update-kubeconfig --profile $FULL_PROFILE --name $CLUSTER_NAME --alias "$PROFILE/$CLUSTER_NAME"
}

complete -F _awsprofile akc

# usage
akc profile1 eks-cluster-A
```
