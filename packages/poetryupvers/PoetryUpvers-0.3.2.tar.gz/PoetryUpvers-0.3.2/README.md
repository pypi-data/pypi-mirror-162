# Automatic Semantic Versioning for Poetry

Handle automatically incrementing the version in your pyproject.toml

## Installation

```
pip install poetryupvers
```

## Upversion process

This package executes the following processes:
- open pyproject.toml and read version
- parse version into a semver-friendly format
- read the commit history of the repo from HEAD to the latest numeric tag
- searches for keyword matches in the commit messages compared to the content of the messages.json file
- if any keywords match with phrases defined the major, minor, or patch json objects, then the bump type will reflect major, minor, or patch
    - For example, if a commit message with "[BREAKING CHANGE]" is found in the history, the bump type will be major
- bump version based on version type determined
- update pyproject.toml file

## Usage

```
Usage:
    ppuv bump [--messages-file=<path>]
    ppuv push-bump [--config-user=<user>] [--config-email=<email>] [--remote=<remote>] [--branch=<branch>]
    ppuv generate-release-notes [--save] [--path=<path>]

Options:
    -h, --help      Show Usage.

Commands:
    bump                    Bump the version of the pyproject.toml file. 
                            This is based on specific keywords, defined in the messages.json file, 
                            found in commit messages ranging from HEAD to the last numeric tag
    
    push-bump               Commits the pyproject.toml file to the git repository.
                            Contains multiple options to run this command in a CI pipeline

    generate-release-notes  Generates release notes based on commits and related MRs in GitLab

Arguments:
    messages-file   Override the messages file JSON (text snippets denoting the version bump), 
                    if not using a local messages.json or installed messages.json
    save            Writes release notes to file (default path = ./release_notes.md)
    path            Override release notes file path
    config-user     Sets git user
    config-email    Sets git user email
    remote          Sets git remote name (ex: origin)
    branch          Sets git push branch
```

### Bump version with default configuration

```bash
ppuv bump
```

### Bump version with overriden messages.json

```bash
# If you have a messages.json defined directly at the root of your repository
ppuv bump

# If you have a different location for your messages.json (or a different filename)
ppuv bump --messages-file=<path-to-file>
```

### Example messages.json

```json
{
    "major": "[BREAKING CHANGE]",
    "minor": [
        "[New Feature]",
        "Add",
        "Update"
    ],
    "patch": [
        "[BUGFIX]",
        "Fix"
    ]
}
```

## Generate release notes (For GitLab only)

```bash
ppuv generate-release-notes
```

This process is dependent on the following environment variables being set:
- CI_PROJECT_ID: The ID of the project, should be available within a CI pipeline. 
    You will need to set this manually if you run this command outside of a GitLab CI pipeline
- CI_SERVER_URL: The base url of the GitLab instance itself (e.g https://gitlab.com). 
    Also should be available within a CI pipeline, but you will need to set it manually to run this script outside of a GitLab CI pipeline
- ACCESS_TOKEN: Personal access token or Project-level access token. 
    Used to interact with the GitLab API to retrieve the related MRs to the git commits. You will need to store this as a CI/CD variable

The process is the following:

- Grab a list of commit hashes between HEAD and the latest numeric tag
- Iterate over the hashes and send a request to 
    [`projects/{id}/repository/commits/{commit}/merge_requests`](https://docs.gitlab.com/ee/api/commits.html#list-merge-requests-associated-with-a-commit)
    to retrieve any related MRs to that commit
- Append the MR title and ID to an internal dictionary to prevent any duplicate entries
- Format each MR title and ID to a markdown bullet
- Print out release notes and write them to a file
