#!/bin/bash
# check_upstream_sync.sh
#
# This script checks for new commits in the upstream repository and compares
# them with what's already integrated in the fork.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================"
echo "Upstream Sync Checker"
echo "================================================"
echo ""

# Check if upstream remote exists
if ! git remote | grep -q "^upstream$"; then
    echo "⚠️  Upstream remote not found. Adding it now..."
    git remote add upstream https://github.com/dobbelina/repository.dobbelina.git
    echo "✅ Upstream remote added"
fi

echo "🔄 Fetching latest commits from upstream..."
git fetch upstream --quiet

echo ""
echo "================================================"
echo "New Upstream Commits (excluding version bumps)"
echo "================================================"
echo ""

# Get new commits, excluding version bumps
new_commits=$(git log upstream/master --not origin/master --oneline --no-merges | grep -v "Bumped to v." || true)

if [ -z "$new_commits" ]; then
    echo "✅ Fork is up to date with upstream!"
    echo ""
    exit 0
fi

# Count new commits
count=$(echo "$new_commits" | wc -l)
echo "📊 Found $count new commits"
echo ""

# Display commits in a table format
echo "| Hash    | Commit Message"
echo "|---------|---------------"
echo "$new_commits" | while read hash message; do
    echo "| $hash | $message"
done

echo ""
echo "================================================"
echo "Integrated Commits Check"
echo "================================================"
echo ""

# Read already integrated commits from UPSTREAM_SYNC.md
if [ -f "$REPO_ROOT/UPSTREAM_SYNC.md" ]; then
    echo "Checking UPSTREAM_SYNC.md for already integrated commits..."
    echo ""

    integrated_count=0
    truly_new_count=0

    echo "$new_commits" | while read hash message; do
        if grep -q "$hash" "$REPO_ROOT/UPSTREAM_SYNC.md"; then
            echo "✅ $hash - Already tracked in UPSTREAM_SYNC.md"
            integrated_count=$((integrated_count + 1))
        else
            echo "🆕 $hash - NEW (not yet integrated)"
            truly_new_count=$((truly_new_count + 1))
        fi
    done
else
    echo "⚠️  UPSTREAM_SYNC.md not found. All commits shown are potentially new."
fi

echo ""
echo "================================================"
echo "Next Steps"
echo "================================================"
echo ""
echo "1. Review commits listed as 🆕 NEW above"
echo "2. For each commit you want to integrate:"
echo "   git cherry-pick -x <hash>"
echo ""
echo "3. After cherry-picking, update UPSTREAM_SYNC.md with:"
echo "   | \`<upstream-hash>\` | Message | \`<fork-hash>\` | $(date +%Y-%m-%d) | Cherry-picked with -x |"
echo ""
echo "4. Run tests:"
echo "   python run_tests.py"
echo ""
echo "For detailed analysis, see CHERRY_PICK_ANALYSIS.md"
echo ""
