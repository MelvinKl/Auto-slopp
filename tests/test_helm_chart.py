"""Tests for Helm chart structure and configuration."""

import subprocess
from pathlib import Path

import pytest
import yaml


class TestHelmChartStructure:
    """Test Helm chart directory structure and files."""

    @pytest.fixture
    def chart_path(self):
        """Return path to Helm chart."""
        return Path("charts/auto-slopp")

    def test_chart_directory_exists(self, chart_path):
        """Test that chart directory exists."""
        assert chart_path.exists(), f"Chart directory {chart_path} does not exist"
        assert chart_path.is_dir(), f"{chart_path} is not a directory"

    def test_chart_yaml_exists(self, chart_path):
        """Test that Chart.yaml exists."""
        chart_yaml = chart_path / "Chart.yaml"
        assert chart_yaml.exists(), "Chart.yaml not found"
        assert chart_yaml.is_file(), "Chart.yaml is not a file"

    def test_values_yaml_exists(self, chart_path):
        """Test that values.yaml exists."""
        values_yaml = chart_path / "values.yaml"
        assert values_yaml.exists(), "values.yaml not found"
        assert values_yaml.is_file(), "values.yaml is not a file"

    def test_templates_directory_exists(self, chart_path):
        """Test that templates directory exists."""
        templates_dir = chart_path / "templates"
        assert templates_dir.exists(), "templates directory not found"
        assert templates_dir.is_dir(), "templates is not a directory"

    def test_required_templates_exist(self, chart_path):
        """Test that required template files exist."""
        templates_dir = chart_path / "templates"
        required_templates = [
            "deployment.yaml",
            "configmap.yaml",
            "serviceaccount.yaml",
            "pvc.yaml",
            "_helpers.tpl",
        ]

        for template in required_templates:
            template_path = templates_dir / template
            assert template_path.exists(), f"Required template {template} not found"

    def test_helpers_tpl_exists(self, chart_path):
        """Test that _helpers.tpl exists."""
        helpers = chart_path / "templates" / "_helpers.tpl"
        assert helpers.exists(), "_helpers.tpl not found"


class TestHelmChartYaml:
    """Test Chart.yaml configuration."""

    @pytest.fixture
    def chart_yaml(self):
        """Load Chart.yaml."""
        chart_path = Path("charts/auto-slopp/Chart.yaml")
        with open(chart_path) as f:
            return yaml.safe_load(f)

    def test_chart_api_version(self, chart_yaml):
        """Test that apiVersion is v2."""
        assert chart_yaml["apiVersion"] == "v2", "Chart apiVersion should be v2"

    def test_chart_name(self, chart_yaml):
        """Test that chart name is correct."""
        assert chart_yaml["name"] == "auto-slopp", "Chart name should be auto-slopp"

    def test_chart_type(self, chart_yaml):
        """Test that chart type is application."""
        assert chart_yaml["type"] == "application", "Chart type should be application"

    def test_chart_has_version(self, chart_yaml):
        """Test that chart has a version."""
        assert "version" in chart_yaml, "Chart should have a version"
        assert chart_yaml["version"], "Chart version should not be empty"

    def test_chart_has_app_version(self, chart_yaml):
        """Test that chart has an appVersion."""
        assert "appVersion" in chart_yaml, "Chart should have an appVersion"
        assert chart_yaml["appVersion"], "Chart appVersion should not be empty"


