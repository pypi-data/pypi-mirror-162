from __future__ import annotations
import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path
from .format import SubprocessError
from .network import determine_proxy_url

def download_gpg_key(keyid: str, target_path: Path, keyserver: str = None):
    with TemporaryDirectory() as tmpdir:
        # Retrieve the key
        cmd = ["gpg", "--homedir", tmpdir]
        
        if keyserver:
            cmd += ["--keyserver", keyserver]
            
            if keyserver.startswith("hkp://"):
                proxy_url = determine_proxy_url(keyserver)
                if proxy_url:
                    cmd += ["--keyserver-options", f"http-proxy={proxy_url}"]

        cmd += ["--recv-keys", keyid]
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Export the key
        cmd = ["gpg", "--homedir", tmpdir, "--output", target_path, "--export", keyid]
        subprocess.run(cmd, capture_output=True, text=True, check=True)

def verify_gpg_signature(sign_path: Path, public_key_path: Path):
    cmd = ["gpg", "--no-default-keyring", "--keyring", public_key_path, "--verify", sign_path]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    if cp.returncode != 0:
        raise SubprocessError(cp)
