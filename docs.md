---
layout: default
title: Documentation
permalink: /docs/
---

<section class="section">
  <div class="container">
    <p class="section-label">Project Documentation</p>
    <h1>Open Road Code Documentation</h1>

    <div class="documentation-index">
      {% assign docs = site.docs | sort: "title" %}

      {% if docs.size > 0 %}
        {% for doc in docs %}
          <article class="documentation-card">
            <h2>
              <a href="{{ doc.url | relative_url }}">
                {{ doc.title }}
              </a>
            </h2>

            {% if doc.source_path %}
              <code>{{ doc.source_path }}</code>
            {% endif %}
          </article>
        {% endfor %}
      {% else %}
        <p>No documentation pages were generated.</p>
      {% endif %}
    </div>
  </div>
</section>
