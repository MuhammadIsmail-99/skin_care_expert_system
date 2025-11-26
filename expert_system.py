# ============================================================================
# FILE 1: expert_system.py
# Core Expert System Engine (Updated without comments)
# ============================================================================

import json
from sympy import symbols, sympify, And, Or, Not, Implies
from sympy.logic.boolalg import Boolean
from typing import Dict, List, Tuple, Any
from copy import deepcopy


class ExpertSystem:
    
    def __init__(self, kb_file: str = None):
        self.rules = []
        self.working_memory = {}
        self.fired_rules = []
        self.symbol_cache = {}
        
        if kb_file:
            self.load_knowledge_base(kb_file)
    
    def load_knowledge_base(self, kb_file: str):
        with open(kb_file, 'r') as f:
            rules_data = json.load(f)
        
        self.rules = []
        for rule_data in rules_data:
            rule = {
                'rule_id': rule_data['rule_id'],
                'if_text': rule_data['if_text'],
                'then_concl': rule_data['then_concl'],
                'antecedent_logic': self._parse_logic(rule_data['antecedent_logic']),
                'cf': float(rule_data['cf']),
                'priority': int(rule_data['priority'])
            }
            self.rules.append(rule)
        
        self.rules.sort(key=lambda r: r['priority'], reverse=True)
        print(f"✓ Loaded {len(self.rules)} rules from {kb_file}")
    
    def _parse_logic(self, logic_str: str) -> Boolean:
        import re
        symbol_names = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', logic_str)
        
        keywords = {'And', 'Or', 'Not', 'Implies', 'Equivalent', 'Xor', 'True', 'False'}
        symbol_names = [s for s in symbol_names if s not in keywords]
        
        for name in symbol_names:
            if name not in self.symbol_cache:
                self.symbol_cache[name] = symbols(name)
        
        local_dict = self.symbol_cache.copy()
        local_dict.update({'And': And, 'Or': Or, 'Not': Not, 'Implies': Implies})
        
        return sympify(logic_str, locals=local_dict)
    
    def _get_symbol(self, name: str):
        if name not in self.symbol_cache:
            self.symbol_cache[name] = symbols(name)
        return self.symbol_cache[name]
    
    def set_fact(self, fact_name: str, cf: float):
        symbol = self._get_symbol(fact_name)
        self.working_memory[symbol] = max(-1.0, min(1.0, cf))
    
    def get_fact_cf(self, fact_name: str) -> float:
        symbol = self._get_symbol(fact_name)
        return self.working_memory.get(symbol, 0.0)
    
    def evaluate_expression(self, expr: Boolean) -> float:
        if expr in self.working_memory:
            return self.working_memory[expr]
        
        if isinstance(expr, And):
            cfs = [self.evaluate_expression(arg) for arg in expr.args]
            return min(cfs)
        
        elif isinstance(expr, Or):
            cfs = [self.evaluate_expression(arg) for arg in expr.args]
            return max(cfs)
        
        elif isinstance(expr, Not):
            return -self.evaluate_expression(expr.args[0])
        
        elif isinstance(expr, Implies):
            antecedent_cf = self.evaluate_expression(expr.args[0])
            consequent_cf = self.evaluate_expression(expr.args[1])
            
            if antecedent_cf > 0.5:
                return consequent_cf
            return 0.0
        
        return self.working_memory.get(expr, 0.0)
    
    def combine_cf(self, cf1: float, cf2: float) -> float:
        if cf1 > 0 and cf2 > 0:
            return cf1 + cf2 * (1 - cf1)
        elif cf1 < 0 and cf2 < 0:
            return cf1 + cf2 * (1 + cf1)
        else:
            return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))
    
    def forward_chaining(self, threshold: float = 0.3, max_iterations: int = 100):
        print("\n=== FORWARD CHAINING ===")
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            rules_fired = False
            
            for rule in self.rules:
                antecedent_cf = self.evaluate_expression(rule['antecedent_logic'])
                
                if antecedent_cf >= threshold:
                    conclusion_cf = antecedent_cf * rule['cf']
                    
                    concl_symbol = self._get_symbol(rule['then_concl'])
                    
                    if concl_symbol in self.working_memory:
                        old_cf = self.working_memory[concl_symbol]
                        new_cf = self.combine_cf(old_cf, conclusion_cf)
                        self.working_memory[concl_symbol] = new_cf
                        
                        if abs(new_cf - old_cf) > 0.01:
                            rules_fired = True
                            self.fired_rules.append({
                                'iteration': iteration,
                                'rule_id': rule['rule_id'],
                                'if_text': rule['if_text'],
                                'conclusion': rule['then_concl'],
                                'antecedent_cf': round(antecedent_cf, 3),
                                'conclusion_cf': round(new_cf, 3)
                            })
                            print(f"  [{iteration}] Fired {rule['rule_id']}: "
                                  f"{rule['then_concl']} = {new_cf:.3f}")
                    else:
                        self.working_memory[concl_symbol] = conclusion_cf
                        rules_fired = True
                        self.fired_rules.append({
                            'iteration': iteration,
                            'rule_id': rule['rule_id'],
                            'if_text': rule['if_text'],
                            'conclusion': rule['then_concl'],
                            'antecedent_cf': round(antecedent_cf, 3),
                            'conclusion_cf': round(conclusion_cf, 3)
                        })
                        print(f"  [{iteration}] Fired {rule['rule_id']}: "
                              f"{rule['then_concl']} = {conclusion_cf:.3f}")
            
            if not rules_fired:
                print(f"\n✓ Converged after {iteration} iterations")
                break
        
        if iteration >= max_iterations:
            print(f"\n⚠ Stopped after {max_iterations} iterations")
    
    def backward_chaining(self, goal: str, threshold: float = 0.3, 
                          depth: int = 0, max_depth: int = 10) -> float:
        if depth == 0:
            print(f"\n=== BACKWARD CHAINING: Goal = {goal} ===")
        
        indent = "  " * depth
        goal_symbol = self._get_symbol(goal)
        
        if goal_symbol in self.working_memory:
            cf = self.working_memory[goal_symbol]
            print(f"{indent}✓ {goal} already known: CF = {cf:.3f}")
            return cf
        
        if depth >= max_depth:
            print(f"{indent}⚠ Max depth reached for {goal}")
            return 0.0
        
        print(f"{indent}? Searching for rules concluding {goal}...")
        
        applicable_rules = [r for r in self.rules if r['then_concl'] == goal]
        
        if not applicable_rules:
            print(f"{indent}✗ No rules found for {goal}")
            return 0.0
        
        max_cf = 0.0
        for rule in applicable_rules:
            print(f"{indent}→ Trying {rule['rule_id']}: {rule['if_text']}")
            
            antecedent_cf = self._backward_eval(rule['antecedent_logic'], 
                                                threshold, depth + 1, max_depth)
            
            if antecedent_cf >= threshold:
                conclusion_cf = antecedent_cf * rule['cf']
                print(f"{indent}  ✓ Rule fired: CF = {conclusion_cf:.3f}")
                max_cf = max(max_cf, conclusion_cf)
                
                self.fired_rules.append({
                    'rule_id': rule['rule_id'],
                    'if_text': rule['if_text'],
                    'conclusion': goal,
                    'antecedent_cf': round(antecedent_cf, 3),
                    'conclusion_cf': round(conclusion_cf, 3)
                })
        
        self.working_memory[goal_symbol] = max_cf
        print(f"{indent}⇒ {goal} = {max_cf:.3f}")
        return max_cf
    
    def _backward_eval(self, expr: Boolean, threshold: float, 
                       depth: int, max_depth: int) -> float:
        if expr in self.working_memory:
            return self.working_memory[expr]
        
        if isinstance(expr, And):
            cfs = [self._backward_eval(arg, threshold, depth, max_depth) 
                   for arg in expr.args]
            return min(cfs)
        
        elif isinstance(expr, Or):
            cfs = [self._backward_eval(arg, threshold, depth, max_depth) 
                   for arg in expr.args]
            return max(cfs)
        
        elif isinstance(expr, Not):
            return -self._backward_eval(expr.args[0], threshold, depth, max_depth)
        
        if hasattr(expr, 'name'):
            return self.backward_chaining(expr.name, threshold, depth, max_depth)
        
        return 0.0
    
    def explain(self):
        print("\n=== EXPLANATION ===")
        if not self.fired_rules:
            print("No rules were fired.")
            return
        
        for i, record in enumerate(self.fired_rules, 1):
            print(f"\n{i}. Rule {record['rule_id']}:")
            print(f"   IF: {record['if_text']}")
            print(f"   THEN: {record['conclusion']}")
            print(f"   Antecedent CF: {record['antecedent_cf']}")
            print(f"   Conclusion CF: {record['conclusion_cf']}")
    
    def display_working_memory(self):
        print("\n=== WORKING MEMORY ===")
        if not self.working_memory:
            print("Empty")
            return
        
        for symbol, cf in sorted(self.working_memory.items(), 
                                 key=lambda x: str(x[0])):
            print(f"  {symbol}: {cf:.3f}")
    
    def reset(self):
        self.working_memory.clear()
        self.fired_rules.clear()
        print("✓ System reset")