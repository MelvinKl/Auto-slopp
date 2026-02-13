"""Node.js virtual environment worker for auto-slopp automation system.

This worker creates Node.js virtual environments similar to Python's virtualenv,
allowing for isolated Node.js and npm package management per project.
"""

import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from auto_slopp.worker import Worker


class NodeenvWorker(Worker):
    """Worker for creating and managing Node.js virtual environments.

    This worker provides functionality to:
    1. Create isolated Node.js environments
    2. Install specific Node.js versions
    3. Manage npm packages in isolation
    4. Provide activation/deactivation scripts
    """

    def __init__(
        self,
        node_version: Optional[str] = None,
        npm_version: Optional[str] = None,
        env_name: Optional[str] = None,
        force_recreate: bool = False,
    ):
        """Initialize the NodeenvWorker.

        Args:
            node_version: Specific Node.js version to install (e.g., "18.17.0")
            npm_version: Specific npm version to install (e.g., "9.6.7")
            env_name: Name for the virtual environment (defaults to "nodeenv")
            force_recreate: If True, recreate existing environment
        """
        self.node_version = node_version
        self.npm_version = npm_version
        self.env_name = env_name or "nodeenv"
        self.force_recreate = force_recreate
        self.logger = logging.getLogger("auto_slopp.workers.NodeenvWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute the Node.js virtual environment creation.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing execution results and environment info
        """
        import time

        start_time = time.time()
        self.logger.info(f"NodeenvWorker starting with repo_path: {repo_path}")

        env_dir = self._get_env_directory(repo_path, task_path)

        result = self._create_node_environment(env_dir)
        result["execution_time"] = time.time() - start_time
        result["timestamp"] = start_time
        result["repo_path"] = str(repo_path)
        result["task_path"] = str(task_path)
        result["worker_name"] = "NodeenvWorker"

        return result

    def _get_env_directory(self, repo_path: Path, task_path: Path) -> Path:
        """Determine the environment directory path.

        Args:
            repo_path: Repository path
            task_path: Task path

        Returns:
            Path where the node environment should be created
        """
        base_path = task_path if task_path.is_dir() else repo_path
        return base_path / self.env_name

    def _create_node_environment(self, env_dir: Path) -> Dict[str, Any]:
        """Create the Node.js virtual environment.

        Args:
            env_dir: Directory where environment should be created

        Returns:
            Dictionary with creation results
        """
        result = {
            "success": False,
            "env_dir": str(env_dir),
            "node_version": self.node_version,
            "npm_version": self.npm_version,
            "error": None,
            "messages": [],
        }

        try:
            if env_dir.exists():
                if self.force_recreate:
                    self.logger.info(f"Removing existing environment: {env_dir}")
                    shutil.rmtree(env_dir)
                    result["messages"].append(f"Removed existing environment: {env_dir}")
                else:
                    result["success"] = True
                    result["messages"].append(f"Environment already exists: {env_dir}")
                    return result

            env_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Creating Node.js environment in: {env_dir}")

            node_version = self.node_version or self._get_latest_lts_version()
            if not node_version:
                raise RuntimeError("Could not determine Node.js version to install")

            result["node_version"] = node_version

            node_info = self._install_nodejs(env_dir, node_version)
            result["node_installed"] = node_info

            self._create_activation_scripts(env_dir)
            result["messages"].append("Created activation scripts")

            test_result = self._test_environment(env_dir)
            result["test_result"] = test_result

            result["success"] = True
            result["messages"].append(f"Successfully created Node.js environment: {env_dir}")

        except Exception as e:
            result["error"] = str(e)
            result["messages"].append(f"Failed to create environment: {e}")
            self.logger.error(f"Failed to create Node.js environment: {e}")

        return result

    def _get_latest_lts_version(self) -> Optional[str]:
        """Get the latest LTS Node.js version from Node.js API.

        Returns:
            Latest LTS version string or None if failed
        """
        try:
            with urllib.request.urlopen("https://nodejs.org/dist/index.json", timeout=10) as response:  # nosec B310
                data = json.loads(response.read().decode())

                for release in data:
                    if release.get("lts") and not release.get("security"):
                        version = release["version"].lstrip("v")
                        self.logger.info(f"Using latest LTS Node.js version: {version}")
                        return version

        except Exception as e:
            self.logger.warning(f"Failed to fetch latest LTS version: {e}")

        return "18.17.0"

    def _install_nodejs(self, env_dir: Path, version: str) -> Dict[str, Any]:
        """Install Node.js in the environment directory.

        Args:
            env_dir: Environment directory
            version: Node.js version to install

        Returns:
            Dictionary with installation info
        """
        self.logger.info(f"Installing Node.js {version}")

        bin_dir = env_dir / "bin"
        bin_dir.mkdir(exist_ok=True)

        platform = self._detect_platform()
        arch = self._detect_architecture()

        filename = f"node-v{version}-{platform}-{arch}.tar.gz"
        download_url = f"https://nodejs.org/dist/v{version}/{filename}"

        temp_dir = Path(tempfile.mkdtemp())
        try:
            archive_path = temp_dir / filename
            self.logger.info(f"Downloading Node.js from: {download_url}")
            urllib.request.urlretrieve(download_url, archive_path)  # nosec B310

            extracted_dir = temp_dir / f"node-v{version}-{platform}-{arch}"
            shutil.unpack_archive(archive_path, temp_dir)

            node_source_dir = extracted_dir / "bin"
            for file_path in node_source_dir.glob("*"):
                shutil.copy2(file_path, bin_dir)

            lib_dir = env_dir / "lib"
            lib_dir.mkdir(exist_ok=True)
            shutil.copytree(extracted_dir / "lib" / "node_modules", lib_dir / "node_modules")

            include_dir = env_dir / "include"
            include_dir.mkdir(exist_ok=True)
            shutil.copytree(extracted_dir / "include" / "node", include_dir / "node")

            share_dir = env_dir / "share"
            share_dir.mkdir(exist_ok=True)
            shutil.copytree(extracted_dir / "share" / "man", share_dir / "man")

            return {
                "version": version,
                "platform": platform,
                "arch": arch,
                "bin_dir": str(bin_dir),
                "success": True,
            }

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _detect_platform(self) -> str:
        """Detect the current platform for Node.js binaries.

        Returns:
            Platform string for Node.js downloads
        """
        system = sys.platform.lower()
        if system == "darwin":
            return "darwin"
        elif system == "linux":
            return "linux"
        elif system == "win32":
            return "win"
        else:
            return "linux"

    def _detect_architecture(self) -> str:
        """Detect the current architecture for Node.js binaries.

        Returns:
            Architecture string for Node.js downloads
        """
        machine = os.uname().machine.lower() if hasattr(os, "uname") else "x64"

        if machine in ("x86_64", "amd64"):
            return "x64"
        elif machine in ("aarch64", "arm64"):
            return "arm64"
        elif machine.startswith("arm"):
            return "armv7l"
        else:
            return "x64"

    def _create_activation_scripts(self, env_dir: Path) -> None:
        """Create activation scripts for the environment.

        Args:
            env_dir: Environment directory
        """
        bin_dir = env_dir / "bin"

        activate_script = env_dir / "bin" / "activate"
        with activate_script.open("w") as f:
            f.write(f"""# Node.js virtual environment activation script
# Usage: source {env_dir}/bin/activate

_OLD_NODE_PATH="$PATH"

export PATH="{bin_dir}:$PATH"

export NODE_PATH="{env_dir}/lib/node_modules"

export NODE_ENV_ACTIVE="{env_dir}"

deactivate () {{
    export PATH="$_OLD_NODE_PATH"

    unset NODE_PATH
    unset NODE_ENV_ACTIVE
    unset _OLD_NODE_PATH

    if [ -n "$_OLD_NODE_PS1" ]; then
        export PS1="$_OLD_NODE_PS1"
        unset _OLD_NODE_PS1
    fi

    echo "Node.js virtual environment deactivated"
}}

_OLD_NODE_PS1="$PS1"
export PS1="(nodeenv) $PS1"

echo "Node.js virtual environment activated"
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
""")

        activate_script.chmod(0o755)

        activate_bat = env_dir / "bin" / "activate.bat"
        with activate_bat.open("w") as f:
            f.write(f"""@echo off
REM Node.js virtual environment activation script for Windows
REM Usage: {env_dir}\\bin\\activate.bat

set _OLD_NODE_PATH=%PATH%
set PATH={bin_dir};%PATH%
set NODE_PATH={env_dir}\\lib\\node_modules
set NODE_ENV_ACTIVE={env_dir}

echo Node.js virtual environment activated
node --version
npm --version
""")

        activate_ps1 = env_dir / "bin" / "activate.ps1"
        with activate_ps1.open("w") as f:
            f.write(f"""# Node.js virtual environment activation script for PowerShell
# Usage: . {env_dir}\\bin\\activate.ps1

$env:_OLD_NODE_PATH = $env:PATH
$env:PATH = "{bin_dir};" + $env:PATH
$env:NODE_PATH = "{env_dir}\\lib\\node_modules"
$env:NODE_ENV_ACTIVE = "{env_dir}"

Write-Host "Node.js virtual environment activated"
node --version
npm --version
""")

        for script in [activate_script, activate_bat, activate_ps1]:
            script.chmod(0o755)

    def _test_environment(self, env_dir: Path) -> Dict[str, Any]:
        """Test the created Node.js environment.

        Args:
            env_dir: Environment directory to test

        Returns:
            Dictionary with test results
        """
        test_result = {"success": False, "node_version": None, "npm_version": None}

        try:
            bin_dir = env_dir / "bin"
            node_exe = bin_dir / "node"
            npm_exe = bin_dir / "npm"

            if not node_exe.exists():
                raise RuntimeError("Node.js executable not found")

            result = subprocess.run(
                [str(node_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                test_result["node_version"] = result.stdout.strip()
            else:
                raise RuntimeError(f"Node.js version check failed: {result.stderr}")

            if npm_exe.exists():
                result = subprocess.run(
                    [str(npm_exe), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    test_result["npm_version"] = result.stdout.strip()

            test_result["success"] = True

        except Exception as e:
            test_result["error"] = str(e)

        return test_result
