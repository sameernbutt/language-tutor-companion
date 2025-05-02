import re

def find_duplicate_css_labels(css_file_path):
    """
    Reads a CSS file and prints out any duplicate labels (selectors).

    Args:
        css_file_path (str): The path to the CSS file.
    """
    labels = {}
    duplicates = set()

    try:
        with open(css_file_path, 'r') as f:
            content = f.read()

        # Regex to find CSS selectors (labels)
        # This regex tries to capture various selector types:
        # - Element selectors (e.g., body, div)
        # - Class selectors (e.g., .container, .button)
        # - ID selectors (e.g., #header, #main-content)
        # - Attribute selectors (e.g., [type="text"], [data-value])
        # - Pseudo-classes (e.g., :hover, :focus)
        # - Pseudo-elements (e.g., ::before, ::after)
        # It aims to be reasonably comprehensive but might need adjustments
        # based on the complexity of your CSS.
        selector_pattern = r"([a-zA-Z0-9.#\[\]='\"-]+(?:[:]{1,2}[a-zA-Z0-9-]+)*)\s*\{"
        matches = re.findall(selector_pattern, content)

        for label in matches:
            cleaned_label = label.strip()  # Remove leading/trailing whitespace
            if cleaned_label in labels:
                duplicates.add(cleaned_label)
            else:
                labels[cleaned_label] = 1

        if duplicates:
            print("Duplicate CSS labels found:")
            for duplicate in duplicates:
                print(f"- {duplicate}")
        else:
            print("No duplicate CSS labels found.")

    except FileNotFoundError:
        print(f"Error: File not found at '{css_file_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
css_file = "styles.css"  # Replace with the actual path to your CSS file
find_duplicate_css_labels(css_file)