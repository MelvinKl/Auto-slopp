"""Tests for the NodeenvWorker."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from auto_slopp.workers.nodeenv_worker import NodeenvWorker


class TestNodeenvWorker(unittest.TestCase):
    """Test cases for NodeenvWorker."""

    def setUp(self):
        """Set up test fixtures."""
        self.worker = NodeenvWorker(
            node_version="18.17.0",
            env_name="test-nodeenv",
            force_recreate=True,
        )
        self.temp_dir = Path(tempfile.mkdtemp())
        self.repo_path = self.temp_dir / "test-repo"
        self.repo_path.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test worker initialization."""
        worker = NodeenvWorker()
        self.assertIsNone(worker.node_version)
        self.assertIsNone(worker.npm_version)
        self.assertEqual(worker.env_name, "nodeenv")
        self.assertFalse(worker.force_recreate)

        worker = NodeenvWorker(
            node_version="18.0.0",
            npm_version="8.0.0",
            env_name="custom-env",
            force_recreate=True,
        )
        self.assertEqual(worker.node_version, "18.0.0")
        self.assertEqual(worker.npm_version, "8.0.0")
        self.assertEqual(worker.env_name, "custom-env")
        self.assertTrue(worker.force_recreate)

    def test_get_env_directory_with_task_path(self):
        """Test environment directory resolution with task path."""
        task_path = self.temp_dir / "task"
        task_path.mkdir()

        env_dir = self.worker._get_env_directory(self.repo_path, task_path)
        self.assertEqual(env_dir, task_path / self.worker.env_name)

    def test_get_env_directory_with_file_task_path(self):
        """Test environment directory resolution with file task path."""
        task_file = self.temp_dir / "task.txt"
        task_file.write_text("test")

        env_dir = self.worker._get_env_directory(self.repo_path, task_file)
        self.assertEqual(env_dir, self.repo_path / self.worker.env_name)

    def test_detect_platform(self):
        """Test platform detection."""
        platform = self.worker._detect_platform()
        self.assertIn(platform, ["darwin", "linux", "win"])

    def test_detect_architecture(self):
        """Test architecture detection."""
        arch = self.worker._detect_architecture()
        self.assertIn(arch, ["x64", "arm64", "armv7l"])

    @patch("auto_slopp.workers.nodeenv_worker.urllib.request.urlopen")
    def test_get_latest_lts_version_success(self, mock_urlopen):
        """Test successful LTS version fetch."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"""
        [
            {"version": "v20.5.0", "lts": false},
            {"version": "v18.17.0", "lts": "Hydrogen", "security": false},
            {"version": "v16.20.1", "lts": "Gallium"}
        ]
        """
        mock_urlopen.return_value.__enter__.return_value = mock_response

        version = self.worker._get_latest_lts_version()
        self.assertEqual(version, "18.17.0")

    @patch("auto_slopp.workers.nodeenv_worker.urllib.request.urlopen")
    def test_get_latest_lts_version_failure(self, mock_urlopen):
        """Test LTS version fetch failure fallback."""
        mock_urlopen.side_effect = Exception("Network error")

        version = self.worker._get_latest_lts_version()
        self.assertEqual(version, "18.17.0")

    def test_create_activation_scripts(self):
        """Test creation of activation scripts."""
        env_dir = self.temp_dir / "test-env"
        env_dir.mkdir()
        (env_dir / "bin").mkdir()

        self.worker._create_activation_scripts(env_dir)

        activate_script = env_dir / "bin" / "activate"
        self.assertTrue(activate_script.exists())
        content = activate_script.read_text()
        self.assertIn("source", content)
        self.assertIn("deactivate ()", content)

        activate_bat = env_dir / "bin" / "activate.bat"
        self.assertTrue(activate_bat.exists())

        activate_ps1 = env_dir / "bin" / "activate.ps1"
        self.assertTrue(activate_ps1.exists())

    @patch.object(NodeenvWorker, "_install_nodejs")
    @patch.object(NodeenvWorker, "_create_activation_scripts")
    @patch.object(NodeenvWorker, "_test_environment")
    @patch.object(NodeenvWorker, "_get_latest_lts_version")
    def test_create_node_environment_success(self, mock_lts, mock_test, mock_scripts, mock_install):
        """Test successful environment creation."""
        mock_lts.return_value = "18.17.0"
        mock_install.return_value = {"success": True, "version": "18.17.0"}
        mock_test.return_value = {"success": True, "node_version": "v18.17.0"}

        env_dir = self.repo_path / "nodeenv"
        result = self.worker._create_node_environment(env_dir)

        self.assertTrue(result["success"])
        self.assertEqual(result["env_dir"], str(env_dir))
        self.assertEqual(result["node_version"], "18.17.0")
        mock_install.assert_called_once()
        mock_scripts.assert_called_once()
        mock_test.assert_called_once()

    def test_create_node_environment_existing(self):
        """Test environment creation when directory exists."""
        worker = NodeenvWorker(force_recreate=False)
        env_dir = self.repo_path / "nodeenv"
        env_dir.mkdir()

        result = worker._create_node_environment(env_dir)

        self.assertTrue(result["success"])
        self.assertIn("already exists", result["messages"][-1])

    def test_create_node_environment_force_recreate(self):
        """Test environment recreation with force flag."""
        worker = NodeenvWorker(force_recreate=True)

        env_dir = self.repo_path / "nodeenv"
        env_dir.mkdir()

        with patch.object(worker, "_install_nodejs") as mock_install:
            with patch.object(worker, "_create_activation_scripts"):
                with patch.object(worker, "_test_environment") as mock_test:
                    with patch.object(worker, "_get_latest_lts_version") as mock_lts:
                        mock_lts.return_value = "18.17.0"
                        mock_install.return_value = {"success": True}
                        mock_test.return_value = {"success": True}

                        result = worker._create_node_environment(env_dir)

                        self.assertTrue(result["success"])
                        mock_install.assert_called_once()

    @patch("subprocess.run")
    def test_test_environment_success(self, mock_subprocess):
        """Test successful environment testing."""
        env_dir = self.temp_dir / "test-env"
        env_dir.mkdir()
        bin_dir = env_dir / "bin"
        bin_dir.mkdir()

        (bin_dir / "node").touch()
        (bin_dir / "npm").touch()

        mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="v18.17.0"),
            MagicMock(returncode=0, stdout="9.6.7"),
        ]

        result = self.worker._test_environment(env_dir)

        self.assertTrue(result["success"])
        self.assertEqual(result["node_version"], "v18.17.0")
        self.assertEqual(result["npm_version"], "9.6.7")

    @patch("subprocess.run")
    def test_test_environment_node_missing(self, mock_subprocess):
        """Test environment testing with missing node executable."""
        env_dir = self.temp_dir / "test-env"
        env_dir.mkdir()
        bin_dir = env_dir / "bin"
        bin_dir.mkdir()

        result = self.worker._test_environment(env_dir)

        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])

    @patch("subprocess.run")
    def test_test_environment_node_failure(self, mock_subprocess):
        """Test environment testing with node execution failure."""
        env_dir = self.temp_dir / "test-env"
        env_dir.mkdir()
        bin_dir = env_dir / "bin"
        bin_dir.mkdir()

        (bin_dir / "node").touch()

        mock_subprocess.return_value = MagicMock(returncode=1, stderr="Command failed")

        result = self.worker._test_environment(env_dir)

        self.assertFalse(result["success"])
        self.assertIn("failed", result["error"])


if __name__ == "__main__":
    unittest.main()
