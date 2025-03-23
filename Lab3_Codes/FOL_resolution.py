from MGU import MGU
from utils.parse import Parse_for_FOL
from utils.record import format_record, index2letter

class Node:
    def __init__(self, clause, parents=None, res_info=None):
        """
        clause: tuple[str] 表示该节点的子句
        parents: list[Node] 父节点列表（初始子句则为空列表）
        res_info: 对于归结节点，记录一个三元组 (idx_i, idx_j, mgu)，表示归结时分别用了父节点中哪个公式及替换情况；
                  对初始节点则为 None。
        """
        self.clause = clause
        self.parents = parents if parents is not None else []
        self.res_info = res_info  # (idx_i, idx_j, mgu) 或 None
        self.new_number = None  # 待重新编号

    def __str__(self):
        return str(self.clause)

#########################################
def resolve(clause1, clause2):
    """
    尝试对两个子句归结，返回：
      resolvents: set[tuple[str]]
      resolution_info: list of (resolvent, mgu, idx_i, idx_j)
    归结只考虑一正一负的情况。
    """
    resolvents = set()
    resolution_info = []
    clause1_list = list(clause1)
    clause2_list = list(clause2)
    for i, lit1 in enumerate(clause1_list):
        lit1 = lit1.strip()
        if not lit1:
            continue
        for j, lit2 in enumerate(clause2_list):
            lit2 = lit2.strip()
            if not lit2:
                continue
            mgu = None
            if lit1[0] == "~" and lit2[0] != "~":
                mgu = MGU(lit1[1:], lit2)
            elif lit1[0] != "~" and lit2[0] == "~":
                mgu = MGU(lit1, lit2[1:])
            else:
                continue
            if mgu is not None:
                new_clause1 = [clause1_list[k] for k in range(len(clause1_list)) if k != i]
                new_clause2 = [clause2_list[k] for k in range(len(clause2_list)) if k != j]
                new_clause = []
                for formula in new_clause1 + new_clause2:
                    new_formula = formula
                    for var, term in mgu.items():
                        new_formula = new_formula.replace(var, term)
                    new_clause.append(new_formula)
                resolvent = tuple(new_clause)
                resolvents.add(resolvent)
                resolution_info.append((resolvent, mgu, i, j))
    return resolvents, resolution_info

