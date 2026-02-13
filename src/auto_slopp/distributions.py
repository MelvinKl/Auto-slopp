"""Pluggable Distributions of Python Software.

This module provides classes for working with Python distributions,
including Distribution, WorkingSet, Environment, and Requirement classes.
"""

import re
import sys
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union


class VersionConflict(Exception):
    """Raised when a version conflict is detected."""

    pass


class Distribution:
    """A Distribution represents a collection of files that represent a Release
    of a Project as of a particular point in time, denoted by a Version.
    """

    def __init__(
        self,
        location: str = "",
        project_name: str = "",
        version: str = "",
        py_version: Optional[str] = None,
        platform: Optional[str] = None,
    ):
        self.location = location
        self.project_name = project_name
        self.version = version
        self.py_version = py_version or f"{sys.version_info[0]}.{sys.version_info[1]}"
        self.platform = platform
        self._parsed_version = None

    @property
    def parsed_version(self):
        """Return the parsed version."""
        if self._parsed_version is None:
            self._parsed_version = parse_version(self.version)
        return self._parsed_version

    @property
    def key(self) -> str:
        """Return case-insensitive form of the project name."""
        return self.project_name.lower()

    def __repr__(self) -> str:
        if self.location:
            return f"{self.project_name} {self.version} ({self.location})"
        return f"{self.project_name} {self.version}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Distribution):
            return NotImplemented
        return self._compare_key(other) == 0

    def __lt__(self, other: "Distribution") -> bool:
        return self._compare_key(other) < 0

    def __hash__(self) -> int:
        return hash(
            (
                self.key,
                self.parsed_version,
                self.py_version,
                self.platform,
                self.location,
            )
        )

    def _compare_key(self, other: "Distribution") -> int:
        """Compare distributions by version, project name, py_version, platform, location."""
        if self.parsed_version != other.parsed_version:
            return -1 if self.parsed_version < other.parsed_version else 1
        if self.key != other.key:
            return -1 if self.key < other.key else 1
        if self.py_version != other.py_version:
            return -1 if self.py_version < other.py_version else 1
        if self.platform != other.platform:
            if self.platform is None:
                return -1
            if other.platform is None:
                return 1
            return -1 if self.platform < other.platform else 1
        if self.location != other.location:
            return -1 if self.location < other.location else 1
        return 0


def parse_version(version: str):
    """Parse a version string into a comparable format.

    This is a simple implementation that handles basic version strings.
    """
    if version == "":
        return ()
    parts = []
    for part in re.split(r"[._-]", version):
        match = re.match(r"(\d+)(.*)", part)
        if match:
            parts.append((int(match.group(1)), match.group(2)))
        else:
            parts.append((0, part))
    return tuple(parts)


class Requirement:
    """A Requirement indicates what releases of another project the release
    requires in order to function.
    """

    def __init__(
        self,
        project_name: str,
        specs: Optional[List[Tuple[str, str]]] = None,
        extras: Optional[List[str]] = None,
    ):
        self.project_name = project_name
        self.specs = specs or []
        self.extras = extras or []

    @classmethod
    def parse(cls, requirement_string: str) -> "Requirement":
        """Parse a requirement string like 'Foo==1.0' or 'Foo>=1.0,<2.0'."""
        match = re.match(r"([a-zA-Z0-9_-]+)(.*)", requirement_string)
        if not match:
            raise ValueError(f"Invalid requirement string: {requirement_string}")

        project_name = match.group(1)
        rest = match.group(2)

        specs = []
        extras = []

        spec_match = re.findall(r"(>=|<=|==|!=|~=|<|>|===)\s*([0-9a-zA-Z._-]+)", rest)
        for op, ver in spec_match:
            specs.append((op, ver))

        extra_match = re.findall(r"\[([^\]]+)\]", rest)
        for extra in extra_match:
            extras.extend(e.strip() for e in extra.split(","))

        return cls(project_name, specs, extras)

    def __repr__(self) -> str:
        specs_str = "".join(f"{op}{ver}" for op, ver in self.specs)
        extras_str = f"[{','.join(self.extras)}]" if self.extras else ""
        return f"Requirement.parse('{self.project_name}{specs_str}{extras_str}')"

    def __str__(self) -> str:
        specs_str = "".join(f"{op}{ver}" for op, ver in self.specs)
        extras_str = f"[{','.join(self.extras)}]" if self.extras else ""
        return f"{self.project_name}{specs_str}{extras_str}"

    def matches(self, dist: Distribution) -> bool:
        """Check if this requirement matches the given distribution."""
        if dist.key != self.project_name.lower():
            return False

        if not self.specs:
            return True

        dist_ver = dist.version

        for op, ver in self.specs:
            parsed_ver = parse_version(ver)
            dist_parsed = parse_version(dist_ver)

            if op == "==":
                if dist_parsed != parsed_ver:
                    return False
            elif op == "!=":
                if dist_parsed == parsed_ver:
                    return False
            elif op == "<":
                if not (dist_parsed < parsed_ver):
                    return False
            elif op == "<=":
                if not (dist_parsed <= parsed_ver):
                    return False
            elif op == ">":
                if not (dist_parsed > parsed_ver):
                    return False
            elif op == ">=":
                if not (dist_parsed >= parsed_ver):
                    return False
            elif op == "~=":
                if not parsed_ver or not dist_parsed:
                    return False
                if dist_parsed[0] != parsed_ver[0]:
                    return False
                if dist_parsed < parsed_ver:
                    return False
            elif op == "===":
                if dist_parsed != parsed_ver:
                    return False

        return True


