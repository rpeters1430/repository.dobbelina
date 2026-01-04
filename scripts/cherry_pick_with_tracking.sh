#!/bin/bash
# cherry_pick_with_tracking.sh
#
# Cherry-pick a commit from upstream and automatically update UPSTREAM_SYNC.md

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SYNC_FILE="$REPO_ROOT/UPSTREAM_SYNC.md"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <upstream-commit-hash> [<upstream-commit-hash> ...]"
    echo ""
    echo "Example:"
    echo "  $0 7bbe1c7"
    echo "  $0 7bbe1c7 004f106 d92bd04"
    echo ""
    echo "This script will:"
    echo "  1. Cherry-pick the commit(s) with -x flag (adds source reference)"
    echo "  2. Prompt you to update UPSTREAM_SYNC.md"
    echo "  3. Run tests (optional)"
    exit 1
fi

echo "================================================"
echo "Cherry-Pick with Tracking"
echo "================================================"
echo ""

# Process each commit
for upstream_hash in "$@"; do
    echo "Processing: $upstream_hash"
    echo ""

    # Show the commit
    echo "--- Commit Details ---"
    git show --stat "$upstream_hash" | head -20
    echo ""

    # Confirm
    read -p "Cherry-pick this commit? (y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "⏭️  Skipped $upstream_hash"
        echo ""
        continue
    fi

    # Cherry-pick with -x flag
    echo "🍒 Cherry-picking $upstream_hash..."
    if git cherry-pick -x "$upstream_hash"; then
        echo "✅ Cherry-pick successful!"

        # Get the new commit hash in fork
        fork_hash=$(git log -1 --format="%h")
        commit_msg=$(git log -1 --format="%s")
        today=$(date +%Y-%m-%d)

        echo ""
        echo "--- New Fork Commit ---"
        echo "Fork Hash: $fork_hash"
        echo "Message: $commit_msg"
        echo ""

        # Prepare the new table entry
        new_entry="| \`$upstream_hash\` | $commit_msg | \`$fork_hash\` | $today | Cherry-picked with -x |"

        echo "📝 Add this entry to UPSTREAM_SYNC.md:"
        echo ""
        echo "$new_entry"
        echo ""

        read -p "Open UPSTREAM_SYNC.md for editing? (y/n) " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Try to open with common editors
            if command -v nano &> /dev/null; then
                nano "$SYNC_FILE"
            elif command -v vim &> /dev/null; then
                vim "$SYNC_FILE"
            elif command -v vi &> /dev/null; then
                vi "$SYNC_FILE"
            else
                echo "⚠️  No editor found. Please manually add the entry to $SYNC_FILE"
                echo "Entry to add:"
                echo "$new_entry"
            fi
        else
            echo "Remember to manually update $SYNC_FILE with:"
            echo "$new_entry"
        fi
    else
        echo "❌ Cherry-pick failed (likely conflicts)"
        echo ""
        echo "To resolve:"
        echo "  1. Fix conflicts in the affected files"
        echo "  2. git add <resolved-files>"
        echo "  3. git cherry-pick --continue"
        echo ""
        echo "Or abort with:"
        echo "  git cherry-pick --abort"
        exit 1
    fi

    echo ""
    echo "---"
    echo ""
done

echo "================================================"
echo "All Done!"
echo "================================================"
echo ""

read -p "Run tests now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Running tests..."
    cd "$REPO_ROOT"
    python run_tests.py
fi

echo ""
echo "✅ Complete! Don't forget to:"
echo "   1. Review UPSTREAM_SYNC.md"
echo "   2. Commit the tracking file if you updated it"
echo "   3. Push your changes"
echo ""
