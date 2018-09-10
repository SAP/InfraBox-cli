# New CLI Usage
## Remotes management

__Get remotes list__:
```sh
$ infrabox remotes list
```

__Login to some remote, e.g. http://exampleremote.com__:
```sh
$ infrabox login http://exampleremote.com
```
You will be asked to enter email and password then.
You can also optionally pass these as parameters `--email`, `--password`

If log in procedure succeeded, the remote will be set as current, meaning all further commands will be performed in that remote's context. 

__Logout from current remote__:
```sh
$ infrabox logout
```
This action will delete current remote's token from local config.

## Configuration
__Set current project__:
```sh
$ infrabox config set-current-project PROJECT_NAME
```
If project name was a valid one, all further commands will be performed in that project's context.

__You can also specify non-current project name for any project command to perform the command in another project's context, e.g.__:
Get collaborators list of project named _ANOTHER_PROJECT_NAME_:
```sh
$ infrabox project --project-name ANOTHER_PROJECT_NAME collaborators list
```


## Project
### * General project management
__Get project list__
```sh
$ infrabox project list
```

__Create new project__:
Available project types:
- upload;
- github (WIP);
- gerrit (WIP);

Available visibility options:
- -\-private
- -\-public

E.g.: Create private project named "PrivateUploadProject" of _upload_ type
```sh
$ infrabox project create --name PrivateUploadProject --type upload --private
```
__Delete a project__:
By name:
```sh
$ infrabox project delete --name PROJECT_NAME
```
By id:
```sh
$ infrabox project delete --id PROJECT_ID
```

### * Collaborators
__Get collaborators list__:
```sh
$ infrabox project collaborators list
```
__Add a collaborator__:
```sh
$ infrabox project collaborators add --username USERNAME
```
__Remove a collaborator__:
```sh
$ infrabox project collaborators remove --username USERNAME
```

### * Secrets
__Get secrets list__:
```sh
$ infrabox project secrets list
```
__Create a new secret__:
```sh
$ infrabox project secrets create --name SECRET_NAME --value SECRET_VALUE
```
__Delete a secret__:
By name:
```sh
$ infrabox project secrets delete --name SECRET_NAME
```
By id:
```sh
$ infrabox project secrets delete --id SECRET_ID
```

### * Project tokens
__Get tokens list__:
```sh
$ infrabox project tokens list
```
__Create a new token__:
```sh
$ infrabox project tokens create --description DESCRIPTION
```
__Delete a token__:
By description:
```sh
$ infrabox project tokens delete --description DESCRIPTION
```
By id:
```sh
$ infrabox project tokens delete --id TOKEN_ID
```
