#########################################
# 简单的格式化函数（仅用于未推出空子句时）
#########################################
def format_record(rec, mapping, records):
    clause_str = str(rec["clause"])
    if mapping is None or rec["parents_info"] is None:
        return f"{rec['step']} {clause_str}"
    else:
        p1, p2, idx_i, idx_j, mgu = rec["parents_info"]
        new_p1 = mapping[records[p1]["step"]]
        new_p2 = mapping[records[p2]["step"]]
        subst_str = ""
        if mgu:
            subst_str = "{" + ", ".join(f"{var}={term}" for var, term in mgu.items()) + "}"
        return f"{mapping[rec['step']]} R[{new_p1}{index2letter(idx_i)},{new_p2}{index2letter(idx_j)}]{subst_str} = {clause_str}"

def index2letter(index):
    return chr(97 + index)
