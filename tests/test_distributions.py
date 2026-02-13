"""Tests for distributions module."""

import sys

import pytest

from auto_slopp.distributions import (
    Distribution,
    Environment,
    Requirement,
    VersionConflict,
    WorkingSet,
    compatible_platforms,
    evaluate_marker,
    invalid_marker,
    parse_version,
)


class TestDistribution:
    def test_basic_creation(self):
        dist = Distribution(project_name="Foo", version="1.2")
        assert dist.project_name == "Foo"
        assert dist.version == "1.2"

    def test_repr(self):
        dist = Distribution(project_name="Foo", version="1.2")
        assert repr(dist) == "Foo 1.2"

    def test_repr_with_location(self):
        dist = Distribution(
            location="http://example.com/something",
            project_name="Bar",
            version="0.9",
        )
        assert "Bar 0.9" in repr(dist)
        assert "http://example.com/something" in repr(dist)

    def test_location_attribute(self):
        dist = Distribution(
            location="http://example.com/something",
            project_name="Bar",
            version="0.9",
        )
        assert dist.location == "http://example.com/something"

    def test_project_name_attribute(self):
        dist = Distribution(project_name="Bar", version="0.9")
        assert dist.project_name == "Bar"

    def test_version_attribute(self):
        dist = Distribution(project_name="Bar", version="0.9")
        assert dist.version == "0.9"

    def test_py_version_attribute(self):
        dist = Distribution(project_name="Bar", version="0.9")
        expected = f"{sys.version_info[0]}.{sys.version_info[1]}"
        assert dist.py_version == expected

    def test_platform_attribute(self):
        dist = Distribution(project_name="Bar", version="0.9")
        assert dist.platform is None

    def test_parsed_version(self):
        from auto_slopp.distributions import parse_version

        dist = Distribution(project_name="Bar", version="0.9")
        assert dist.parsed_version == parse_version(dist.version)

    def test_key_case_insensitive(self):
        dist = Distribution(project_name="Bar", version="0.9")
        assert dist.key == "bar"

    def test_equality_by_version(self):
        assert Distribution(version="1.0") == Distribution(version="1.0")
        assert not (Distribution(version="1.0") == Distribution(version="1.1"))

    def test_less_than_by_version(self):
        assert Distribution(version="1.0") < Distribution(version="1.1")
        assert not (Distribution(version="1.1") < Distribution(version="1.0"))

    def test_equality_by_project_name_case_insensitive(self):
        assert Distribution(project_name="Foo", version="1.0") == Distribution(project_name="Foo", version="1.0")
        assert Distribution(project_name="Foo", version="1.0") == Distribution(project_name="foo", version="1.0")
        assert not (Distribution(project_name="Foo", version="1.0") == Distribution(project_name="Foo", version="1.1"))

    def test_equality_by_py_version(self):
        assert Distribution(project_name="Foo", py_version="2.3", version="1.0") == Distribution(
            project_name="Foo", py_version="2.3", version="1.0"
        )
        assert not (
            Distribution(project_name="Foo", py_version="2.3", version="1.0")
            == Distribution(project_name="Foo", py_version="2.4", version="1.0")
        )

    def test_equality_by_location(self):
        assert Distribution(location="spam", version="1.0") == Distribution(location="spam", version="1.0")
        assert not (Distribution(location="spam", version="1.0") == Distribution(location="baz", version="1.0"))


