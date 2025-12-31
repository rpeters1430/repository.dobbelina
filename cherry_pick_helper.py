#!/usr/bin/env python3
"""
Script to help cherry-pick upstream commits to fork.
Provides interactive commit selection and automated conflict handling.
"""

import subprocess
import sys
from typing import List, Tuple

# Define commit groups
COMMIT_GROUPS = {
    'phase1_critical': {
        'name': 'Phase 1: Critical Fixes',
        'commits': [
            ('673fe9b', 'fix module load error on TvOS #1724'),
            ('7bbe1c7', 'Fix video playback for FlareSolverr scraped sites'),
            ('3a98f37', 'Python 2 fixes #1722 fixes #1663'),
            ('fb3243d', 'fix python 2 compatibility #1663'),
            ('86946aa', 'chaturbate python 2 compatibiity fix'),
            ('24d0b16', 'Exceptionlogger Python 2.7 compatible'),
        ]
    },
    'phase2_popular_sites': {
        'name': 'Phase 2: Popular Site Fixes',
        'commits': [
            ('31644dc', 'pornhub fixes #1712'),
            ('0649955', 'pornhub categories - fixes #1664'),
            ('f3d48c1', 'xhmster playback'),
            ('ad3cfe5', 'xhamster fixes #1668'),
            ('c92e14e', 'xhamster: play h264 streams instead of av1'),
            ('7436c71', 'awmnet fix xhamster streams #1677'),
            ('e250c5d', 'hanime - fix playback fixes #1646'),
            ('273e27b', 'hanime fix favorites #1666'),
            ('86d995a', 'hanime fixes #1686'),
            ('60b6859', 'hanime playback - fixes #1688'),
            ('5069719', 'hentaihavenco - fix listing, playback #1644'),
            ('1e2417e', 'spankbang - fix listing #1643'),
            ('e96ed9b', 'stripchat - fix playback (SD only) fixes #1710'),
            ('6ee3883', 'Foxnxx & HQPorner playback fix'),
            ('58d28d9', 'foxnxx - fix playback fixes #1657'),
            ('cd0cc1c', 'foxnxx - fix playback fixes #1600'),
            ('efddcfe', 'foxnxx playback fixes #1629'),
        ]
    },
    'phase3_removals': {
        'name': 'Phase 3: Site Cleanup',
        'commits': [
            ('43c6322', 'americass - removed fixes #1709'),
            ('f4c5a43', 'iflix - removed'),
            ('b5ae7b6', 'bubba, cambro, yespornplease removed'),
            ('71d1398', 'vintagetube - removed'),
            ('abb53d8', 'ividz - removed'),
            ('8655ef5', 'asstoo & bitporno - removed'),
            ('da3a465', 'asianporn - removed'),
            ('24b5b73', 'amateurcool - removed'),
        ]
    },
    'phase4_new_sites': {
        'name': 'Phase 4: New Sites',
        'commits': [
            ('8eae561', 'fullxcinema'),
            ('122e955', 'freepornvideos - new site'),
            ('67bd60f', 'tokyomotion - new site'),
            ('ba754a5', 'xxdbx - new site'),
            ('8301e4d', '85po - new site'),
            ('4e2c8e0', 'premiumporn - new site'),
            ('750c731', 'Netflav - new site (JAV)'),
            ('464392c', 'PornTN - new site'),
        ]
    }
}


