"""
Push complaints.db to the GitHub data branch.
Called by sync_and_push.bat after each sync.
"""
import subprocess
import os
import sys
import tempfile
import shutil
import datetime

REPO_URL = "https://github.com/Anthonyooo0/MAC_Quality_Dashboard.git"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "complaints.db")


def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed (exit {result.returncode}): {' '.join(cmd)}")
    return result


def push():
    if not os.path.exists(DB_PATH):
        print("[ERROR] complaints.db not found")
        sys.exit(1)

    size = os.path.getsize(DB_PATH)
    print(f"[INFO] Pushing database ({size:,} bytes) to GitHub...")

    tmpdir = tempfile.mkdtemp(prefix="mac_push_")
    try:
        # Try to clone existing data branch
        result = run(
            ["git", "clone", "--depth", "1", "--branch", "data", REPO_URL, tmpdir],
            check=False
        )

        if result.returncode != 0:
            # Data branch doesn't exist yet — create it
            print("[INFO] Data branch not found, creating it...")
            run(["git", "init"], cwd=tmpdir)
            run(["git", "remote", "add", "origin", REPO_URL], cwd=tmpdir)
            run(["git", "checkout", "--orphan", "data"], cwd=tmpdir)

        # Copy the database
        shutil.copy2(DB_PATH, os.path.join(tmpdir, "complaints.db"))

        run(["git", "add", "complaints.db"], cwd=tmpdir)

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        run([
            "git", "-c", "user.email=sync@macproducts.net", "-c", "user.name=MAC Sync",
            "commit", "-m", f"Update complaints database {ts}"
        ], cwd=tmpdir)

        run(["git", "push", "origin", "data", "--force"], cwd=tmpdir)

        print("[OK] Successfully pushed to GitHub data branch")

    except Exception as e:
        print(f"[ERROR] Push failed: {e}")
        sys.exit(1)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    push()
