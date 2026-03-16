"""Tests for Docker configuration and image."""

import subprocess
from pathlib import Path

import pytest


class TestDockerfileExists:
    """Test that Dockerfile exists and has correct structure."""

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists in project root."""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile should exist in project root"
        assert dockerfile_path.is_file(), "Dockerfile should be a file"

    def test_dockerfile_not_empty(self):
        """Test that Dockerfile is not empty."""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        content = dockerfile_path.read_text()
        assert len(content) > 0, "Dockerfile should not be empty"
        assert len(content.strip()) > 0, "Dockerfile should not be only whitespace"


class TestDockerignoreExists:
    """Test that .dockerignore exists and has proper exclusions."""

    def test_dockerignore_exists(self):
        """Test that .dockerignore exists in project root."""
        dockerignore_path = Path(__file__).parent.parent / ".dockerignore"
        assert dockerignore_path.exists(), ".dockerignore should exist in project root"
        assert dockerignore_path.is_file(), ".dockerignore should be a file"

    def test_dockerignore_excludes_venv(self):
        """Test that .dockerignore excludes .venv directory."""
        dockerignore_path = Path(__file__).parent.parent / ".dockerignore"
        content = dockerignore_path.read_text()
        assert ".venv" in content, ".dockerignore should exclude .venv directory"

    def test_dockerignore_excludes_git(self):
        """Test that .dockerignore excludes .git directory."""
        dockerignore_path = Path(__file__).parent.parent / ".dockerignore"
        content = dockerignore_path.read_text()
        assert ".git" in content, ".dockerignore should exclude .git directory"

    def test_dockerignore_excludes_tests(self):
        """Test that .dockerignore excludes tests directory."""
        dockerignore_path = Path(__file__).parent.parent / ".dockerignore"
        content = dockerignore_path.read_text()
        assert "tests/" in content, ".dockerignore should exclude tests directory"


class TestDockerfileContent:
    """Test Dockerfile content and structure."""

    @pytest.fixture
    def dockerfile_content(self):
        """Load Dockerfile content."""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        return dockerfile_path.read_text()

    def test_dockerfile_has_from_instruction(self, dockerfile_content):
        """Test that Dockerfile has FROM instruction."""
        assert "FROM" in dockerfile_content, "Dockerfile should have FROM instruction"

    def test_dockerfile_uses_python_base(self, dockerfile_content):
        """Test that Dockerfile uses Python base image."""
        assert "python" in dockerfile_content.lower(), "Dockerfile should use Python base image"

    def test_dockerfile_installs_git(self, dockerfile_content):
        """Test that Dockerfile installs git."""
        assert "git" in dockerfile_content, "Dockerfile should install git"

    def test_dockerfile_installs_uv(self, dockerfile_content):
        """Test that Dockerfile installs uv package manager."""
        assert "uv" in dockerfile_content, "Dockerfile should install uv package manager"

    def test_dockerfile_sets_workdir(self, dockerfile_content):
        """Test that Dockerfile sets working directory."""
        assert "WORKDIR" in dockerfile_content, "Dockerfile should set WORKDIR"

    def test_dockerfile_copies_source(self, dockerfile_content):
        """Test that Dockerfile copies source code."""
        assert "COPY" in dockerfile_content, "Dockerfile should have COPY instruction"
        assert "src/" in dockerfile_content, "Dockerfile should copy src/ directory"

    def test_dockerfile_has_entrypoint(self, dockerfile_content):
        """Test that Dockerfile has ENTRYPOINT."""
        assert "ENTRYPOINT" in dockerfile_content, "Dockerfile should have ENTRYPOINT"

    def test_dockerfile_sets_volume(self, dockerfile_content):
        """Test that Dockerfile sets VOLUME for repos."""
        assert "VOLUME" in dockerfile_content, "Dockerfile should set VOLUME"
        assert "/repos" in dockerfile_content, "Dockerfile should set /repos volume"

    def test_dockerfile_sets_env_repo_path(self, dockerfile_content):
        """Test that Dockerfile sets AUTO_SLOPP_BASE_REPO_PATH env var."""
        assert (
            "AUTO_SLOPP_BASE_REPO_PATH" in dockerfile_content
        ), "Dockerfile should set AUTO_SLOPP_BASE_REPO_PATH environment variable"


class TestDockerBuild:
    """Test Docker image building (integration tests)."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_docker_image_builds_successfully(self):
        """Test that Docker image builds without errors."""
        result = subprocess.run(
            ["docker", "build", "-t", "auto-slopp:test", "."],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, f"Docker build failed: {result.stderr}"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_docker_image_exists_after_build(self):
        """Test that Docker image exists after building."""
        subprocess.run(
            ["docker", "build", "-t", "auto-slopp:test", "."],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            timeout=300,
        )

        result = subprocess.run(
            ["docker", "images", "-q", "auto-slopp:test"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Failed to list Docker images"
        assert len(result.stdout.strip()) > 0, "Docker image should exist after build"


class TestDockerRun:
    """Test Docker container execution (integration tests)."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_docker_container_shows_help(self):
        """Test that Docker container can show help message."""
        subprocess.run(
            ["docker", "build", "-t", "auto-slopp:test", "."],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            timeout=300,
        )

        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "auto-slopp:test",
                "--help",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Docker container failed to run: {result.stderr}"
        assert (
            "auto-slopp" in result.stdout.lower() or "usage" in result.stdout.lower()
        ), "Container should show help message"