def run_command(cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Exit code: {result.returncode}")
        print(f"Stderr: {result.stderr}")
    return result.returncode, result.stdout, result.stderr


def check_upstream_remote():
    """Ensure upstream remote exists."""
    code, stdout, _ = run_command(['git', 'remote', '-v'], check=False)
    if 'upstream' not in stdout:
        print("Upstream remote not found. Adding it...")
        run_command([
            'git', 'remote', 'add', 'upstream',
            'https://github.com/dobbelina/repository.dobbelina.git'
        ])
        print("Fetching from upstream...")
        run_command(['git', 'fetch', 'upstream'])
    else:
        print("Upstream remote exists. Fetching latest...")
        run_command(['git', 'fetch', 'upstream'])


def show_commit_details(commit_sha: str):
    """Show commit details."""
    print(f"\n{'='*80}")
    code, stdout, _ = run_command(['git', 'show', '--stat', commit_sha], check=False)
    if code == 0:
        print(stdout[:2000])  # Show first 2000 chars
        if len(stdout) > 2000:
            print("... (truncated)")
    else:
        print(f"Could not fetch commit {commit_sha}")
    print('='*80)


def cherry_pick_commit(commit_sha: str, commit_msg: str) -> bool:
    """
    Cherry-pick a single commit.
    Returns True if successful, False if conflicts occurred.
    """
    print(f"\n🍒 Cherry-picking: {commit_sha} - {commit_msg}")
    
    code, stdout, stderr = run_command(['git', 'cherry-pick', commit_sha], check=False)
    
    if code == 0:
        print("✅ Successfully applied!")
        return True
    else:
        if 'conflict' in stderr.lower() or 'conflict' in stdout.lower():
            print("⚠️  CONFLICT detected!")
            print("\nConflicted files:")
            run_command(['git', 'status', '--short'])
            print("\nOptions:")
            print("  1. Resolve conflicts manually, then run: git add <files> && git cherry-pick --continue")
            print("  2. Skip this commit: git cherry-pick --skip")
            print("  3. Abort cherry-pick: git cherry-pick --abort")
            return False
        else:
            print(f"❌ Failed to apply commit: {stderr}")
            return False


def apply_phase(phase_key: str, interactive: bool = True):
    """Apply all commits in a phase."""
    phase = COMMIT_GROUPS[phase_key]
    print(f"\n{'='*80}")
    print(f"📦 {phase['name']}")
    print(f"{'='*80}")
    print(f"Total commits: {len(phase['commits'])}")
    
    if interactive:
        response = input("\nProceed with this phase? (y/n/q): ").lower()
        if response == 'q':
            return False
        if response != 'y':
            print("Skipping phase.")
            return True
    
    success_count = 0
    conflict_count = 0
    
    for sha, msg in phase['commits']:
        if interactive:
            print(f"\n📋 Next: {sha} - {msg}")
            response = input("Apply this commit? (y/n/d=details/s=skip phase/q=quit): ").lower()
            
            if response == 'q':
                return False
            elif response == 's':
                print("Skipping rest of phase.")
                break
            elif response == 'd':
                show_commit_details(sha)
                response = input("Apply this commit? (y/n): ").lower()
                if response != 'y':
                    print("Skipping commit.")
                    continue
            elif response != 'y':
                print("Skipping commit.")
                continue
        
        if cherry_pick_commit(sha, msg):
            success_count += 1
        else:
            conflict_count += 1
            if interactive:
                response = input("\nConflict occurred. Continue with next commit? (y/n): ").lower()
                if response != 'y':
                    print("Stopping phase due to conflict.")
                    break
            else:
                print("Stopping phase due to conflict.")
                break
    
    print(f"\n{'='*80}")
    print(f"Phase complete: {success_count} successful, {conflict_count} conflicts")
    print(f"{'='*80}")
    
    return True


def main():
    """Main function."""
    print("🍒 Upstream Commit Cherry-Pick Helper")
    print("="*80)
    
    # Check we're in the right directory
    code, _, _ = run_command(['git', 'rev-parse', '--git-dir'], check=False)
    if code != 0:
        print("Error: Not in a git repository!")
        sys.exit(1)
    
    # Check upstream remote
    check_upstream_remote()
    
    # Show current branch
    code, stdout, _ = run_command(['git', 'branch', '--show-current'])
    current_branch = stdout.strip()
    print(f"\nCurrent branch: {current_branch}")
    
    if current_branch != 'copilot/update-fork-with-commits':
        response = input(f"\nYou're on branch '{current_branch}'. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting.")
            sys.exit(0)
    
    # Show menu
    while True:
        print("\n" + "="*80)
        print("Select a phase to apply:")
        print("="*80)
        print("1. Phase 1: Critical Fixes (8 commits)")
        print("2. Phase 2: Popular Site Fixes (17 commits)")
        print("3. Phase 3: Site Cleanup/Removals (8 commits)")
        print("4. Phase 4: New Sites (8 commits)")
        print("5. Apply all phases sequentially")
        print("6. Show commit details for a specific SHA")
        print("q. Quit")
        
        choice = input("\nEnter choice: ").strip().lower()
        
        if choice == 'q':
            print("Exiting.")
            break
        elif choice == '1':
            if not apply_phase('phase1_critical'):
                break
        elif choice == '2':
            if not apply_phase('phase2_popular_sites'):
                break
        elif choice == '3':
            if not apply_phase('phase3_removals'):
                break
        elif choice == '4':
            if not apply_phase('phase4_new_sites'):
                break
        elif choice == '5':
            for phase_key in ['phase1_critical', 'phase2_popular_sites', 
                             'phase3_removals', 'phase4_new_sites']:
                if not apply_phase(phase_key):
                    break
        elif choice == '6':
            sha = input("Enter commit SHA: ").strip()
            show_commit_details(sha)
        else:
            print("Invalid choice.")
    
    print("\n✅ Done! Remember to:")
    print("  1. Run tests: python run_tests.py")
    print("  2. Test manually: 2-3 sites per phase")
    print("  3. Commit changes: git commit -m 'Applied upstream commits'")
    print("  4. Push: git push origin", current_branch)


if __name__ == '__main__':
    main()
