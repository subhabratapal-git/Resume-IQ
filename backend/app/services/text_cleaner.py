import re


def clean_resume_text(text: str) -> str:

    # Convert line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Join words broken by hyphen + line break
    # Example: "model-\ning" -> "modeling"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Remove extra spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces around line breaks
    text = re.sub(r" *\n *", "\n", text)

    # Remove multiple blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    # Add space after bullet symbol
    # Example: "•Languages" -> "• Languages"
    text = re.sub(r"•\s*", "• ", text)

    # Add space after colon (but not in URLs like https://)
    # Example: "Languages:C" -> "Languages: C"
    text = re.sub(r":(?!//|\s|$)(?=\S)", ": ", text)

    # Fix common PDF extraction issues
    replacements = {
        "T echnology": "Technology",
        "F rontend": "Frontend",
        "F undamentals": "Fundamentals",
        "F rameworks": "Frameworks",
        "T ools": "Tools",
        "T racking": "Tracking",
        "T ask": "Task",
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    # Fix missing spaces before years
    text = re.sub(
        r"(Engineering|Technology|Python)(20\d{2})",
        r"\1 \2",
        text
    )

    # Fix "PythonSept" -> "Python Sept"
    text = re.sub(
        r"(Python)(Sept)",
        r"\1 \2",
        text
    )

    return text.strip()