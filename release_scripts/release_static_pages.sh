#!/bin/bash

# Release script for updated static_pages
# For every step, takes confirmation from the user before executing

set -e

confirm() {
    local msg="$1"
    echo ""
    echo ">>> $msg"
    read -p "Proceed? (y/n): " choice
    case "$choice" in
        y|Y ) return 0 ;;
        * ) echo "Skipped."; return 1 ;;
    esac
}

# Determine the repository directory
if [ -n "$RELEASE_REPO_LOCATION" ]; then
    echo "Found RELEASE_REPO_LOCATION environment variable: $RELEASE_REPO_LOCATION"
    read -p "Use this location? (y/n): " use_env
    if [ "$use_env" = "y" ] || [ "$use_env" = "Y" ]; then
        REPO_DIR="$RELEASE_REPO_LOCATION"
    else
        read -p "Enter the repository directory path: " REPO_DIR
    fi
else
    read -p "Enter the repository directory path: " REPO_DIR
fi
if [ ! -d "$REPO_DIR" ]; then
    echo "Error: Directory '$REPO_DIR' does not exist."
    exit 1
fi

# Ask for the hotfix branch name
read -p "Enter the hotfix branch name (e.g. 2015-02-03_1702_static_pages): " HOTFIX_NAME
if [ -z "$HOTFIX_NAME" ]; then
    echo "Error: Hotfix branch name cannot be empty."
    exit 1
fi

# cd to repository directory
if confirm "cd to repository directory: $REPO_DIR"; then
    cd "$REPO_DIR"
    echo "Changed to $(pwd)"
fi

# Checkout develop and pull
if confirm "git checkout develop"; then
    git checkout develop
fi

if confirm "git pull (develop)"; then
    git pull
fi

# Checkout master and pull
if confirm "git checkout master"; then
    git checkout master
fi

if confirm "git pull (master)"; then
    git pull
fi

# Start hotfix
if confirm "git flow hotfix start $HOTFIX_NAME"; then
    git flow hotfix start "$HOTFIX_NAME"
fi

# Checkout static_pages and pull
if confirm "git checkout static_pages"; then
    git checkout static_pages
fi

if confirm "git pull (static_pages)"; then
    git pull
fi

# Checkout hotfix branch and merge static_pages
if confirm "git checkout hotfix/$HOTFIX_NAME"; then
    git checkout "hotfix/$HOTFIX_NAME"
fi

if confirm "git merge static_pages into hotfix/$HOTFIX_NAME"; then
    git merge static_pages
fi

# Review latest commits
if confirm "Review latest commits in static_pages (git log -p static_pages -5)"; then
    git log -p static_pages -5
fi

# Show diff of files changed
if confirm "Show files changed: git diff master hotfix/$HOTFIX_NAME --name-only"; then
    git diff master "hotfix/$HOTFIX_NAME" --name-only
fi

# Check for JS/CSS changes and optionally update version
echo ""
echo ">>> Checking for JS or CSS file changes..."
JS_CSS_CHANGES=$(git diff master "hotfix/$HOTFIX_NAME" --name-only | grep -E '\.(js|css)$' || true)

if [ -n "$JS_CSS_CHANGES" ]; then
    echo "JS/CSS changes detected:"
    echo "$JS_CSS_CHANGES"
    echo ""
    echo "You need to update the version in setup.py and portality/settings.py"

    if confirm "Edit setup.py to update DOAJ_VERSION"; then
        ${EDITOR:-vi} setup.py
    fi

    if confirm "Edit portality/settings.py to update version"; then
        ${EDITOR:-vi} portality/settings.py
    fi

    if confirm "Commit version changes"; then
        git add setup.py portality/settings.py
        git commit -m "Update DOAJ_VERSION for static_pages hotfix"
    fi
else
    echo "No JS/CSS changes detected. Version update not required."
fi

# Finish hotfix
if confirm "git flow hotfix finish $HOTFIX_NAME"; then
    git flow hotfix finish "$HOTFIX_NAME"
fi

# Push develop
if confirm "git push (current branch)"; then
    git push
fi

# Checkout master and push
if confirm "git checkout master && git push"; then
    git checkout master
    git push
fi

# Push tags
if confirm "git push --tags"; then
    git push --tags
fi

echo ""
echo "=== Static pages hotfix release complete! ==="
echo ""
echo "####    from the doaj folder in the 'sysadmin' repo, run the command:"
echo "####    ansible-playbook -i doaj-hosts.ini update-site.yml"
echo ""
