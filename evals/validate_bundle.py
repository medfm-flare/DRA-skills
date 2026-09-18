#!/usr/bin/env python3
"""Validate skill packaging and fixture installs without SSH or user config writes.

Run with Python 3, PyYAML, bash, and jq. This checks structure and installation,
not model routing; use routing-trigger.json in a fresh model session for that.
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- BEGIN: lab-config -->"
END = "<!-- END: lab-config -->"
PERSONAL = "# Personal notes\nKeep my project preferences.\n"


def parse_skill(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    parts = text.split("---", 2)
    assert len(parts) == 3 and not parts[0], f"Missing frontmatter: {path}"
    metadata = yaml.safe_load(parts[1])
    assert isinstance(metadata, dict), f"Invalid frontmatter: {path}"
    name = metadata.get("name", "")
    description = metadata.get("description", "")
    assert isinstance(name, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), path
    assert len(name) <= 64, path
    assert isinstance(description, str) and 0 < len(description) <= 1024, path
    assert name == path.parent.name, f"Directory/name mismatch: {path}"
    assert parts[2].strip(), f"Empty skill body: {path}"
    return metadata, parts[2]


def check_links(path: Path) -> None:
    """Check local Markdown resources from both source and installed locations."""
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
        if "://" in target or target.startswith("#"):
            continue
        relative = target.split("#", 1)[0]
        assert (path.parent / relative).exists(), f"Broken reference in {path}: {target}"


def validate_sources() -> set[str]:
    paths = sorted(ROOT.glob("shared/**/SKILL.md"))
    paths += sorted(ROOT.glob("modules/**/SKILL.md.template"))
    names = set()
    for path in paths:
        metadata, _ = parse_skill(path)
        names.add(metadata["name"])
        check_links(path)
    for path in ROOT.glob("shared/**/references/**/*.md"):
        # Older cluster pages contain prose URL examples rather than Markdown links.
        check_links(path)

    for name in ("slurm-queue", "slurm-resource", "slurm-storage"):
        adapter = ROOT / f"shared/codex/skills/{name}/SKILL.md"
        agent = ROOT / f"shared/agents/{name}.md"
        agent_body = agent.read_text().split("---", 2)[2]
        assert parse_skill(adapter)[1] == agent_body, f"Workflow drift: {name}"

    cases = json.loads((ROOT / "evals/routing-trigger.json").read_text())
    assert set(cases["skills_under_test"]) == names, "Eval catalog differs from skill catalog"
    ids = [case["id"] for case in cases["cases"]]
    assert len(ids) == len(set(ids)), "Duplicate eval IDs"
    for case in cases["cases"]:
        assert case["expect"] is None or case["expect"] in names, case["id"]
    print(f"Source validation: {len(paths)} skill entrypoints, {len(names)} names, "
          f"{len(ids)} model-eval cases")
    return names


def fixture_install(targets: str, module: str, names: set[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="dra-bundle-") as temp:
        fixture = Path(temp).resolve()
        repo = fixture / "repo"
        repo.mkdir()
        for directory in ("shared", "modules"):
            shutil.copytree(ROOT / directory, repo / directory)

        claude = fixture / "claude"
        codex = fixture / "codex"
        for config in (claude, codex):
            config.mkdir()
        (claude / "CLAUDE.md").write_text(PERSONAL)
        (codex / "AGENTS.md").write_text(PERSONAL)

        # Redirect only the disposable copy's two config constants. Do not change
        # HOME/CODEX_HOME or execute the real installer against the user's config.
        installer = (ROOT / "setup.sh").read_text()
        for original, directory in (("CLAUDE_DIR=\"$HOME/.claude\"", claude),
                                    ("CODEX_DIR=\"$HOME/.codex\"", codex)):
            assert installer.count(original) == 1, "Installer fixture needs updating"
            variable = original.split("=", 1)[0]
            installer = installer.replace(original, f"{variable}={shlex.quote(str(directory))}")
        (repo / "setup.sh").write_text(installer)
        (repo / "build").mkdir()
        (repo / "build/.env.local").write_text(
            "FIR_USERNAME=fixture-user\nFIR_ACCOUNT=def-fixture_gpu\n"
            "FIR_GPU_TYPE=nvidia_h100_80gb_hbm3_1g.10gb\n"
        )
        command = ["bash", str(repo / "setup.sh"), "--modules", module,
                   "--targets", targets, "--non-interactive"]
        before = None
        for _ in range(2):
            result = subprocess.run(command, cwd=repo, text=True, capture_output=True, timeout=30)
            assert result.returncode == 0, result.stdout + result.stderr
            documents = {}
            for target, config, doc in (("claude", claude, "CLAUDE.md"),
                                        ("codex", codex, "AGENTS.md")):
                content = (config / doc).read_text()
                if target not in targets.split(","):
                    assert content == PERSONAL, f"Unselected target changed: {target}"
                    continue
                assert content.count(BEGIN) == content.count(END) == 1, doc
                assert content.endswith(PERSONAL), f"Personal content lost: {doc}"
                assert "{{" not in content, f"Unexpanded instruction template: {doc}"
                adapter = repo / "shared/instructions" / f"{target}.md"
                assert adapter.read_text().strip() in content, f"Missing {target} adapter: {doc}"
                if module == "fir":
                    fir_adapter = repo / "modules/fir/instructions" / f"{target}.md"
                    assert fir_adapter.read_text().strip() in content, f"Missing Fir {target} adapter: {doc}"
                    other = "codex" if target == "claude" else "claude"
                    other_adapter = repo / "modules/fir/instructions" / f"{other}.md"
                    assert other_adapter.read_text().strip() not in content, f"Wrong tool adapter: {doc}"
                documents[target] = content
                expected = names - ({"slurm-status"} if module == "none" else set())
                if target == "claude":
                    expected -= {"slurm-queue", "slurm-resource", "slurm-storage"}
                installed = {path.name for path in (config / "skills").iterdir()}
                assert installed == expected, (target, installed, expected)
                for name in expected:
                    skill = config / "skills" / name / "SKILL.md"
                    assert skill.is_file(), f"Broken installed link: {skill}"
                    parse_skill(skill)
                    check_links(skill)
                    assert "{{" not in skill.read_text(), f"Unexpanded skill: {skill}"
                if target == "codex":
                    assert (config / "skills/onboard").resolve() == (repo / "shared/codex/skills/onboard").resolve()
                else:
                    json.loads((config / "settings.json").read_text())
                    for name in ("slurm-queue", "slurm-resource", "slurm-storage"):
                        assert (config / "agents" / f"{name}.md").is_file()
            if before is not None:
                assert documents == before, "Repeated install changed instruction content"
            before = documents

        if module == "fir":
            result = subprocess.run(
                ["bash", str(repo / "setup.sh"), "--modules", "none", "--targets", targets,
                 "--non-interactive"], cwd=repo, text=True, capture_output=True, timeout=30
            )
            assert result.returncode == 0, result.stdout + result.stderr
            for target, config in (("claude", claude), ("codex", codex)):
                if target in targets.split(","):
                    link = config / "skills/slurm-status"
                    assert not link.exists() and not link.is_symlink(), "Stale Fir skill survived"
        print(f"Fixture install: targets={targets}, modules={module}, repeated install OK")


def main() -> None:
    for program in ("bash", "jq"):
        if not shutil.which(program):
            raise SystemExit(f"Required for fixture installation: {program}")
    names = validate_sources()
    for targets in ("codex", "claude", "claude,codex"):
        for module in ("none", "fir"):
            fixture_install(targets, module, names)
    print("Bundle validation passed. Model routing has not been evaluated by this script.")


if __name__ == "__main__":
    main()