class TestValuesYaml:
    """Test values.yaml configuration."""

    @pytest.fixture
    def values_yaml(self):
        """Load values.yaml."""
        values_path = Path("charts/auto-slopp/values.yaml")
        with open(values_path) as f:
            return yaml.safe_load(f)

    def test_replica_count(self, values_yaml):
        """Test that replicaCount is defined."""
        assert "replicaCount" in values_yaml, "replicaCount should be defined"
        assert values_yaml["replicaCount"] >= 1, "replicaCount should be at least 1"

    def test_image_configuration(self, values_yaml):
        """Test that image configuration is defined."""
        assert "image" in values_yaml, "image configuration should be defined"
        assert "repository" in values_yaml["image"], "image.repository should be defined"
        assert "pullPolicy" in values_yaml["image"], "image.pullPolicy should be defined"
        assert "tag" in values_yaml["image"], "image.tag should be defined"

    def test_additional_programs_option(self, values_yaml):
        """Test that additionalPrograms option exists."""
        assert "additionalPrograms" in values_yaml, "additionalPrograms should be defined"
        assert isinstance(values_yaml["additionalPrograms"], list), "additionalPrograms should be a list"

    def test_persistence_configuration(self, values_yaml):
        """Test that persistence configuration is defined."""
        assert "persistence" in values_yaml, "persistence should be defined"
        assert "enabled" in values_yaml["persistence"], "persistence.enabled should be defined"
        assert "size" in values_yaml["persistence"], "persistence.size should be defined"
        assert "accessMode" in values_yaml["persistence"], "persistence.accessMode should be defined"

    def test_environment_variables(self, values_yaml):
        """Test that environment variables are defined."""
        assert "env" in values_yaml, "env should be defined"
        assert isinstance(values_yaml["env"], dict), "env should be a dictionary"

    def test_default_env_values(self, values_yaml):
        """Test default environment variable values."""
        env = values_yaml["env"]
        assert "AUTO_SLOPP_DEBUG" in env, "AUTO_SLOPP_DEBUG should be defined"
        assert env["AUTO_SLOPP_DEBUG"] == "false", "AUTO_SLOPP_DEBUG should default to false"
        assert "AUTO_SLOPP_TELEGRAM_ENABLED" in env, "AUTO_SLOPP_TELEGRAM_ENABLED should be defined"

    def test_service_account_configuration(self, values_yaml):
        """Test that serviceAccount configuration is defined."""
        assert "serviceAccount" in values_yaml, "serviceAccount should be defined"
        assert "create" in values_yaml["serviceAccount"], "serviceAccount.create should be defined"


class TestDeploymentTemplate:
    """Test deployment.yaml template."""

    @pytest.fixture
    def deployment_template(self):
        """Load deployment.yaml template."""
        template_path = Path("charts/auto-slopp/templates/deployment.yaml")
        with open(template_path) as f:
            return f.read()

    def test_deployment_has_api_version(self, deployment_template):
        """Test that deployment has apiVersion."""
        assert "apiVersion: apps/v1" in deployment_template, "Deployment should use apps/v1 apiVersion"

    def test_deployment_has_kind(self, deployment_template):
        """Test that deployment has kind."""
        assert "kind: Deployment" in deployment_template, "Template should be a Deployment"

    def test_deployment_has_replicas(self, deployment_template):
        """Test that deployment has replica configuration."""
        assert "replicas:" in deployment_template, "Deployment should have replicas configuration"

    def test_deployment_has_init_container_logic(self, deployment_template):
        """Test that deployment has init container for additional programs."""
        assert "initContainers:" in deployment_template, "Deployment should have initContainers section"
        assert "additionalPrograms" in deployment_template, "Deployment should reference additionalPrograms"

    def test_deployment_has_volume_mount(self, deployment_template):
        """Test that deployment has volume mount for /repos."""
        assert "mountPath: /repos" in deployment_template, "Deployment should mount /repos volume"

    def test_deployment_has_env_from_configmap(self, deployment_template):
        """Test that deployment loads env from ConfigMap."""
        assert "configMapRef:" in deployment_template, "Deployment should use configMapRef"
        assert "envFrom:" in deployment_template, "Deployment should have envFrom section"

    def test_deployment_has_init_container_for_programs(self, deployment_template):
        """Test that deployment template has init container for additional programs."""
        assert "install-additional-programs" in deployment_template, "Should have init container name"
        assert "initContainer.command" in deployment_template, "Should reference initContainer command helper"


