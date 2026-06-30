import re

def validate_sql_safety(sql: str) -> bool:
    """
    Validates that the SQL query is read-only, only uses SELECT or WITH,
    and blocks dangerous commands (e.g. INSERT, UPDATE, DELETE, DROP, etc.)
    """
    if not sql:
        return False

    # Remove comments (single line and block comments)
    clean_sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    clean_sql = re.sub(r'/\*.*?\*/', '', clean_sql, flags=re.DOTALL)
    
    # Tokenize words to inspect keywords
    tokens = re.findall(r'\b\w+\b', clean_sql.upper())
    
    disallowed_keywords = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", 
        "TRUNCATE", "GRANT", "REVOKE", "REPLACE", "UPSERT"
    }
    
    for token in tokens:
        if token in disallowed_keywords:
            return False
            
    # The statement must strictly start with SELECT or WITH
    first_word_match = re.match(r'^\s*(\w+)', clean_sql, re.IGNORECASE)
    if not first_word_match:
        return False
        
    first_word = first_word_match.group(1).upper()
    return first_word in {"SELECT", "WITH"}