#########################################
# 主函数：归结并构造最小归结树重新编号
#########################################
def FOL_resolution(KB):
    """
    1. 先用原有方法构造归结记录（resolution_records），记录中保存原始 step 及父节点信息。
    2. 如果空子句推出，则从空子句记录开始回溯构造归结树（把每个记录转换为独立的 Node 对象）。
    3. 对这棵归结树进行拓扑排序（或 DFS 收集后根据依赖关系排序），重新赋予连续编号。
    4. 根据新的编号构造输出字符串。
    """
    # 第一步：构造归结记录（与之前类似，不做新编号处理）
    clause_set = Parse_for_FOL(KB)
    clause_set = set(tuple(token.strip() for token in clause if token.strip()) for clause in clause_set)

    resolution_records = {}  # 键：子句（tuple），值：记录字典
    clause_history = {}
    orig_step = 1
    for clause in clause_set:
        rec = {"step": orig_step, "clause": clause, "parents_info": None, "is_initial": True}
        resolution_records[clause] = rec
        clause_history[clause] = orig_step
        orig_step += 1

    new_clauses = set()
    empty_clause_record = None
    done = False
    while not done:
        clauses = list(clause_set)
        progress = False
        for i in range(len(clauses)):
            for j in range(i+1, len(clauses)):
                ci = clauses[i]
                cj = clauses[j]
                resolvents, res_info = resolve(ci, cj)
                for resolvent, mgu, idx_i, idx_j in res_info:
                    if resolvent == ():
                        rec = {"step": orig_step, "clause": resolvent,
                               "parents_info": (ci, cj, idx_i, idx_j, mgu),
                               "is_initial": False}
                        resolution_records[resolvent] = rec
                        clause_history[resolvent] = orig_step
                        empty_clause_record = rec
                        orig_step += 1
                        progress = True
                        done = True
                        break
                    if resolvent not in clause_history:
                        rec = {"step": orig_step, "clause": resolvent,
                               "parents_info": (ci, cj, idx_i, idx_j, mgu),
                               "is_initial": False}
                        resolution_records[resolvent] = rec
                        clause_history[resolvent] = orig_step
                        new_clauses.add(resolvent)
                        progress = True
                        orig_step += 1
                if empty_clause_record is not None:
                    break
            if empty_clause_record is not None:
                break
        if empty_clause_record is not None:
            break
        if not progress:
            break
        clause_set.update(new_clauses)
        new_clauses.clear()

    if empty_clause_record is None:
        # 若没有推出空子句，返回所有原始记录（不重新编号）
        all_steps = [format_record(rec, None, resolution_records) for rec in sorted(resolution_records.values(), key=lambda r: r["step"])]
        return all_steps

    # 第二步：从空子句记录回溯构造归结树（转换为 Node 对象）
    memo_nodes = {}
    def build_node(clause):
        if clause in memo_nodes:
            return memo_nodes[clause]
        rec = resolution_records[clause]
        if rec["parents_info"] is None:
            node = Node(clause)
        else:
            p1, p2, idx_i, idx_j, mgu = rec["parents_info"]
            node1 = build_node(p1)
            node2 = build_node(p2)
            node = Node(clause, parents=[node1, node2], res_info=(idx_i, idx_j, mgu))
        memo_nodes[clause] = node
        return node

    empty_node = build_node(empty_clause_record["clause"])

    # 第三步：收集归结树中所有节点（DAG），并对每个节点计算深度（初始节点深度为0）
    all_nodes = {}
    def collect_nodes(node):
        if id(node) in all_nodes:
            return
        all_nodes[id(node)] = node
        for p in node.parents:
            collect_nodes(p)
    collect_nodes(empty_node)

    def compute_depth(node, memo={}):
        if id(node) in memo:
            return memo[id(node)]
        if not node.parents:
            memo[id(node)] = 0
            return 0
        d = max(compute_depth(p, memo) for p in node.parents) + 1
        memo[id(node)] = d
        return d

    for node in all_nodes.values():
        node.depth = compute_depth(node)

    # 第四步：拓扑排序所有节点：简单按 (depth, original step) 排序
    # 为此，我们需要每个节点对应的原始 step，即 resolution_records[node.clause]["step"]
    sorted_nodes = sorted(all_nodes.values(), key=lambda n: (n.depth, resolution_records[n.clause]["step"]))
    # 重新赋予新编号，从1开始连续
    new_mapping = {}
    new_num = 1
    for node in sorted_nodes:
        node.new_number = new_num
        new_mapping[id(node)] = new_num
        new_num += 1

    # 第五步：生成输出。对于初始节点："<new_number> <clause>"  
    # 对于归结节点："<new_number> R[<new_num_parent1><letter>,<new_num_parent2><letter>]{<subst>} = <clause>"
    output_lines = []
    # 为方便查找父节点新编号：查 resolution_records 获取记录，再用 memo_nodes转换
    def format_node(node):
        if not node.parents:  # 初始节点
            return f"{node.new_number} {node.clause}"
        else:
            # 获取对应的记录信息
            rec = resolution_records[node.clause]
            p1, p2, idx_i, idx_j, mgu = rec["parents_info"]
            new_p1 = memo_nodes[p1].new_number
            new_p2 = memo_nodes[p2].new_number
            subst_str = ""
            if mgu:
                subst_str = "{" + ", ".join(f"{var}={term}" for var, term in mgu.items()) + "}"
            return f"{node.new_number} R[{new_p1}{index2letter(idx_i)},{new_p2}{index2letter(idx_j)}]{subst_str} = {node.clause}"
    # 按新编号顺序输出
    for node in sorted_nodes:
        output_lines.append(format_node(node))
    return output_lines





