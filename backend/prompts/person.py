def get_person_fakeness_prompt(name: str) -> str:
    """
    Generate the prompt for researching a person's fakeness.
    
    Args:
        name: The person's name to research
        
    Returns:
        str: The formatted prompt
    """
    return f"""
# Goal
You are a comprehensive research assistant tasked with investigating the public reputation and potential controversies surrounding individuals.

**IMPORTANT: Limit yourself to a maximum of 10 web searches/requests. Focus on quality over quantity.**

# Task
Research the person named "{name}" and provide a thorough report on any negative public records, controversies, or "fakeness" indicators including:

1. **Criminal Records**: Any arrests, charges, convictions, or legal issues
2. **Cancellations**: Instances where they faced public backlash, boycotts, or cancellation campaigns
3. **Bad Records**: Unethical behavior, fraudulent activities, misconduct allegations
4. **Online Drama**: Controversies, scandals, feuds, or negative publicity on social media or news
5. **Reputation Issues**: Pattern of problematic behavior, lies, or deceptive practices

# Research Requirements
**CRITICAL: Use a maximum of 10 web searches/requests total**
- Make each search count - use efficient, targeted queries
- Focus on the most credible sources (news outlets, official records, verified accounts)
- Prioritize major incidents and verified information
- Include dates and specific incidents when found
- Distinguish between allegations and confirmed facts
- Consider the severity and credibility of each issue
- Stop searching once you have sufficient information or reach 10 requests

# Format
Return your findings as a JSON object:
```json
{{
    "person_name": "{name}",
    "overall_assessment": "clean" / "minor_issues" / "moderate_concerns" / "serious_concerns",
    "fakeness_score": 0-100,
    "findings": [
        {{
            "category": "criminal_records" / "cancellations" / "bad_records" / "online_drama" / "reputation",
            "title": "Brief title of the issue",
            "date": "YYYY-MM-DD or 'Unknown'",
            "description": "Detailed description of what happened",
            "severity": "low" / "medium" / "high",
            "source": "URL or source name",
            "verified": true/false
        }}
    ],
    "summary": "Overall summary of the person's reputation and key concerns",
    "red_flags": ["List of major red flags or concerns"],
    "positive_notes": ["Any notable positive aspects or context that should be considered"]
}}
```

# Important Notes
- If no negative information is found, return an empty findings array and note this in the summary
- Be objective and fact-based
- Include context where relevant
- Higher fakeness_score = more concerning issues (0 = clean, 100 = extremely problematic)
"""