class TestWorkingSet:
    def test_default_entries_from_sys_path(self):
        ws = WorkingSet()
        assert ws.entries == sys.path

    def test_empty_working_set(self):
        ws = WorkingSet([])
        assert ws.entries == []

    def test_add_distribution(self):
        ws = WorkingSet([])
        dist = Distribution(
            location="http://example.com/something",
            project_name="Bar",
            version="0.9",
        )
        ws.add(dist)
        assert "http://example.com/something" in ws.entries

    def test_contains_distribution(self):
        ws = WorkingSet([])
        dist = Distribution(
            location="http://example.com/something",
            project_name="Bar",
            version="0.9",
        )
        ws.add(dist)
        assert dist in ws

    def test_not_contains_distribution(self):
        ws = WorkingSet([])
        assert Distribution(project_name="foo", version="") not in ws

    def test_iterate_over_distributions(self):
        ws = WorkingSet([])
        dist = Distribution(
            location="http://example.com/something",
            project_name="Bar",
            version="0.9",
        )
        ws.add(dist)
        assert list(ws) == [dist]

    def test_add_same_distribution_twice(self):
        ws = WorkingSet([])
        dist = Distribution(
            location="http://example.com/something",
            project_name="Bar",
            version="0.9",
        )
        ws.add(dist)
        ws.add(dist)
        assert list(ws) == [dist]

    def test_add_multiple_versions_same_project(self):
        ws = WorkingSet([])
        dist1 = Distribution(
            location="http://example.com/something",
            project_name="Bar",
            version="0.9",
        )
        dist2 = Distribution(
            location="http://example.com/something",
            project_name="Bar",
            version="7.2",
        )
        ws.add(dist1)
        ws.add(dist2)
        assert list(ws) == [dist1]

    def test_add_entry(self):
        ws = WorkingSet([])
        ws.add(
            Distribution(
                location="http://example.com/something",
                project_name="Bar",
                version="0.9",
            )
        )
        ws.add_entry(__file__)
        assert len(ws.entries) == 2

    def test_add_entry_with_path(self):
        ws = WorkingSet([])
        dist = Distribution(project_name="Bar", version="0.9", location="http://example.com/something")
        ws.add(dist, "foo")
        assert ws.entries == ["foo"]

    def test_find_no_match(self):
        ws = WorkingSet([])
        ws.add(
            Distribution(
                project_name="Bar",
                version="0.9",
                location="http://example.com/something",
            )
        )
        result = ws.find(Requirement.parse("Foo==1.0"))
        assert result is None

    def test_find_match(self):
        ws = WorkingSet([])
        ws.add(
            Distribution(
                project_name="Bar",
                version="0.9",
                location="http://example.com/something",
            )
        )
        result = ws.find(Requirement.parse("Bar==0.9"))
        assert result is not None
        assert result.project_name == "Bar"

    def test_find_version_conflict(self):
        ws = WorkingSet([])
        ws.add(
            Distribution(
                project_name="Bar",
                version="0.9",
                location="http://example.com/something",
            )
        )
        with pytest.raises(VersionConflict):
            ws.find(Requirement.parse("Bar==1.0"))

    def test_subscribe_callback(self):
        ws = WorkingSet([])
        dist = Distribution(project_name="Bar", version="0.9", location="http://example.com/something")
        ws.add(dist)

        called = []

        def added(d):
            called.append(d)

        ws.subscribe(added)
        assert len(called) == 1

    def test_subscribe_new_dist_callback(self):
        ws = WorkingSet([])
        dist = Distribution(project_name="Foo", version="1.2", location="f12")
        ws.add(dist)

        called = []

        def added(d):
            called.append(d)

        ws.subscribe(added)
        assert len(called) == 1

        foo14 = Distribution(project_name="Foo", version="1.4", location="f14")
        ws.add(foo14)
        assert len(called) == 1

    def test_find_plugins_basic(self):
        plugins = Environment([])
        foo12 = Distribution(project_name="Foo", version="1.2", location="f12")
        foo14 = Distribution(project_name="Foo", version="1.4", location="f14")
        just_a_test = Distribution(project_name="JustATest", version="0.99")

        plugins.add(foo12)
        plugins.add(foo14)
        plugins.add(just_a_test)

        ws = WorkingSet([])
        available, errors = ws.find_plugins(plugins)

        assert len(available) == 2
        assert just_a_test in available

    def test_find_plugins_with_conflict(self):
        plugins = Environment([])
        foo12 = Distribution(project_name="Foo", version="1.2", location="f12")
        foo14 = Distribution(project_name="Foo", version="1.4", location="f14")
        just_a_test = Distribution(project_name="JustATest", version="0.99")

        plugins.add(foo12)
        plugins.add(foo14)
        plugins.add(just_a_test)

        ws = WorkingSet([])
        ws.add(foo12)

        available, errors = ws.find_plugins(plugins)
        assert len(available) == 2
        assert foo12 in available

    def test_find_plugins_fallback_false(self):
        plugins = Environment([])
        foo12 = Distribution(project_name="Foo", version="1.2", location="f12")
        foo14 = Distribution(project_name="Foo", version="1.4", location="f14")
        just_a_test = Distribution(project_name="JustATest", version="0.99")

        plugins.add(foo12)
        plugins.add(foo14)
        plugins.add(just_a_test)

        ws = WorkingSet([])
        ws.add(foo12)

        available, errors = ws.find_plugins(plugins, fallback=False)
        assert len(available) == 1
        assert just_a_test in available


class TestEnvironment:
    def test_create_empty(self):
        env = Environment([])
        assert len(env) == 0

    def test_add_distribution(self):
        env = Environment([])
        dist = Distribution(project_name="Foo", version="1.2")
        env.add(dist)
        assert len(env) == 1

    def test_iterate(self):
        env = Environment([])
        dist = Distribution(project_name="Foo", version="1.2")
        env.add(dist)
        assert list(env) == [dist]


