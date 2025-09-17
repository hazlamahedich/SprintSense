#!/bin/bash

# SprintSense Deployment Utilities
# Fixed git command for deployment tracking

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Fixed function to get deployment-related commits and files
get_deploy_commits_and_files() {
    local limit=${1:-10}
    local search_term=${2:-"deploy"}

    print_status "Getting last $limit commits containing '$search_term' with changed files..."

    # FIXED: Use --pretty=format instead of --oneline with --name-only
    git --no-pager log --grep="$search_term" -"$limit" --pretty=format:"%h %s" --name-only

    if [ $? -eq 0 ]; then
        print_success "Successfully retrieved deployment-related commits and files"
    else
        print_error "Failed to retrieve deployment commits"
        return 1
    fi
}

# Alternative method: Get commits and files separately (safer approach)
get_deploy_commits_safe() {
    local limit=${1:-10}
    local search_term=${2:-"deploy"}

    print_status "Getting deployment-related commits (safe method)..."

    # First get the commit hashes
    local commit_hashes=$(git --no-pager log --grep="$search_term" -"$limit" --pretty=format:"%H")

    if [ -z "$commit_hashes" ]; then
        print_warning "No commits found matching '$search_term'"
        return 0
    fi

    echo "Recent deployment commits:"
    git --no-pager log --grep="$search_term" -"$limit" --oneline

    echo ""
    echo "Files changed in these commits:"
    for hash in $commit_hashes; do
        echo "Files in commit $hash:"
        git --no-pager show --name-only --pretty=format:"" "$hash" | grep -v '^$' | sed 's/^/  /'
        echo ""
    done
}

# Function to get deployment stats
get_deploy_stats() {
    print_status "Deployment Statistics"

    echo "Total deployment-related commits:"
    git --no-pager log --grep="deploy" --oneline | wc -l | sed 's/^[ \t]*//'

    echo "Last 5 deployment commits:"
    git --no-pager log --grep="deploy" -5 --oneline

    echo "Deployment activity by author:"
    git --no-pager log --grep="deploy" --pretty=format:"%an" | sort | uniq -c | sort -rn
}

# Function to validate git repository state
check_git_state() {
    print_status "Checking Git repository state..."

    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a Git repository"
        return 1
    fi

    if ! git diff --quiet; then
        print_warning "Uncommitted changes detected"
        echo "Modified files:"
        git status --porcelain | sed 's/^/  /'
    else
        print_success "Working directory is clean"
    fi

    local current_branch=$(git symbolic-ref --short HEAD)
    print_status "Current branch: $current_branch"

    # Check if we're ahead/behind remote
    if git remote -v | grep -q origin; then
        local ahead_behind=$(git rev-list --left-right --count origin/"$current_branch"..."$current_branch" 2>/dev/null || echo "0	0")
        local behind=$(echo "$ahead_behind" | cut -f1)
        local ahead=$(echo "$ahead_behind" | cut -f2)

        if [ "$behind" != "0" ]; then
            print_warning "Your branch is $behind commits behind origin/$current_branch"
        fi

        if [ "$ahead" != "0" ]; then
            print_warning "Your branch is $ahead commits ahead of origin/$current_branch"
        fi

        if [ "$behind" = "0" ] && [ "$ahead" = "0" ]; then
            print_success "Branch is up to date with origin/$current_branch"
        fi
    else
        print_warning "No remote 'origin' configured"
    fi
}

# Main function
main() {
    case "${1:-help}" in
        "commits-and-files"|"cf")
            get_deploy_commits_and_files "${2:-10}" "${3:-deploy}"
            ;;
        "commits-safe"|"cs")
            get_deploy_commits_safe "${2:-10}" "${3:-deploy}"
            ;;
        "stats"|"s")
            get_deploy_stats
            ;;
        "check"|"c")
            check_git_state
            ;;
        "help"|"h"|*)
            echo -e "${GREEN}SprintSense Deployment Utilities${NC}"
            echo "================================"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  commits-and-files, cf [limit] [search]  - Get deploy commits with changed files (FIXED version)"
            echo "  commits-safe, cs [limit] [search]      - Get deploy commits safely (alternative method)"
            echo "  stats, s                               - Show deployment statistics"
            echo "  check, c                               - Check Git repository state"
            echo "  help, h                                - Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 commits-and-files 5 deploy         - Get last 5 deployment commits with files"
            echo "  $0 commits-safe 10 feat               - Safely get last 10 feature commits"
            echo "  $0 stats                               - Show deployment statistics"
            echo "  $0 check                               - Check repository state"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
