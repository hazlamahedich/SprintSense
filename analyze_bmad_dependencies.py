#!/usr/bin/env python3
"""
Analyze BMad Method dependencies to find missing referenced documents.
This script identifies files referenced by the bmad method but not present in the filesystem.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

import yaml


class BmadDependencyAnalyzer:
    def __init__(self, bmad_core_path: str):
        self.bmad_core = Path(bmad_core_path)
        self.referenced_files = set()
        self.actual_files = set()
        self.missing_files = []
        self.references_map = {}  # file -> list of sources that reference it

    def extract_yaml_from_markdown(self, content: str) -> Dict:
        """Extract YAML block from markdown content."""
        yaml_pattern = r"```yaml\n(.*?)\n```"
        match = re.search(yaml_pattern, content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                return {}
        return {}

    def add_reference(self, filename: str, source: str):
        """Add a reference to the tracking map."""
        if filename not in self.references_map:
            self.references_map[filename] = []
        self.references_map[filename].append(source)
        self.referenced_files.add(filename)

    def parse_agent_dependencies(self):
        """Parse all agent files for dependency references."""
        agents_dir = self.bmad_core / "agents"

        for agent_file in agents_dir.glob("*.md"):
            print(f"Processing agent: {agent_file.name}")
            content = agent_file.read_text()
            yaml_data = self.extract_yaml_from_markdown(content)

            if "dependencies" in yaml_data:
                deps = yaml_data["dependencies"]
                for category, files in deps.items():
                    if isinstance(files, list):
                        for file_name in files:
                            full_path = f"{category}/{file_name}"
                            self.add_reference(full_path, f"agent:{agent_file.name}")

            # Also check commands for template references
            if "commands" in yaml_data:
                commands = yaml_data["commands"]
                for cmd in commands:
                    if isinstance(cmd, str) and "{template}" in cmd:
                        # This command uses templates, add all templates as potential references
                        templates_dir = self.bmad_core / "templates"
                        if templates_dir.exists():
                            for tmpl in templates_dir.glob("*.yaml"):
                                self.add_reference(
                                    f"templates/{tmpl.name}",
                                    f"agent:{agent_file.name}:command",
                                )

    def parse_core_config(self):
        """Parse core-config.yaml for document references."""
        config_file = self.bmad_core / "core-config.yaml"
        if config_file.exists():
            config = yaml.safe_load(config_file.read_text())

            # Check for file references in config
            file_keys = ["prdFile", "architectureFile", "devDebugLog"]
            for key in file_keys:
                if key in config:
                    self.add_reference(config[key], "core-config.yaml")

            # Check devLoadAlwaysFiles
            if "devLoadAlwaysFiles" in config and config["devLoadAlwaysFiles"]:
                for file_path in config["devLoadAlwaysFiles"]:
                    self.add_reference(file_path, "core-config.yaml:devLoadAlwaysFiles")

    def scan_templates_for_references(self):
        """Scan template and workflow files for nested references."""
        for category in ["templates", "workflows", "tasks", "checklists", "data"]:
            category_dir = self.bmad_core / category
            if category_dir.exists():
                for file_path in category_dir.glob("*.md"):
                    self._scan_file_for_references(file_path, category)
                for file_path in category_dir.glob("*.yaml"):
                    self._scan_file_for_references(file_path, category)

    def _scan_file_for_references(self, file_path: Path, source_category: str):
        """Scan a single file for references to other files."""
        try:
            content = file_path.read_text()

            # Look for .md file references
            md_refs = re.findall(r"([a-zA-Z0-9_-]+\.md)", content)
            for ref in md_refs:
                self.add_reference(ref, f"{source_category}:{file_path.name}")

            # Look for .yaml/.yml file references
            yaml_refs = re.findall(r"([a-zA-Z0-9_-]+\.ya?ml)", content)
            for ref in yaml_refs:
                self.add_reference(ref, f"{source_category}:{file_path.name}")

            # Look for bmad-core path references
            bmad_refs = re.findall(
                r"\.bmad-core/([a-zA-Z0-9_/-]+\.(md|ya?ml))", content
            )
            for ref, ext in bmad_refs:
                self.add_reference(ref, f"{source_category}:{file_path.name}")

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    def enumerate_actual_files(self):
        """Build set of files that actually exist in the filesystem."""
        for root, dirs, files in os.walk(self.bmad_core):
            for file in files:
                if file.endswith((".md", ".yaml", ".yml")):
                    rel_path = Path(root).relative_to(self.bmad_core) / file
                    self.actual_files.add(str(rel_path))

        # Also check for files in project docs directory (referenced by core-config)
        docs_dir = self.bmad_core.parent / "docs"
        if docs_dir.exists():
            for root, dirs, files in os.walk(docs_dir):
                for file in files:
                    if file.endswith((".md", ".yaml", ".yml")):
                        rel_path = Path(root).relative_to(self.bmad_core.parent) / file
                        self.actual_files.add(str(rel_path))

    def compute_missing_files(self):
        """Compute the difference between referenced and actual files."""
        for ref_file in self.referenced_files:
            # Try different path variations
            variations = [
                ref_file,
                ref_file.replace("/", os.sep),
                f".bmad-core/{ref_file}",
                ref_file.split("/")[-1] if "/" in ref_file else ref_file,
            ]

            found = False
            for variation in variations:
                if variation in self.actual_files:
                    found = True
                    break
                # Also check if file exists with different extension or in different location
                for actual in self.actual_files:
                    if Path(actual).name == Path(variation).name:
                        found = True
                        break

            if not found:
                # Categorize the missing file
                category = "other"
                if ref_file.startswith("checklists/"):
                    category = "checklist"
                elif ref_file.startswith("tasks/"):
                    category = "task"
                elif ref_file.startswith("templates/"):
                    category = "template"
                elif ref_file.startswith("data/"):
                    category = "data"
                elif ref_file.startswith("workflows/"):
                    category = "workflow"
                elif ref_file.endswith("checklist.md"):
                    category = "checklist"
                elif "template" in ref_file or "tmpl" in ref_file:
                    category = "template"

                self.missing_files.append(
                    {
                        "file": ref_file,
                        "category": category,
                        "referenced_by": self.references_map.get(ref_file, []),
                    }
                )

    def generate_report(self) -> str:
        """Generate a comprehensive markdown report."""
        report = []
        report.append("# BMad Method Missing Dependencies Report")
        report.append("")
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Total referenced files**: {len(self.referenced_files)}")
        report.append(f"- **Total actual files**: {len(self.actual_files)}")
        report.append(f"- **Missing files**: {len(self.missing_files)}")
        report.append("")

        if not self.missing_files:
            report.append(
                "✅ **Good news!** All referenced files appear to exist in the filesystem."
            )
            return "\n".join(report)

        # Group by category
        by_category = {}
        for item in self.missing_files:
            category = item["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)

        report.append("## Missing Files by Category")
        report.append("")

        for category, files in sorted(by_category.items()):
            report.append(f"### {category.title()} Files ({len(files)} missing)")
            report.append("")
            report.append("| File | Referenced By | Likely Purpose |")
            report.append("|------|---------------|----------------|")

            for file_info in files:
                file_name = file_info["file"]
                refs = ", ".join(
                    file_info["referenced_by"][:3]
                )  # Limit to 3 refs for readability
                if len(file_info["referenced_by"]) > 3:
                    refs += f" (+{len(file_info['referenced_by'])-3} more)"

                # Infer purpose from filename
                purpose = self._infer_purpose(file_name, category)

                report.append(f"| `{file_name}` | {refs} | {purpose} |")

            report.append("")

        report.append("## Recommendations")
        report.append("")
        report.append(
            "1. **Create missing files**: Start with the most referenced files"
        )
        report.append(
            "2. **Update references**: Some files may exist with different names/paths"
        )
        report.append(
            "3. **Clean up**: Remove references to files that are no longer needed"
        )
        report.append("")

        return "\n".join(report)

    def _infer_purpose(self, filename: str, category: str) -> str:
        """Infer the purpose of a missing file based on its name and category."""
        name = filename.lower()

        if category == "checklist":
            return "Quality assurance checklist"
        elif category == "template":
            if "prd" in name:
                return "Product Requirements Document template"
            elif "architecture" in name:
                return "Architecture document template"
            elif "story" in name:
                return "User story template"
            else:
                return "Document template"
        elif category == "task":
            if "create" in name:
                return "Document creation workflow"
            elif "review" in name:
                return "Review/validation workflow"
            else:
                return "Task workflow"
        elif category == "data":
            return "Reference data or knowledge base"
        elif category == "workflow":
            return "Multi-step process workflow"
        else:
            return "Support document"


def main():
    bmad_core_path = "/Users/sherwingorechomante/Sprintsense/.bmad-core"
    analyzer = BmadDependencyAnalyzer(bmad_core_path)

    print("🔍 Starting BMad dependency analysis...")

    print("📋 Parsing agent dependencies...")
    analyzer.parse_agent_dependencies()

    print("⚙️ Parsing core configuration...")
    analyzer.parse_core_config()

    print("🔗 Scanning for nested references...")
    analyzer.scan_templates_for_references()

    print("📁 Enumerating actual files...")
    analyzer.enumerate_actual_files()

    print("🧮 Computing missing files...")
    analyzer.compute_missing_files()

    print("📝 Generating report...")
    report = analyzer.generate_report()

    # Save report
    report_path = "/Users/sherwingorechomante/Sprintsense/docs/bmad-missing-dependencies-report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w") as f:
        f.write(report)

    print(f"✅ Report saved to: {report_path}")
    print("\n" + "=" * 50)
    print("PREVIEW:")
    print("=" * 50)
    print(report[:1000] + "..." if len(report) > 1000 else report)

    return analyzer


if __name__ == "__main__":
    analyzer = main()
