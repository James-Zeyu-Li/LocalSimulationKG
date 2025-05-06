# activateTerraform/tfManager.py
import subprocess
import sys
import os


class TfManager:
    TF_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../terraform"))

    @staticmethod
    def ensure_infra(script_path: str = "./initTerra.sh") -> None:
        try:
            subprocess.run([script_path], check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(f"[TF ERROR] init infra failed: {e}")