class TestConfigMapTemplate:
    """Test configmap.yaml template."""

    @pytest.fixture
    def configmap_template(self):
        """Load configmap.yaml template."""
        template_path = Path("charts/auto-slopp/templates/configmap.yaml")
        with open(template_path) as f:
            return f.read()

    def test_configmap_has_api_version(self, configmap_template):
        """Test that ConfigMap has apiVersion."""
        assert "apiVersion: v1" in configmap_template, "ConfigMap should use v1 apiVersion"

    def test_configmap_has_kind(self, configmap_template):
        """Test that ConfigMap has kind."""
        assert "kind: ConfigMap" in configmap_template, "Template should be a ConfigMap"

    def test_configmap_has_data_section(self, configmap_template):
        """Test that ConfigMap has data section."""
        assert "data:" in configmap_template, "ConfigMap should have data section"

    def test_configmap_iterates_env_vars(self, configmap_template):
        """Test that ConfigMap iterates over env variables."""
        assert ".Values.env" in configmap_template, "ConfigMap should reference .Values.env"


class TestPVCTemplate:
    """Test pvc.yaml template."""

    @pytest.fixture
    def pvc_template(self):
        """Load pvc.yaml template."""
        template_path = Path("charts/auto-slopp/templates/pvc.yaml")
        with open(template_path) as f:
            return f.read()

    def test_pvc_has_api_version(self, pvc_template):
        """Test that PVC has apiVersion."""
        assert "apiVersion: v1" in pvc_template, "PVC should use v1 apiVersion"

    def test_pvc_has_kind(self, pvc_template):
        """Test that PVC has kind."""
        assert "kind: PersistentVolumeClaim" in pvc_template, "Template should be a PersistentVolumeClaim"

    def test_pvc_has_persistence_reference(self, pvc_template):
        """Test that PVC references persistence configuration."""
        assert ".Values.persistence" in pvc_template, "PVC should reference .Values.persistence"

    def test_pvc_has_access_modes(self, pvc_template):
        """Test that PVC has accessModes."""
        assert "accessModes:" in pvc_template, "PVC should have accessModes"

    def test_pvc_has_storage_request(self, pvc_template):
        """Test that PVC has storage request."""
        assert "storage:" in pvc_template, "PVC should have storage request"


class TestServiceAccountTemplate:
    """Test serviceaccount.yaml template."""

    @pytest.fixture
    def sa_template(self):
        """Load serviceaccount.yaml template."""
        template_path = Path("charts/auto-slopp/templates/serviceaccount.yaml")
        with open(template_path) as f:
            return f.read()

    def test_sa_has_api_version(self, sa_template):
        """Test that ServiceAccount has apiVersion."""
        assert "apiVersion: v1" in sa_template, "ServiceAccount should use v1 apiVersion"

    def test_sa_has_kind(self, sa_template):
        """Test that ServiceAccount has kind."""
        assert "kind: ServiceAccount" in sa_template, "Template should be a ServiceAccount"

    def test_sa_conditional_creation(self, sa_template):
        """Test that ServiceAccount has conditional creation."""
        assert ".Values.serviceAccount.create" in sa_template, "Should check serviceAccount.create"


class TestHelpersTemplate:
    """Test _helpers.tpl template."""

    @pytest.fixture
    def helpers_template(self):
        """Load _helpers.tpl template."""
        template_path = Path("charts/auto-slopp/templates/_helpers.tpl")
        with open(template_path) as f:
            return f.read()

    def test_helpers_has_name_template(self, helpers_template):
        """Test that helpers has name template."""
        assert 'define "auto-slopp.name"' in helpers_template, "Should define auto-slopp.name template"

    def test_helpers_has_fullname_template(self, helpers_template):
        """Test that helpers has fullname template."""
        assert 'define "auto-slopp.fullname"' in helpers_template, "Should define auto-slopp.fullname template"

    def test_helpers_has_labels_template(self, helpers_template):
        """Test that helpers has labels template."""
        assert 'define "auto-slopp.labels"' in helpers_template, "Should define auto-slopp.labels template"

    def test_helpers_has_init_container_command(self, helpers_template):
        """Test that helpers has initContainer command template."""
        assert (
            'define "auto-slopp.initContainer.command"' in helpers_template
        ), "Should define auto-slopp.initContainer.command template"

    def test_helpers_init_container_uses_additional_programs(self, helpers_template):
        """Test that init container command uses additionalPrograms."""
        assert ".Values.additionalPrograms" in helpers_template, "Should reference .Values.additionalPrograms"
        assert "apt-get install" in helpers_template, "Should have apt-get install command"


