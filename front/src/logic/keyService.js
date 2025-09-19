import { ref } from "vue";
import { getFeatureDisplay } from "./modelNodeService";
import katex from 'katex'
import 'katex/dist/katex.min.css'
// 定义一个响应式的 Set 来存储展开的 keys
export const expandedKeys = ref(new Set());

  // 定义一个函数来切换 key 的展开状态
export const toggleKey = (section, key, messageId = null) => {
    const compositeKey = messageId ? `${section}-${key}-${messageId}` : `${section}-${key}`;
    if (expandedKeys.value.has(compositeKey)) {
      expandedKeys.value.delete(compositeKey);
    } else {
      expandedKeys.value.add(compositeKey);
    }
  };

    // 定义一个函数来检查 key 是否展开
export const isKeyExpanded = (section, key, messageId = null) => {
    // 如果提供了messageId，使用它来创建唯一的key
    const compositeKey = messageId ? `${section}-${key}-${messageId}` : `${section}-${key}`;
    return expandedKeys.value.has(compositeKey);
  };


  export const getObjectiveKey = (objective) => {
    if (objective.type === 'add') {
      return `Add：${objective.objective_type} ${objective.name}`;
    } else if (objective.type === 'delete') {
      return `Delete：${objective.objective_type} ${objective.old_name}`;
    } else if (objective.type === 'update') {
      return `Modify：将 ${objective.objective_type} ${objective.old_name} 修改为 ${objective.objective_type} ${objective.name}`;
    }
    return ''; // Default fallback
  }

  export const getObjectiveValue = (objective) => {
    // 提取函数名和函数体
    let functionName = '';
    let functionBody = '';
    
    // 检查expression是否包含函数定义
    if (objective.expression && objective.expression.includes('def ')) {
      // 提取函数名
      const funcNameMatch = objective.expression.match(/def\s+(\w+)\(/);
      if (funcNameMatch && funcNameMatch[1]) {
        functionName = funcNameMatch[1];
      }
      
      // 分离函数体和results赋值语句
      const expressionLines = objective.expression.split('\n');
      const functionLines = [];
      
      for (const line of expressionLines) {
        if (!line.trim().startsWith('results =')) {
          functionLines.push(line);
        }
      }
      
      functionBody = functionLines.join('\n');
    }
    
    // 构建返回字符串
    if (functionName) {
      return `${objective.objective_type} ${functionName}(items, vars)\n\n${functionBody}`;
    } else {
      return `${objective.objective_type} ${objective.math_expression}`;
    }
  }

  // This method returns the appropriate label for the constraint based on its type
  export const getConstraintKey = (constraint) => {
    const type_mapping = {
      "==": "=",
      ">=": ">=",
      "<=": "<="
    }
    if (constraint.type === 'add') {
      return `Add：${constraint.name}${type_mapping[constraint.constraint_type]}${constraint.rhs}`;
    } else if (constraint.type === 'delete') {
      return `Delete：${constraint.old_name}`;
    } else if (constraint.type === 'update') {
      return `Modify：将 ${constraint.old_name} 修改为 ${constraint.name}${type_mapping[constraint.constraint_type]}${constraint.rhs}`;
    }
    return ''; // Default fallback
  }

  export const getConstraintValue = (constraint) => {
    if (constraint.type == 'delete'){
      return ''
    }
    
    // 处理新格式：constraint.lhs 是对象 (包含 template_id 和 parameters)
    if (constraint.lhs && typeof constraint.lhs === 'object' && constraint.lhs.template_id) {
      // 新的模板格式
      const templateInfo = `模板ID: ${constraint.lhs.template_id}`;
      const parametersInfo = constraint.lhs.parameters ? 
        `参数: ${JSON.stringify(constraint.lhs.parameters, null, 2)}` : 
        '无参数';
      
      return `${templateInfo}\n${parametersInfo}\n\n约束: ${constraint.name} ${constraint.constraint_type} ${constraint.rhs}`;
    }
    
    // 处理旧格式：constraint.lhs 是字符串 (包含函数定义)
    if (constraint.lhs && typeof constraint.lhs === 'string' && constraint.lhs.includes('def ')) {
      // 提取函数名和函数体
      let functionName = '';
      let functionBody = '';
      
      // 提取函数名
      const funcNameMatch = constraint.lhs.match(/def\s+(\w+)\(/);
      if (funcNameMatch && funcNameMatch[1]) {
        functionName = funcNameMatch[1];
      }
      
      // 分离函数体和results赋值语句
      const lhsLines = constraint.lhs.split('\n');
      const functionLines = [];
      
      for (const line of lhsLines) {
        if (!line.trim().startsWith('results =')) {
          functionLines.push(line);
        }
      }
      
      functionBody = functionLines.join('\n');
      
      // 构建返回字符串
      if (functionName) {
        return `${functionName}(items, vars) ${constraint.constraint_type} ${constraint.rhs}\n\n${functionBody}`;
      }
    }
    
    // 其他情况：显示数学表达式或基本信息
    if (constraint.math_expression) {
      return `${constraint.math_expression} ${constraint.constraint_type} ${constraint.rhs}`;
    } else {
      return `${constraint.name} ${constraint.constraint_type} ${constraint.rhs}`;
    }
  }

  export const getFilteredConstraintKey = (constraint) => {
    if (constraint.filter_type === 'item') {
      return `选择课程： ${constraint.item['课程名']} (${constraint.item['主讲教师']}) - ${constraint.item['上课时间']}`;
    } else if (constraint.filter_type === 'feature') {
      return `${getFeatureDisplay(constraint.name)} ${constraint.constraint_type} ${constraint.rhs}`;
    }
    return '';
  }

  export const getPrefObjectiveKey = (objective) => {
    return `${objective.objective_type} ${objective.name}`
  }

  export const getPrefConstraintKey = (constraint) => {
    return getFeatureDisplay(constraint.name).startsWith('选择课程') ? getFeatureDisplay(constraint.name) : `${getFeatureDisplay(constraint.name)} ${constraint.constraint_type} ${constraint.rhs}`
  }

  export const renderMath = (latex) => {
    return katex.renderToString(latex, {
      throwOnError: false,
      displayMode: true
    })
  }
  export const getMathExpression = (expression) => {
    // 检查 math_expression 是否存在且为字符串类型
    if (!expression.math_expression || typeof expression.math_expression !== 'string') {
      console.warn('math_expression is not a valid string:', expression.math_expression);
      return ''; // 返回空字符串作为后备
    }
    
    const rendered_math_expression = renderMath(expression.math_expression);
    return rendered_math_expression;
  }