def parse_predicate(formula):
    pred_name = formula[:formula.find('(')]
    args_str = formula[formula.find('(')+1:formula.rfind(')')]
    args = []
    current = ""
    parentheses = 0
    for c in args_str:
        if c == '(':
            parentheses += 1
            current += c
        elif c == ')':
            parentheses -= 1
            current += c
        elif c == ',' and parentheses == 0:
            args.append(current.strip())
            current = ""
        else:
            current += c
    if current:
        args.append(current.strip())
    return pred_name, args

def is_variable(term):
    """
    判断是否为变量:
    1. 两个重复的小写字母 (如 xx, yy, zz)
    2. 单个小写字母 x, y, z
    其余均为常量
    """
    if len(term) == 2 and term[0] == term[1] and term[0].islower():
        return True
    if len(term) == 1 and term in 'xyz':
        return True
    return False

def occurs_check(var, term, subst):
    if var == term:
        return True
    if term in subst:
        return occurs_check(var, subst[term], subst)
    if '(' in term:
        _, args = parse_predicate(term)
        return any(occurs_check(var, arg, subst) for arg in args)
    return False

def apply_subst(term, subst):
    if term in subst:
        return apply_subst(subst[term], subst)
    if '(' in term:
        pred, args = parse_predicate(term)
        new_args = [apply_subst(arg, subst) for arg in args]
        return f"{pred}({','.join(new_args)})"
    return term

def MGU(formula1, formula2):
    pred1, args1 = parse_predicate(formula1)
    pred2, args2 = parse_predicate(formula2)
    if pred1 != pred2 or len(args1) != len(args2):
        return None
    substitution = {}
    pairs = list(zip(args1, args2))
    while pairs:
        s, t = pairs.pop(0)
        s = apply_subst(s, substitution)
        t = apply_subst(t, substitution)
        if s != t:
            if is_variable(s):
                if occurs_check(s, t, substitution):
                    return None
                substitution[s] = t
            elif is_variable(t):
                if occurs_check(t, s, substitution):
                    return None
                substitution[t] = s
            elif '(' in s and '(' in t:
                pred_s, args_s = parse_predicate(s)
                pred_t, args_t = parse_predicate(t)
                if pred_s != pred_t or len(args_s) != len(args_t):
                    return None
                pairs.extend(zip(args_s, args_t))
            else:
                return None
    return substitution
