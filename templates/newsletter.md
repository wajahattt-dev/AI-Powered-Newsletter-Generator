# {{newsletter_title}}

## {{newsletter_subtitle}}

*Generated on: {{generation_date}}*

---

{% if introduction %}
## Today's Highlights

{{introduction}}

---
{% endif %}

{% for category, articles in articles_by_category.items() %}
## {{category|title}}

{% for article in articles %}
### [{{article.title}}]({{article.url}})

*Source: {{article.source}} | Published: {{article.published_date}}*

{% if article.image_url and include_images %}
![{{article.title}}]({{article.image_url}})
{% endif %}

{{article.summary}}

{% if article.key_points %}
**Key Points:**
{% for point in article.key_points %}
- {{point}}
{% endfor %}
{% endif %}

{% if article.quotes and include_quotes %}
**Notable Quotes:**
{% for quote in article.quotes %}
> {{quote}}
{% endfor %}
{% endif %}

{% if include_links %}
[Read full article]({{article.url}})
{% endif %}

---
{% endfor %}
{% endfor %}

## About This Newsletter

This newsletter was automatically generated based on your interests:
{% for interest in user_interests %}
- {{interest}}
{% endfor %}

*Powered by Auto-Newsletter Generator*