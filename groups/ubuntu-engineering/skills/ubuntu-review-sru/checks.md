### Quality Checks

- The overall change should be **minimal** and focused on fixing the reported bug(s).
- No unrelated changes are present in the diff.
- Any new Debian patch file should conform to the Debian DEP-3 format.
- Package version follows SRU convention (`<oldversion>+esm*` or `<release><number>.<oldversion>`).
- No dependency on another SRU that must land simultaneously.

### Upstream / Archive Alignment

```bash
rmadison -a source <package>
```

- Identify the versions in **later supported releases** and the **current devel release**.
- In the git-ubuntu repository, each Ubuntu release is represented by a tag of the form `pkg/ubuntu/<release>-devel`.
- For each relevant release, compare its changelog/diff against this SRU to confirm the same fix (or an equivalent/superseding fix) is present.
- The fix is present in all **later supported releases**.
- The fix is present in the **current devel release**.
- If a new upstream version is included, confirm `uscan` works and the tarball is verifiable.

### Packaging Specifics

- The maintainer in `debian/control` needs to have an `ubuntu.com` email address.
- Check `debian/control` for **NEW packages**; if any exist, this requires an AA/SRU combined review per [non-standard SRU processes](https://documentation.ubuntu.com/sru/en/latest/explanation/non-standard-processes/#new-queue-in-the-sru-context).
- Verify no changes affect translations.
- If the bug claims a **package-specific procedure**, consult [package-specific SRU instructions](https://documentation.ubuntu.com/sru/en/latest/reference/package-specific/).

### Bug & Test Plan Validation

- On Launchpad, the bug has **Ubuntu release tasks** for every target release.
- The **SRU template** is completely and correctly filled in on each bug.
- The test plan covers **normal usage** of the package, not only the specific code change.
- The test plan tells a coherent **user story**.
- If the bug involves the **kernel**, both **GA and HWE kernels** must be included in the test plan.

### Phasing Status

- Visit <https://ubuntu-archive-team.ubuntu.com/phased-updates.html>.
- If phasing was halted due to errors, confirm the changes in this upload address the failure.