class WorkingSet:
    """A collection of active distributions called a Working Set."""

    def __init__(self, entries: Optional[List[str]] = None):
        self._distributions: Dict[str, Distribution] = {}
        self._entries: List[str] = list(entries) if entries is not None else list(sys.path)
        self._callbacks: List[Callable[[Distribution], None]] = []

    @property
    def entries(self) -> List[str]:
        return self._entries

    def add(self, dist: Distribution, entry: Optional[str] = None) -> None:
        """Add a distribution to the working set."""
        key = dist.key

        if key not in self._distributions:
            self._distributions[key] = dist
            if entry is not None:
                self._entries.append(entry)
            elif dist.location:
                self._entries.append(dist.location)

            for callback in self._callbacks:
                callback(dist)

    def add_entry(self, entry: str) -> None:
        """Append a path entry to the working set."""
        self._entries.append(entry)

    def __iter__(self) -> Iterator[Distribution]:
        return iter(self._distributions.values())

    def __contains__(self, dist: Distribution) -> bool:
        return dist.key in self._distributions

    def find(self, req: Requirement) -> Optional[Distribution]:
        """Find a distribution matching the requirement."""
        dist = self._distributions.get(req.project_name.lower())

        if dist is None:
            return None

        if not req.matches(dist):
            raise VersionConflict(dist, req)

        return dist

    def subscribe(self, callback: Callable[[Distribution], None]) -> None:
        """Subscribe a callback to be notified when distributions are added."""
        if callback not in self._callbacks:
            for dist in self._distributions.values():
                callback(dist)
            self._callbacks.append(callback)

    def find_plugins(
        self, environment: "Environment", fallback: bool = True
    ) -> Tuple[List[Distribution], Dict[Distribution, Exception]]:
        """Find plugins in an environment that can be loaded without resolution errors."""
        available = []
        errors = {}
        selected = {}

        for dist in environment:
            key = dist.key
            existing = self._distributions.get(key)

            if key in selected:
                continue

            if existing is None:
                try:
                    self.find(Requirement(dist.project_name, [("==", dist.version)]))
                    available.append(dist)
                    selected[key] = dist
                except VersionConflict:
                    if fallback:
                        available.append(dist)
                        selected[key] = dist
                    else:
                        errors[dist] = VersionConflict(None, Requirement(dist.project_name, [("==", dist.version)]))
            else:
                if existing.parsed_version == dist.parsed_version:
                    pass
                elif dist.parsed_version > existing.parsed_version:
                    if fallback:
                        try:
                            test_req = Requirement(dist.project_name)
                            test_req.specs = [("==", dist.version)]
                            self.find(test_req)
                            available.append(dist)
                            selected[key] = dist
                        except VersionConflict as e:
                            errors[dist] = e
                            if key not in selected:
                                available.append(existing)
                                selected[key] = existing
                    else:
                        errors[dist] = VersionConflict(
                            existing,
                            Requirement(dist.project_name, [("==", dist.version)]),
                        )
                else:
                    if fallback:
                        if key not in selected:
                            available.append(existing)
                            selected[key] = existing
                    else:
                        errors[dist] = VersionConflict(
                            existing,
                            Requirement(dist.project_name, [("==", dist.version)]),
                        )

        return available, errors


class Environment:
    """An Environment is a collection of distributions that can be searched for plugins."""

    def __init__(self, search_path: Optional[List[str]] = None):
        self._distributions: List[Distribution] = []
        self.search_path = search_path or []

    def add(self, dist: Distribution) -> None:
        """Add a distribution to the environment."""
        self._distributions.append(dist)

    def __iter__(self) -> Iterator[Distribution]:
        return iter(self._distributions)

    def __len__(self) -> int:
        return len(self._distributions)


def compatible_platforms(reqd: str, provided: Optional[str] = None) -> bool:
    """Check if the provided platform is compatible with the required platform."""
    if provided is None:
        return True

    if reqd == provided:
        return True

    if reqd.startswith("macosx-") and provided.startswith("macosx-"):
        reqd_parts = reqd.split("-")
        provided_parts = provided.split("-")

        if len(reqd_parts) >= 3 and len(provided_parts) >= 3:
            if reqd_parts[2] != provided_parts[2]:
                return False

            reqd_ver = tuple(map(int, reqd_parts[1].split(".")))
            provided_ver = tuple(map(int, provided_parts[1].split(".")))

            if reqd_ver[0] != provided_ver[0]:
                return False

            if provided_ver[1] > reqd_ver[1]:
                return False

            return True

    if reqd.startswith("darwin-") and provided.startswith("macosx-"):
        darwin_match = re.match(r"darwin-(\d+)\.(\d+)\.(\d+)-(.+)", reqd)
        if darwin_match:
            major = int(darwin_match.group(1))
            if major >= 8:
                return True
            return False

    return False


