# Floorp Localization

<a href="https://crowdin.com/project/floorp-browser" rel="nofollow">
  <img style="width:140;height:40px" src="https://badges.crowdin.net/badge/light/crowdin-on-dark.png#gh-dark-mode-only" alt="Floorp Browser Localize at Crowdin" />
</a>

<p align="center">
<img src="assets/Floorp_Logo_f10n_Light.svg#gh-light-mode-only" width="400px"></img>
<img src="assets/Floorp_Logo_f10n_Dark.svg#gh-dark-mode-only" width="400px"></img>
</p>

This repository hosts the localization files for Floorp, which have been sourced from Crowdin. It also include main [English localization](https://github.com/Floorp-Projects/Unified-l10n-central/blob/main/en-US/floorp.ftl).

## Improving the English Localization

If you notice any issues with the English localization, you can modify or fix it by following these steps:

1. Fork this repository by clicking the [Fork](https://github.com/Floorp-Projects/Floorp-12/fork) button.

2. Clone your forked repository to your local machine using the following command:

```bash
git clone https://github.com/{YOUR_USERNAME}/Floorp-12.git
```

3. Create a new branch for your improvements using the following command:

```bash
git checkout -b your_branch
```

4. Edit `en-US.json` listed in locales dir https://github.com/Floorp-Projects/Floorp-12/blob/main/src/apps/i18n-supports/translation-targets.json.

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

[Create Pull Request](https://github.com/Floorp-Projects/Unified-l10n-central/compare)

# Contributing to other translation

✅ If you are fluent in a language and want to help translate Floorp Browser, we invite you to be part of our Crowdin translation project.

🌎 [Get started on Crowdin](https://crowdin.com/project/floorp-browser) and contribute to making Floorp accessible in your language.

🙏 Your support in this effort is greatly appreciated. Let's make Floorp available to even more people worldwide!

# Main Repository

[![Link to Main Repository](assets/Link2MainRepo.svg)](https://github.com/Floorp-Projects/Floorp)
