# Open Road Code Website

Starter GitHub Pages site for [Open Road Code](https://openroadcode.org).

## Local preview

Install Ruby and Bundler, then run:

```bash
bundle install
bundle exec jekyll serve
```

Open `http://localhost:4000`.

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
