class ProblemModel:
    def __init__(self):
        self.objectives = []  # 存储目标函数
        self.constraints = []  # 存储约束
        self.global_constraints = []
    
    def set_global_constraints(self, constraints):
        self.global_constraints = constraints
    
    def add_objective(self, name, expression, maximize=True,description=None, weight=1.0):
        """添加目标函数，支持参数化定义"""
        objective_def = {
            'name': name,
            'expression': expression,
            'maximize': maximize,
            'description': description,
            'weight': weight
        }
        self.objectives.append(objective_def)
    
    def remove_objective(self, name):
        self.objectives = [obj for obj in self.objectives if obj['name'] != name]

    def update_objective(self, name, expression, maximize=True,description=None, old_name=None, weight=1.0):
        """更新目标函数，支持参数化定义"""
        self.remove_objective(old_name)
        self.add_objective(name, expression, maximize, description, weight)

    def add_constraint(self, name, lhs, constraint_type, rhs, description=None, is_hard_constraint=True):
        constraint_def = {
            'name': name,
            'lhs': lhs,
            'constraint_type': constraint_type,
            'rhs': rhs,
            'description': description,
            'is_hard_constraint': is_hard_constraint,   
        }
        
        self.constraints.append(constraint_def)

    def remove_constraint(self, name):
        """根据描述删除约束"""
        self.constraints = [constr for constr in self.constraints if constr['name'] != name]

    def update_constraint(self, old_name, name, lhs, constraint_type, rhs, description=None, is_hard_constraint=True):
        """更新约束，支持参数化定义"""
        self.remove_constraint(old_name)
        self.add_constraint(name, lhs, constraint_type, rhs, description, is_hard_constraint)
    
    def set_problem_model(self, problem_model):
        for obj in problem_model.get("objectives", []):
            self.add_objective(
                name=obj.get('name'),
                expression=obj.get('expression'),
                maximize=(obj.get('objective_type') == 'maximize'),
                description=obj.get('description'),
                weight=obj.get('weight', 1.0),
            )
        for constr in problem_model.get("constraints", []):
            self.add_constraint(
                name=constr['name'],
                lhs=constr.get('lhs'),
                constraint_type=constr['constraint_type'],
                rhs=constr['rhs'],
                description=constr.get('description'),
                is_hard_constraint=constr.get('is_hard_constraint', True),
            )
            
    def update_problem_model(self, problem_model):
        # 更新目标函数
        for obj_update in problem_model.get("updated_objectives", []):
            if obj_update['type'] == 'add':
                self.add_objective(
                    name=obj_update.get('name'),
                    expression=obj_update.get('expression'),
                    maximize=(obj_update['objective_type'] == 'maximize'),
                    description=obj_update.get('description'),
                    weight=obj_update.get('weight', 1.0),
                )
            elif obj_update['type'] == 'delete':
                self.remove_objective(obj_update['old_name'])
            elif obj_update['type'] == 'update':
                self.update_objective(
                    name=obj_update.get('name'),
                    expression=obj_update.get('expression'),
                    maximize=(obj_update['objective_type'] == 'maximize'),
                    description=obj_update.get('description'),
                    old_name=obj_update['old_name'],
                    weight=obj_update.get('weight', 1.0),
                )

        # 更新约束
        for constr_update in problem_model.get("updated_constraints", []):
            if constr_update['type'] == 'add':
                self.add_constraint(
                    name=constr_update['name'],
                    lhs=constr_update.get('lhs'),
                    constraint_type=constr_update['constraint_type'],
                    rhs=constr_update['rhs'],
                    description=constr_update.get('description'),
                    is_hard_constraint=constr_update.get('is_hard_constraint', True),
                )
            elif constr_update['type'] == 'delete':
                self.remove_constraint(constr_update['old_name'])
            elif constr_update['type'] == 'update':
                self.update_constraint(
                    old_name=constr_update['old_name'],
                    name=constr_update['name'],
                    lhs=constr_update.get('lhs'),
                    constraint_type=constr_update['constraint_type'],
                    rhs=constr_update['rhs'],
                    description=constr_update.get('description'),
                    is_hard_constraint=constr_update.get('is_hard_constraint', True),
                )


