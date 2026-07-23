# Open Road Code Website

Starter GitHub Pages site for [Open Road Code](https://openroadcode.org).

## Local preview

Install Ruby and Bundler, then run:

```bash
bundle install
bundle exec jekyll serve
```

Open `http://localhost:4000`.

## Generated documentation

The Pages workflow publishes two documentation sets:

- `/docs/` contains guides imported from every `README.md` in OpenRoadCode.
- `/api/` contains Doxygen HTML generated from every Python file in
  OpenRoadCode.

To generate the API reference locally, install Doxygen and run:

```bash
DOXYGEN_INPUT_DIRECTORY=/path/to/OpenRoadCode \
DOXYGEN_OUTPUT_DIRECTORY=/tmp/openroadcode-doxygen \
doxygen Doxyfile
```

Open `/tmp/openroadcode-doxygen/html/index.html`.

The Doxygen build uses the custom files in `doxygen/` to share the main site's
header, footer, colors, and typography.

## GitHub Pages deployment

1. Create a GitHub repository, for example `openroadcode-site`.
2. Push this project to the repository.
3. Open **Settings → Pages**.
4. Set **Build and deployment** to **Deploy from a branch**.
5. Select the `main` branch and `/ (root)`.
6. Save.
7. Add `openroadcode.org` as the custom domain.
8. Update the placeholder GitHub links in `index.html`.

## Cloudflare DNS

For an apex domain pointing to GitHub Pages, add GitHub's current Pages A/AAAA
records in Cloudflare. For `www`, add a CNAME to your GitHub Pages hostname.
Confirm the current required DNS values in GitHub's documentation before
publishing.

## Notes

- The current site is intentionally a single-page first iteration.
- The included logo is stored at `assets/images/open-road-code-logo.png`.
- Replace `href="#"` placeholders with the actual GitHub repository URL.
