from __future__ import annotations
import subprocess, re, logging
from .format import SubprocessError, FOREGROUND_RED

logger = logging.getLogger(__name__)

def get_git_tags(points_at: str = None, pattern: str = None) -> list[str]:
    """
    Get list of defined tags.
    Use points_at="HEAD" for tags pointing on last commit.
    """
    cmd = ['git', 'tag', '--list']
    if points_at:
        cmd.append("--points-at")
        cmd.append(points_at)
    if pattern:
        cmd.append(pattern)

    cp = subprocess.run(cmd, check=True, text=True, capture_output=True)
    tags = cp.stdout.strip()
    if not tags:
        return []
    
    return tags.splitlines()


def get_git_hash(ref: str = None) -> None|str:
    """
    Get commit hash of a reference (branch, tag, etc).
    Use ref="HEAD" for last commit and ref=None for last commit only if there is no changes.
    """
    cmd = ['git', 'rev-list', '-n', '1', ref if ref else "HEAD"]

    cp = subprocess.run(cmd, text=True, capture_output=True)
    if cp.returncode == 128:
        return None
    elif cp.returncode != 0:
        raise SubprocessError(cp)

    hash = cp.stdout.strip()
    if not ref:
        cp = subprocess.run(['git', 'status', '--porcelain'], text=True, capture_output=True)
        if cp.returncode != 0:
            raise SubprocessError(cp)
        if cp.stdout:
            return f"changes[{hash}]"

    return hash


def check_git_version_tags(version: str) -> bool:
    if not version:
        raise AttributeError("version: empty")
    
    ok = True

    # Check version
    if not re.match(r"^\d+\.\d+\.\d+(?:\-[a-z0-9\-]+)?$", version):
        logger.error(f"version \"{version}\" does not match required regex")
        ok = False

    # Compare version with git tags
    tags = get_git_tags(pattern="v*")
    if not tags or not f"v{version}" in tags:
        logger.error(f"tag v{version} not found")
        ok = False
    else:
        # Ensure corresponding version tag matches current hash
        tag_hash = get_git_hash(f"v{version}")
        if tag_hash:
            current_hash = get_git_hash()
            if tag_hash != current_hash:
                logger.error(f"version tag (v{version}) hash: {FOREGROUND_RED % tag_hash}, current hash: {FOREGROUND_RED % current_hash}")
            ok = False

    return ok
