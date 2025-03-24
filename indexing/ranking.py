def calculate_rank(content, keyword, links):
    keyword_occurrences = content.lower().count(keyword.lower())
    content_length = len(content)
    link_score = len(links)

    rank = (keyword_occurrences * 2) + (content_length * 0.1) + (link_score * 1.5)

    return rank
