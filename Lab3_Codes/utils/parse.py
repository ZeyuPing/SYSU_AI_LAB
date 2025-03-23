def split_literals(clause_str):
    """
    拆分字面量，确保谓词内部的逗号不被拆分
    """
    literals = []
    current = ""
    paren_count = 0
    for char in clause_str:
        if char == '(':
            paren_count += 1
            current += char
        elif char == ')':
            paren_count -= 1
            current += char
        elif char == ',' and paren_count == 0:
            if current.strip():
                literals.append(current.strip())
            current = ""
        else:
            current += char
    if current.strip():
        literals.append(current.strip())
    return literals


def Parse_for_FOL(KB):
    """
    改进版解析函数，能够正确处理谓词内部逗号。
    返回：set[tuple[str]]
    """
    kb_str = KB.strip()
    if kb_str[0] == '{' and kb_str[-1] == '}':
        kb_str = kb_str[1:-1].strip()
    clauses = []
    current_clause = ""
    paren_count = 0
    for char in kb_str:
        if char == '(':
            if paren_count == 0:
                current_clause = ""
            else:
                current_clause += char
            paren_count += 1
        elif char == ')':
            paren_count -= 1
            if paren_count == 0:
                clauses.append(current_clause.strip())
                current_clause = ""
            else:
                current_clause += char
        else:
            if paren_count > 0:
                current_clause += char
    clause_set = set()
    for clause in clauses:
        if clause.endswith(','):
            clause = clause[:-1].strip()
        literals = split_literals(clause)
        clause_set.add(tuple(literals))
    return clause_set

def Parse_for_PC(KB):
    """
    将命题逻辑知识库字符串解析为子句集（集合中每个子句为 tuple[str]）。
    例如：
      KB = "{(FirstGrade,),(~FirstGrade,Child),(~Child,)}"
    返回：
      {('FirstGrade',), ('~FirstGrade','Child'), ('~Child',)}
    """
    KB = KB.strip()
    if KB[0] == '{' and KB[-1] == '}':
        KB = KB[1:-1]
    clause_strs = []
    current = ""
    paren = 0
    for char in KB:
        if char == '(':
            paren += 1
            current += char
        elif char == ')':
            paren -= 1
            current += char
            if paren == 0:
                clause_strs.append(current)
                current = ""
        else:
            if paren > 0:
                current += char
    clauses = []
    for s in clause_strs:
        s = s.strip()[1:-1]  # 去掉外层括号
        # 根据逗号拆分，但过滤掉空串
        lits = [lit.strip() for lit in s.split(",") if lit.strip() != ""]
        clauses.append(tuple(lits))
    return set(clauses)
    