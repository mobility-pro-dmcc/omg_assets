<p>The following items have dropped below their safety stock levels:</p>

<ul>
{% for row in doc.flags.low_stock_items %}
    <li><strong>Item:</strong> {{ row[1] }} | <strong>Warehouse:</strong> {{ row[0] }} | <strong>Current Balance:</strong> {{ row[2] }}</li>
{% endfor %}
</ul>
