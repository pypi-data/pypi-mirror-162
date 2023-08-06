def get_attr(node, attr, default=None):
    keys_lower = {k.lower(): k for k in node.keys()}
    key = keys_lower.get(attr.lower())
    return node.attrib.get(key, default)
