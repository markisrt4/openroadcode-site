---
layout: default
title: Documentation
permalink: /docs/
---

<section class="section documentation-index">
  <div class="container">
    <p class="section-label">Project Documentation</p>
    <h1>Open Road Code Documentation</h1>

    <p class="documentation-index__intro">
      Browse guides imported from README files in the Open Road Code source
      repository, or explore the generated Python API reference.
    </p>

    <p>
      <a class="button button--primary" href="{{ '/api/' | relative_url }}">
        Browse the API Reference
      </a>
    </p>

    <h2 class="documentation-index__heading">Project Guides</h2>

    <nav
      class="documentation-tree"
      aria-label="Open Road Code documentation"
    >
      {% include docs-tree.html
        nodes=site.data.docs_tree
        level=0
      %}
    </nav>
  </div>
</section>
