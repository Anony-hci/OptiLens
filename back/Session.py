class Session:
    def __init__(self, current_preference, messages, problem_model, model_nodes, features_exprs, action_logs=None):
        self.current_preference = current_preference
        self.messages = messages
        self.problem_model = problem_model
        self.model_nodes = model_nodes
        self.features_exprs = features_exprs
        self.action_logs = action_logs if action_logs is not None else []