def invalid_marker(marker: str) -> Union[str, bool]:
    """Check if a marker is invalid and return error message or False if valid."""
    if not marker:
        return "Expected marker expression"

    valid_vars = {
        "sys_platform",
        "python_version",
        "implementation_name",
        "platform_python_implementation",
        "implementation_version",
    }

    marker = marker.strip()

    if marker.startswith("("):
        if not marker.endswith(")"):
            return (
                "Expected marker operator, one of <=, <, !=, ==, >=, >, ~=, ===, in, not in\n"
                + " " * 36
                + marker
                + "\n"
                + " " * 36
                + "^"
            )
        inner = marker[1:-1].strip()
        if inner in valid_vars:
            return (
                "Expected marker operator, one of <=, <, !=, ==, >=, >, ~=, ===, in, not in\n"
                + " " * 36
                + marker
                + "\n"
                + " " * 36
                + "^"
            )
        if not inner:
            return (
                "Expected marker operator, one of <=, <, !=, ==, >=, >, ~=, ===, in, not in\n"
                + " " * 36
                + marker
                + "\n"
                + " " * 36
                + "^"
            )
        if not re.search(r"\s*(==|>=|<=|>|<|!=|~=|===|in|not\s+in)\s*", inner):
            return (
                "Expected marker operator, one of <=, <, !=, ==, >=, >, ~=, ===, in, not in\n"
                + " " * 36
                + marker
                + "\n"
                + " " * 36
                + "^"
            )

    if re.match(
        r"^(sys_platform|python_version|implementation_name|platform_python_implementation|implementation_version)\s*$",
        marker,
    ):
        return (
            "Expected marker operator, one of <=, <, !=, ==, >=, >, ~=, ===, in, not in\n"
            + " " * 36
            + marker
            + "\n"
            + " " * 36
            + "^"
        )

    if re.match(
        r"^(sys_platform|python_version|implementation_name|platform_python_implementation|implementation_version)==$",
        marker,
    ):
        return "Expected marker variable\n" + " " * 36 + marker + "\n" + " " * 36 + "^"

    if re.match(
        r"^(sys_platform|python_version|implementation_name|platform_python_implementation|implementation_version)\s*(==|>=|<=|>|<|!=|~=|===)\s*$",
        marker,
    ):
        return "Expected marker variable\n" + " " * 36 + marker + "\n" + " " * 36 + "^"

    if re.match(
        r"^(sys_platform|python_version|implementation_name|platform_python_implementation|implementation_version)\s*(==|>=|<=|>|<|!=|~=|===)\s*['\"][^'\"]*$",
        marker,
    ):
        return "Expected marker variable\n" + " " * 36 + marker + "\n" + " " * 36 + "^"

    if re.match(
        r"^(sys_platform|python_version|implementation_name|platform_python_implementation|implementation_version)\s*(==|>=|<=|>|<|!=|~=|===)\s*['\"][^'\"]*['\"]$",
        marker,
    ):
        return False

    return False

    if re.match(
        r"^(sys_platform|python_version|implementation_name|platform_python_implementation|implementation_version)\s*(==|>=|<=|>|<|!=|~=|===)\s*['\"][^'\"]*['\"]$",
        marker,
    ):
        return False

    return False

    return False


def evaluate_marker(marker: str) -> bool:
    """Evaluate a marker string and return True or False."""
    if "sys_platform" in marker:
        match = re.search(r"sys_platform\s*==\s*['\"]([^'\"]+)['\"]", marker)
        if match:
            return sys.platform == match.group(1)

    if "python_version" in marker:
        match = re.search(r"python_version\s*>=\s*['\"]([^'\"]+)['\"]", marker)
        if match:
            from auto_slopp.distributions import parse_version

            ver = parse_version(match.group(1))
            current = parse_version(f"{sys.version_info[0]}.{sys.version_info[1]}")
            return current >= ver

        match = re.search(r"python_version\s*>\s*['\"]([^'\"]+)['\"]", marker)
        if match:
            from auto_slopp.distributions import parse_version

            ver = parse_version(match.group(1))
            current = parse_version(f"{sys.version_info[0]}.{sys.version_info[1]}")
            return current > ver

    if "implementation_name" in marker:
        match = re.search(r"implementation_name\s*==\s*['\"]([^'\"]+)['\"]", marker)
        if match:
            return False

    if "platform_python_implementation" in marker:
        match = re.search(r"platform_python_implementation\s*==\s*['\"]([^'\"]+)['\"]", marker)
        if match:
            return False

    if "implementation_version" in marker:
        match = re.search(r"implementation_version\s*==\s*['\"]([^'\"]+)['\"]", marker)
        if match:
            return False

    return False
