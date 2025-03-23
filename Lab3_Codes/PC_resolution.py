from utils.parse import Parse_for_PC

def complementary(lit1, lit2):
    """
    判断两个文字是否互补：
      如果 lit1 == L 且 lit2 == "~"+L，或反之，则返回 True。
    """
    if lit1.startswith("~") and lit1[1:] == lit2:
        return True
    if lit2.startswith("~") and lit2[1:] == lit1:
        return True
    return False

def resolve_pair(clause1, clause2):
    """
    尝试对两个子句进行归结。
    对于每一对满足互补条件的文字，产生一个归结子句：
      resolvent = (clause1 ∪ clause2) - {L, complement(L)}
    返回一个列表，每个元素为 (resolvent, parent, child_letter_index)：
      - resolvent：新子句（tuple[str]），其中字面量顺序按原来子句顺序拼接后去重。
      - parent：表示使用了哪一个父子句记录了待标记的公式，
        这里约定：如果 clause1 中的文字是正（不以 "~" 开头），则我们选择 clause2 中对应的否定文字，
        否则选择 clause1 中对应文字。
      - child_letter_index：所使用父子句中该文字的下标（0→a,1→b,…）。
    如果有多个可能，本函数返回所有可能归结的情况。
    """
    results = []
    # 我们遍历 clause1 和 clause2 中所有文字组合
    for i, lit1 in enumerate(clause1):
        for j, lit2 in enumerate(clause2):
            if complementary(lit1, lit2):
                # 决定记录哪一侧的下标：
                # 如果 lit1 不以 "~"开头，则 lit1 为正，lit2 为负，记录 clause2 的文字下标 j
                if not lit1.startswith("~"):
                    letter_index = j
                    # 归结产生的新子句：去掉 lit1 和 lit2
                    new_clause = list(clause1) + list(clause2)
                    new_clause.remove(lit1)
                    new_clause.remove(lit2)
                    # 去除重复（保持原来顺序）：
                    seen = set()
                    res = []
                    for lit in new_clause:
                        if lit not in seen:
                            seen.add(lit)
                            res.append(lit)
                    results.append((tuple(res), (clause1, clause2), letter_index))
                # 否则，如果 lit1 为负，则 lit2 为正，记录 clause1 中的文字下标 i
                elif not lit2.startswith("~"):
                    letter_index = i
                    new_clause = list(clause1) + list(clause2)
                    new_clause.remove(lit1)
                    new_clause.remove(lit2)
                    seen = set()
                    res = []
                    for lit in new_clause:
                        if lit not in seen:
                            seen.add(lit)
                            res.append(lit)
                    results.append((tuple(res), (clause2, clause1), letter_index))
    return results

def lit_index_to_letter(idx):
    """将数字下标转换为字母：0->a, 1->b, ..."""
    return chr(97 + idx)

def PC_resolution(KB):
    """命题逻辑归结：返回最小推理树（仅保留必要步骤，并重新编号）。"""
    clauses = Parse_for_PC(KB)
    resolution_steps = []
    clause_history = {}
    step = 1
    
    # 记录初始子句（保持原编号）
    for cl in sorted(clauses, key=lambda x: str(x)):
        clause_history[cl] = step
        resolution_steps.append(f"{step} {cl}")
        step += 1

    inferred = set(clauses)
    derivation_map = {}  # 记录归结生成的子句 -> 其前驱
    empty_clause_found = False

    while not empty_clause_found:
        new_clauses = []
        current_clauses = list(inferred)

        for i in range(len(current_clauses)):
            for j in range(i+1, len(current_clauses)):
                c1 = current_clauses[i]
                c2 = current_clauses[j]
                resolvents = resolve_pair(c1, c2)

                for resolvent, (parent1, parent2), letter_index in resolvents:
                    if resolvent not in inferred:
                        # 记录归结路径
                        derivation_map[resolvent] = (parent1, parent2, letter_index)
                        inferred.add(resolvent)
                        new_clauses.append(resolvent)

                        if resolvent == ():
                            empty_clause_found = True
                            break
            if empty_clause_found:
                break
        if not new_clauses:
            break

    # **回溯最小推理树**
    if () not in derivation_map:
        return resolution_steps  # 无法推出空子句，返回所有初始子句

    # **从空子句回溯，重新编号**
    used_clauses = set()
    backtrace = [()]
    renumbered_history = {}
    step = 1

    while backtrace:
        clause = backtrace.pop()
        if clause in renumbered_history:
            continue
        renumbered_history[clause] = step
        used_clauses.add(clause)
        step += 1
        if clause in derivation_map:
            backtrace.append(derivation_map[clause][0])
            backtrace.append(derivation_map[clause][1])

    # 修改最终步骤的构造部分
    final_steps = []
    all_steps = []
    
    # 收集所有需要的步骤（包括初始子句和归结步骤）
    for clause, num in clause_history.items():
        if clause in used_clauses:
            all_steps.append(('init', clause, None, None, None))
            
    for clause, (p1, p2, letter_index) in derivation_map.items():
        if clause in used_clauses:
            all_steps.append(('res', clause, p1, p2, letter_index))
    
    # 按照推理的依赖关系重新排序
    step = 1
    processed = set()
    while len(processed) < len(all_steps):
        for step_info in all_steps:
            if step_info[0] == 'init':
                if step_info[1] not in processed:
                    processed.add(step_info[1])
                    clause = step_info[1]
                    renumbered_history[clause] = step
                    final_steps.append(f"{step} {clause}")
                    step += 1
            elif step_info[0] == 'res':
                clause, p1, p2, letter_index = step_info[1:]
                if (p1 in processed and p2 in processed and 
                    clause not in processed):
                    processed.add(clause)
                    p1_num = renumbered_history[p1]
                    p2_num = renumbered_history[p2]
                    letter = lit_index_to_letter(letter_index)
                    final_steps.append(f"{step} R[{p1_num},{p2_num}{letter}] = {clause}")
                    renumbered_history[clause] = step
                    step += 1
    
    return final_steps
