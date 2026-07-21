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
      Documentation generated from README files in the Open Road Code
      source repository.
    </p>

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
