# Student Instructions

Use this tool when your instructor tells you to restore write access to a GitHub
Classroom repository.

## What The Tool Does

The tool checks whether your GitHub username is on your instructor's approved
list. If it is, the tool asks GitHub to restore write access to the matching
Classroom repository for the selected assignment.

It does not change your GitHub password, create a new GitHub account, or enroll
you in the course roster.

## Enter Your GitHub Username

Enter your GitHub username exactly as it appears on GitHub. Capitalization does
not matter; the tool normalizes usernames to lowercase.

Use only the username, not your profile URL.

Example:

```text
octocat
```

## Select An Assignment

Choose the assignment your instructor told you to fix. The assignment list comes
from GitHub Classroom assignment data synced by the instructor.

## Success Messages

A success message means GitHub accepted the request. Depending on your current
access, GitHub may either create a new invitation or confirm that write access is
already active.

If GitHub creates an invitation, check your GitHub notifications and email.

## Failure Messages

`Invalid GitHub username` means the username has characters GitHub does not
allow, is too long, or starts or ends with a hyphen.

`This GitHub username is not on the approved access list` means the username is
not currently in your instructor's whitelist.

`Invalid assignment` means the selected assignment is not available in this
tool's assignment list.

Other errors usually mean the tool could not update GitHub. Contact your
instructor with your GitHub username and assignment name.

## If Your Username Is Not Authorized

Contact your instructor. Include:

- Your GitHub username
- The assignment name
- The repository link, if you have one

The instructor must update the whitelist before the tool can restore your
access.