class TestRequirement:
    def test_parse_simple(self):
        req = Requirement.parse("Foo==1.0")
        assert req.project_name == "Foo"
        assert req.specs == [("==", "1.0")]

    def test_parse_complex(self):
        req = Requirement.parse("Foo>=1.0,<2.0")
        assert req.project_name == "Foo"
        assert req.specs == [(">=", "1.0"), ("<", "2.0")]

    def test_parse_with_extras(self):
        req = Requirement.parse("Foo[extra1,extra2]")
        assert req.project_name == "Foo"
        assert req.extras == ["extra1", "extra2"]

    def test_matches_exact_version(self):
        req = Requirement.parse("Foo==1.0")
        dist = Distribution(project_name="Foo", version="1.0")
        assert req.matches(dist)

    def test_matches_different_version(self):
        req = Requirement.parse("Foo==1.0")
        dist = Distribution(project_name="Foo", version="1.1")
        assert not req.matches(dist)

    def test_matches_greater_than(self):
        req = Requirement.parse("Foo>1.0")
        dist = Distribution(project_name="Foo", version="1.1")
        assert req.matches(dist)

    def test_matches_greater_than_equal(self):
        req = Requirement.parse("Foo>=1.0")
        dist = Distribution(project_name="Foo", version="1.0")
        assert req.matches(dist)

    def test_matches_less_than(self):
        req = Requirement.parse("Foo<2.0")
        dist = Distribution(project_name="Foo", version="1.9")
        assert req.matches(dist)

    def test_matches_not_equal(self):
        req = Requirement.parse("Foo!=1.0")
        dist = Distribution(project_name="Foo", version="1.1")
        assert req.matches(dist)

    def test_matches_wildcard(self):
        req = Requirement.parse("Foo~=1.0")
        dist = Distribution(project_name="Foo", version="1.5")
        assert req.matches(dist)


class TestCompatiblePlatforms:
    def test_same_platform(self):
        assert compatible_platforms("win32", "win32")

    def test_different_platforms(self):
        assert not compatible_platforms("win32", "macosx-10.4-ppc")

    def test_macosx_same_version(self):
        assert compatible_platforms("macosx-10.4-ppc", "macosx-10.4-ppc")

    def test_macosx_different_arch(self):
        assert not compatible_platforms("macosx-10.4-ppc", "macosx-10.4-i386")

    def test_macosx_older_version_compatible(self):
        assert compatible_platforms("macosx-10.4-ppc", "macosx-10.3-ppc")

    def test_macosx_newer_version_incompatible(self):
        assert not compatible_platforms("macosx-10.4-ppc", "macosx-10.5-ppc")

    def test_macosx_different_major_incompatible(self):
        assert not compatible_platforms("macosx-10.4-ppc", "macosx-9.5-ppc")

    def test_darwin_to_macosx_compatible(self):
        assert compatible_platforms("darwin-8.2.0-Power_Macintosh", "macosx-10.4-ppc")

    def test_old_darwin_incompatible(self):
        assert not compatible_platforms("darwin-7.2.0-Power_Macintosh", "macosx-10.3-ppc")


class TestInvalidMarker:
    def test_invalid_sys_platform(self):
        result = invalid_marker("sys_platform")
        assert "Expected marker operator" in result

    def test_invalid_incomplete(self):
        result = invalid_marker("sys_platform==")
        assert "Expected marker variable" in result

    def test_valid_sys_platform(self):
        result = invalid_marker("sys_platform=='win32'")
        assert result is False

    def test_invalid_extra(self):
        result = invalid_marker("(extra)")
        assert "Expected marker operator" in result

    def test_invalid_extra_incomplete(self):
        result = invalid_marker("(extra")
        assert "Expected marker operator" in result


class TestEvaluateMarker:
    def test_sys_platform_win32(self):
        result = evaluate_marker("sys_platform=='win32'")
        assert result == (sys.platform == "win32")

    def test_python_version_27(self):
        result = evaluate_marker("python_version >= '2.7'")
        assert result is True

    def test_python_version_greater_than_26(self):
        result = evaluate_marker("python_version > '2.6'")
        assert result is True

    def test_implementation_name(self):
        result = evaluate_marker("implementation_name=='cpython'")
        assert result is False

    def test_platform_python_implementation(self):
        result = evaluate_marker("platform_python_implementation=='CPython'")
        assert result is False

    def test_implementation_version(self):
        result = evaluate_marker("implementation_version=='3.5.1'")
        assert result is False


class TestParseVersion:
    def test_simple_version(self):
        assert parse_version("1.0") == ((1, ""), (0, ""))

    def test_empty_version(self):
        assert parse_version("") == ()

    def test_version_with_suffix(self):
        assert parse_version("1.0a1") == ((1, ""), (0, "a1"))
