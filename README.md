# Floorp Localization

<a href="https://crowdin.com/project/floorp-browser" rel="nofollow">
  <img style="width:140;height:40px" src="https://badges.crowdin.net/badge/light/crowdin-on-dark.png#gh-dark-mode-only" alt="Floorp Browser Localize at Crowdin" />
</a>

<p align="center">
<img src="assets/Floorp_Logo_f18n_Light.svg#gh-light-mode-only" width="300px"></img>
<img src="assets/Floorp_Logo_f18n_Dark.svg#gh-dark-mode-only" width="300px"></img>
</p>

This repository hosts the localization files for Floorp, which have been sourced from Crowdin. It also include main English (US) localization.

## Improving the English (US) Localization

If you notice any issues with the English (US) localization, you can modify or fix it by following these steps:

1. Fork this repository by clicking the [Fork](https://github.com/Floorp-Projects/f18n-central/fork) button.

2. Clone your forked repository to your local machine using the following command:

```bash
git clone https://github.com/{YOUR_USERNAME}/f18n-central.git
```

3. Create a new branch for your improvements using the following command:

```bash
git checkout -b your_branch
```

4. Update the English (US) source files under `main/en-US/` (for example `main/en-US/browser-chrome.json`). The list of synced namespaces lives in Floorp at https://github.com/Floorp-Projects/Floorp/blob/main/i18n/translation-targets.json.

The `JSON` file extension is used for i18next localization files. You can use any text editor to edit the file. The structure of the file is as follows:

```json
{
  "key": "value",
  "key": "value"
}
```

You can modify the value of the key to improve the localization. For example:

```json
{
  "hello": "Hello, World!",
  "welcome": "Welcome to Floorp!"
}
```

5. Commit your changes.

```bash
git add .
git commit -m "Your commit message"
```

6. Push your changes.

```bash
git push origin your_branch
```

7. Create a pull request.

[Create Pull Request](https://github.com/Floorp-Projects/f18n-central/compare)

# Contributing to other translation

✅ If you are fluent in a language and want to help translate Floorp Browser, we invite you to be part of our Crowdin translation project.

🌎 [Get started on Crowdin](https://crowdin.com/project/floorp-browser) and contribute to making Floorp accessible in your language.

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
