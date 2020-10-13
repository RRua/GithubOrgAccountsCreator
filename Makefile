
CONFIG_JSON_FILE="config.json"
LOCAL_REPOS="local_repos"

install:
	@command -v curl >/dev/null 2>&1 || { echo >&2 "I require curl but it's not installed.  Aborting. Please install curl first"; exit 1; }
	@command -v git >/dev/null 2>&1 || { echo >&2 "I require git but it's not installed.  Aborting. Please install git first"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo >&2 "I require python3 but it's not installed.  Aborting. Please install python3 first"; exit 1; }

createAllRepos:
	python3 src/GithubCreator.py -create $(CONFIG_JSON_FILE)

pullAllRepos:
	python3 src/GithubCreator.py -pull $(CONFIG_JSON_FILE)

deleteAllRepos:
	python3 src/GithubCreator.py -delete $(CONFIG_JSON_FILE)

clean:
	@echo "vou apagar $(LOCAL_REPOS)"