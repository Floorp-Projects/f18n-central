# Floorp Localization

<a href="https://crowdin.com/project/floorp-browser" rel="nofollow">
  <img style="width:140;height:40px" src="https://badges.crowdin.net/badge/light/crowdin-on-dark.png#gh-dark-mode-only" alt="Floorp Browser Localize at Crowdin" />
</a>

<p align="center">
<img src="assets/Floorp_Logo_f18n_Light.svg#gh-light-mode-only" width="300px"></img>
<img src="assets/Floorp_Logo_f18n_Dark.svg#gh-dark-mode-only" width="300px"></img>
</p>

> [!IMPORTANT]
> **This repository is read-only for manual contributions.**  
> Localization source files (en-US) are maintained in the main [Floorp repository](https://github.com/Floorp-Projects/Floorp) and automatically synced here.  
> Translations into other languages are managed via [Crowdin](https://crowdin.com/project/floorp-browser). Do not submit Pull Requests directly to this repository.

## How to Contribute

### 1. Updating or Fixing English (en-US) Strings
If you want to improve, fix typos, or update outdated English descriptions, please submit a Pull Request to the **[Floorp-Projects/Floorp](https://github.com/Floorp-Projects/Floorp)** repository instead of this one.

The source files in the Floorp repository correspond to the files here as follows:

| f18n-central path | Source file in `Floorp-Projects/Floorp` |
| :--- | :--- |
| `main/en-US/*.json` | `i18n/en-US/*.json` |
| `stub-win64-installer/en-US.json` | `static/installers/stub-win64-installer/src/lib/i18n/locales/en-US.json` |
| `{feature-name}/en-US.json`<br>*(e.g., `settings/`, `newtab/`, `about-dialog/`)* | `browser-features/pages-{feature-name}/src/lib/i18n/locales/en-US.json`<br>*(e.g., `pages-settings/`, `pages-newtab/`, `pages-aboutDialog/`)* |

*Full mapping configuration can be found in [`i18n/translation-targets.json`](https://github.com/Floorp-Projects/Floorp/blob/main/i18n/translation-targets.json).*

### 2. Translating into Other Languages
All translations (Japanese, French, German, etc.) are managed through Crowdin:
👉 **[Join Floorp Browser translation on Crowdin](https://crowdin.com/project/floorp-browser)**

Translations submitted on Crowdin will be automatically synchronized to this repository and then integrated into Floorp releases.

🙏 Your support in this effort is greatly appreciated. Let's make Floorp available to even more people worldwide!

# Main Repository

[![Link to Main Repository](assets/Link2MainRepo.svg)](https://github.com/Floorp-Projects/Floorp)

# Localization Automation

The source and translated files are synchronized without writing unverified
translations directly to Floorp's `main` branch:

1. `sync-target-files.yml` refreshes the English source files from Floorp once
   per day.
2. `sync-translated-files.yml` runs every six hours. It accepts only the
   same-repository `crowdin` pull request titled `New Crowdin updates`, rejects
   removed or non-translation files, and verifies that translated JSON files
   contain every source key before merging it. The candidate is built locally
   from the exact main and Crowdin commits, rather than GitHub's potentially
   stale PR merge ref. Conflicts report the affected files and stop publication.
   Both commits are checked again before merging. Crowdin PRs use merge commits
   to retain their ancestry, preventing previously published translations from
   being replayed in later PRs.
3. The translated files are copied to the `automation/sync-translations`
   branch in Floorp and submitted as a pull request.
4. The synchronization pull request is merged only after all expected Floorp
   integration checks pass and its tested head commit is unchanged. Failed
   validation or CI leaves the pull request open for review.

Both synchronization workflows use the `localization-sync` concurrency group,
so source and translated-file updates cannot run at the same time. They require
the `PAT` Actions secret to have permission to push branches, create pull
requests, and merge pull requests in both repositories.

If a manual translation on main conflicts with Crowdin, merge main into the
crowdin branch and resolve the affected keys without dropping either side's
additions. Preserve the latest reviewed translation for conflicting wording,
run `validate_translation_schema.py` against the Floorp manifest, then rerun
publication. Do not force-push or replace translations with source-language
fallbacks to clear a conflict.
