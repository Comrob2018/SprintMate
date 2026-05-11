# DELETE this:
if desc_text:
    fields["description"] = {
        "type": "doc", "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": desc_text}]}]
    }

# REPLACE with this:
if desc_text:
    fields["description"] = desc_text