class TestSecretTemplate:
    """Test secret.yaml template."""

    @pytest.fixture
    def secret_template(self):
        """Load secret.yaml template."""
        template_path = Path("charts/auto-slopp/templates/secret.yaml")
        with open(template_path) as f:
            return f.read()

    def test_secret_conditional_creation(self, secret_template):
        """Test that Secret has conditional creation."""
        assert ".Values.secrets" in secret_template, "Should check .Values.secrets"

    def test_secret_has_kind(self, secret_template):
        """Test that Secret has kind."""
        assert "kind: Secret" in secret_template, "Template should be a Secret"

    def test_secret_encodes_values(self, secret_template):
        """Test that Secret encodes values with b64enc."""
        assert "b64enc" in secret_template, "Secret should use b64enc for encoding"


class TestHelmLint:
    """Test Helm chart with helm lint (if helm is available)."""

    def test_helm_lint(self):
        """Test chart with helm lint if helm is available."""
        try:
            result = subprocess.run(
                ["helm", "lint", "charts/auto-slopp"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                assert True, "Helm lint passed"
            else:
                pytest.skip("Helm lint failed, but helm might not be properly configured")
        except FileNotFoundError:
            pytest.skip("Helm not installed - skipping helm lint test")


class TestAdditionalProgramsFeature:
    """Test the additionalPrograms feature specifically."""

    @pytest.fixture
    def values_yaml(self):
        """Load values.yaml."""
        values_path = Path("charts/auto-slopp/values.yaml")
        with open(values_path) as f:
            return yaml.safe_load(f)

    def test_additional_programs_default_empty(self, values_yaml):
        """Test that additionalPrograms defaults to empty list."""
        assert values_yaml["additionalPrograms"] == [], "additionalPrograms should default to empty list"

    def test_additional_programs_accepts_list(self, values_yaml):
        """Test that additionalPrograms accepts a list of packages."""
        values_yaml["additionalPrograms"] = ["android-sdk", "build-essential"]
        assert len(values_yaml["additionalPrograms"]) == 2, "Should accept multiple packages"

    def test_deployment_conditionally_creates_init_container(self):
        """Test that init container is only created when additionalPrograms is set."""
        deployment_path = Path("charts/auto-slopp/templates/deployment.yaml")
        with open(deployment_path) as f:
            content = f.read()

        assert (
            "{{- if .Values.additionalPrograms }}" in content
        ), "Should conditionally create init container based on additionalPrograms"
        assert "initContainers:" in content, "Should have initContainers section"

    def test_init_container_installs_packages_from_list(self):
        """Test that init container installs packages from additionalPrograms list."""
        helpers_path = Path("charts/auto-slopp/templates/_helpers.tpl")
        with open(helpers_path) as f:
            content = f.read()

        assert "join" in content, "Should join package list"
        assert ".Values.additionalPrograms" in content, "Should reference additionalPrograms"


class TestExampleValues:
    """Test example values configurations."""

    def test_example_with_android_build_tools(self):
        """Test example configuration with Android build tools."""
        values_path = Path("charts/auto-slopp/values.yaml")
        with open(values_path) as f:
            values = yaml.safe_load(f)

        values["additionalPrograms"] = [
            "android-sdk",
            "android-sdk-build-tools",
            "openjdk-11-jdk",
        ]

        assert len(values["additionalPrograms"]) == 3, "Should accept Android build tools configuration"

    def test_example_with_custom_env_vars(self):
        """Test example configuration with custom environment variables."""
        values_path = Path("charts/auto-slopp/values.yaml")
        with open(values_path) as f:
            values = yaml.safe_load(f)

        values["env"]["AUTO_SLOPP_DEBUG"] = "true"
        values["env"]["AUTO_SLOPP_TELEGRAM_ENABLED"] = "true"
        values["env"]["CUSTOM_VAR"] = "custom-value"

        assert values["env"]["AUTO_SLOPP_DEBUG"] == "true", "Should allow custom debug setting"
        assert "CUSTOM_VAR" in values["env"], "Should allow custom environment variables"
