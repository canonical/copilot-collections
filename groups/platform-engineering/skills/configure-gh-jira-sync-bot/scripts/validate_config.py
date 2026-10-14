#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "typer"]
# ///
"""Validate a gh-jira-sync-bot `.github/.jira_sync_config.yaml` file."""

from pathlib import Path
from typing import Annotated

import typer
import yaml

# Components of the ISD Jira project
VALID_COMPONENTS: frozenset[str] = frozenset(
    {
        "12-factor",
        "Aproxy",
        "Backup",
        "Bingo",
        "CharmCI",
        "Charmkeeper",
        "Charmstudio",
        "Chrony",
        "Cloudflared",
        "Company initiatives",
        "Content cache",
        "Copilot collections",
        "Digest Squid auth helper",
        "Discourse",
        "Discourse-Gatekeeper",
        "DNS",
        "Documentation",
        "Docusign",
        "Falco",
        "Forward proxy",
        "Gateway API",
        "GitHub runner",
        "gopkg",
        "HAProxy",
        "Hockeypuck",
        "HRMS",
        "HTTP Request lego provider",
        "Indico",
        "Ingress configurator",
        "IS support",
        "Jenkins",
        "Kubernetes ingress",
        "Mail server",
        "Mailman",
        "Matrix",
        "MatterMost",
        "MediaWiki",
        "NetBox",
        "NTP",
        "OpenCTI",
        "Operator workflows",
        "osquery",
        "Penpot",
        "Pollen",
        "repolint",
        "Saml integrator",
        "Smtp integrator",
        "Team initiatives",
        "Traefik",
        "Ubuntu MOTD",
        "Wazuh",
        "WireGuard",
        "WordPress",
        "Zeek",
    }
)
MANDATORY_STATUS_KEYS: tuple[str, ...] = ("opened", "closed")
REQUIRED_LABELS: tuple[str, ...] = ("bug", "enhancement")
PLACEHOLDER_MARKER = "<your-component>"


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_status_mapping(settings: dict[str, object]) -> list[str]:
    status_mapping = settings.get("status_mapping")
    if not isinstance(status_mapping, dict):
        return ["settings.status_mapping is mandatory and must be a mapping"]
    errors = []
    for key in MANDATORY_STATUS_KEYS:
        if not _is_non_empty_string(status_mapping.get(key)):
            errors.append(f"settings.status_mapping.{key} is mandatory (non-empty string)")
    if "not_planned" in status_mapping and not _is_non_empty_string(status_mapping["not_planned"]):
        errors.append("settings.status_mapping.not_planned must be a non-empty string")
    return errors


def _validate_components(settings: dict[str, object]) -> list[str]:
    errors = []
    if "component" in settings:
        errors.append("settings.component is not supported by the bot, use the list settings.components")
    components = settings.get("components")
    if not isinstance(components, list) or not components:
        errors.append("settings.components is mandatory and must be a non-empty list")
        return errors
    for component in components:
        if component == PLACEHOLDER_MARKER:
            errors.append(f"settings.components still contains the placeholder {PLACEHOLDER_MARKER}")
        elif not isinstance(component, str) or component not in VALID_COMPONENTS:
            errors.append(
                f"settings.components: {component!r} is not a valid Jira component "
                f"(valid: {', '.join(sorted(VALID_COMPONENTS))})"
            )
    return errors


def _validate_optional_fields(settings: dict[str, object]) -> list[str]:
    errors = []
    labels = settings.get("labels")
    if not isinstance(labels, list) or not all(_is_non_empty_string(label) for label in labels):
        errors.append("settings.labels is mandatory and must be a list of non-empty strings")
    else:
        missing = [label for label in REQUIRED_LABELS if label not in labels]
        if missing:
            errors.append(
                f"settings.labels must include {', '.join(REQUIRED_LABELS)} "
                f"(missing: {', '.join(missing)}); this avoids syncing Dependency dashboard issues"
            )
    if "epic_key" in settings:
        errors.append("settings.epic_key must not be defined")
    label_mapping = settings.get("label_mapping")
    if label_mapping is not None and (
        not isinstance(label_mapping, dict)
        or not all(_is_non_empty_string(value) for value in label_mapping.values())
    ):
        errors.append("settings.label_mapping must map GitHub labels to Jira issue types (strings)")
    if "add_gh_comment" in settings and not isinstance(settings["add_gh_comment"], bool):
        errors.append("settings.add_gh_comment must be a boolean")
    return errors


def validate_settings(config: object) -> list[str]:
    """Return the list of validation errors for a parsed configuration."""
    if not isinstance(config, dict) or not isinstance(config.get("settings"), dict):
        return ["top-level `settings` mapping is mandatory"]
    settings: dict[str, object] = config["settings"]
    errors = []
    if not _is_non_empty_string(settings.get("jira_project_key")):
        errors.append("settings.jira_project_key is mandatory (non-empty string)")
    errors += _validate_status_mapping(settings)
    errors += _validate_components(settings)
    errors += _validate_optional_fields(settings)
    return errors


def _read_template_labels(template_path: Path) -> object:
    text = template_path.read_text()
    if template_path.suffix == ".md":
        parts = text.split("---", 2)
        text = parts[1] if text.startswith("---") and len(parts) == 3 else ""
    parsed = yaml.safe_load(text)
    return parsed.get("labels") if isinstance(parsed, dict) else None


def validate_issue_templates(issue_template_dir: Path) -> list[str]:
    """Each issue template must carry the `bug` or `enhancement` label."""
    errors = []
    template_paths = sorted(
        path
        for path in issue_template_dir.glob("*")
        if path.suffix in {".yml", ".yaml", ".md"} and path.stem != "config"
    )
    for template_path in template_paths:
        try:
            labels = _read_template_labels(template_path)
        except (OSError, yaml.YAMLError) as error:
            errors.append(f"{template_path}: cannot read issue template: {error}")
            continue
        if isinstance(labels, str):
            labels = [label.strip() for label in labels.split(",")]
        if not isinstance(labels, list) or not set(REQUIRED_LABELS) & set(labels):
            errors.append(f"{template_path}: `labels` must contain bug or enhancement")
    return errors


def main(
    config_path: Annotated[Path, typer.Argument(help="Path to .github/.jira_sync_config.yaml")],
) -> None:
    """Validate the mandatory fields of a gh-jira-sync-bot configuration."""
    try:
        config = yaml.safe_load(config_path.read_text())
    except (OSError, yaml.YAMLError) as error:
        typer.echo(f"ERROR: cannot read {config_path}: {error}", err=True)
        raise typer.Exit(code=1)
    errors = validate_settings(config)
    issue_template_dir = config_path.resolve().parent / "ISSUE_TEMPLATE"
    if issue_template_dir.is_dir():
        errors += validate_issue_templates(issue_template_dir)
    for error in errors:
        typer.echo(f"ERROR: {error}", err=True)
    if errors:
        raise typer.Exit(code=1)
    typer.echo(f"{config_path}: OK")


app = typer.Typer(add_completion=False)
app.command(no_args_is_help=True)(main)

if __name__ == "__main__":
    app()
