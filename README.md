# Github Organization Accounts Creator

Created to simplify and automate the process of creating multiple repositories for an organization that share the same structure.
It allows creating, extracting information (pull) and deleting repositories from an organization account. In order to create the repositories, the program uses a CSV file with the ID of the groups to be created and data on the members of each repository. 

An example CSV input file was included with the program (StudentsSample.csv). The file presented results from the export to CSV format of a form placed in Google Drive that aimed to collect the data of the participants of each project to be created (example of such form at: https://drive.google.com/file/d/1aIKQNFgKTwg8HNp_7u3V6tcncACPS11s/view?usp=sharing). The header column names are subject to change but their order must be maintained for the program to work correctly. The members listed in each group will be invited to join the private repository that was created and the README.md file in the root of the project will have the identification of each group element.

## Usage scenarios:

- Create/mantain base projects for students of a Course;
- Create/mantain base projects for code competitions;

## Setup
First, an organizational account must be created for this purpose. Then, the user must generate an oauth token (with at least the following scopes: repo, admin:org and delete_repos) to communicate with the github API and create the repositories automatically (https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token). The organization ID and the generated token must be placed in the config.json file, which program uses to function properly.

The program will replicate the structure placed in the directory contained in the variable "repos_structure_model" for all repositories. This directory and its variable can be changed for any repository structure that the user wants to replicate.

the config.json configuration file must contain the following information:

```
{
	"input_csv": "StudentsSample.csv", -> name of the input csv
	"input_csv_delimeter": ";", -> csv delimiter
	"oauth_token": "<my-auth-token>", -> generated ouath token
	"org_name": "<my-org-id>", -> organization name. e.g li3-2020
	"group_repo_name_pattern": "group%s", -> pattern of the name that will be given to each repository. leave it that way to genarate repos with name "group<groupid>"
	"repo_structure_model": "repo_model", -> the model directory that will be replicated for each repository
	"repos_folder": "local_repos" -> a folder to receive a local copy of each repository created
}		
```

## RUN

In order to execute the program, use the Makefile contained in the project to carry out the main functionalities of the program:


### Create one instance repository (testing purposes)
```
$ make createRepoInstance
```

### Create repositories
```
$ make createAllRepos
```

### Pull repositories
```
$ make pullAllRepos
```

### Delete repositories
```
$ make deleteAllRepos
```

