from typing import Dict, List, Any
from dataclasses import dataclass
from uuid import uuid4

@dataclass
class TaskNode:
    """任务节点类，用于存储任务信息
    
    专门处理基于items嵌套的DSL结构，每个节点都可能包含items子节点
    """
    task_id: str                # 任务唯一标识
    node_id: str               # DSL节点ID
    node_type: str            # 节点类型（如app, page, container, text等）
    parent_task_id: str       # 父任务ID
    items: List[str]          # 子任务ID列表（对应DSL中的items）
    properties: Dict[str, Any] # 节点的所有其他属性

class DSLTaskSplitter:
    """DSL任务拆分器 - 专门处理基于items嵌套的DSL结构
    
    将嵌套的DSL结构拆分为平铺的任务队列，每个任务保持其属性和items关系。
    主要特点：
    1. 专注于处理items嵌套结构
    2. 保持节点原有的所有属性
    3. 维护任务间的父子关系
    4. 支持按需获取任务信息
    """
    
    def __init__(self):
        self.tasks: Dict[str, TaskNode] = {}
        self.root_task_id: str = None

    def _extract_node_properties(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """提取节点的所有属性（除了items）
        
        Args:
            node: DSL节点数据
            
        Returns:
            properties: 节点的所有非items属性
        """
        return {k: v for k, v in node.items() if k != 'items'}

    def _create_task_node(self, node: Dict[str, Any], parent_task_id: str = None) -> str:
        """创建任务节点
        
        Args:
            node: DSL节点数据
            parent_task_id: 父任务ID
            
        Returns:
            task_id: 新创建的任务ID
        """
        task_id = str(uuid4())
        
        # 获取items列表（如果存在）
        items = node.get('items', [])
        # 提取其他所有属性
        properties = self._extract_node_properties(node)
        
        # 创建任务节点
        task_node = TaskNode(
            task_id=task_id,
            node_id=node.get('id', ''),
            node_type=node.get('type', ''),
            parent_task_id=parent_task_id,
            items=[],  # 初始化为空列表，后续添加子任务ID
            properties=properties
        )
        
        self.tasks[task_id] = task_node
        
        # 处理items中的每个子节点
        for item in items:
            child_task_id = self._create_task_node(item, task_id)
            task_node.items.append(child_task_id)
            
        return task_id

    def split_dsl(self, dsl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """拆分DSL结构为任务队列
        
        Args:
            dsl_data: DSL数据结构
            
        Returns:
            tasks: 任务队列，每个任务包含完整的属性和items关系
        """
        # 重置状态
        self.tasks.clear()
        self.root_task_id = None
        
        # 创建任务树
        self.root_task_id = self._create_task_node(dsl_data)
        
        # 构建任务队列
        task_queue = []
        for task_id, task_node in self.tasks.items():
            task_info = {
                'task_id': task_id,
                'node_id': task_node.node_id,
                'node_type': task_node.node_type,
                'parent_task_id': task_node.parent_task_id,
                'items': task_node.items,
                'properties': task_node.properties
            }
            task_queue.append(task_info)
            
        return task_queue

    def get_task_by_id(self, task_id: str) -> Dict[str, Any]:
        """根据任务ID获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            task_info: 任务完整信息，包含所有属性和items关系
        """
        if task_id not in self.tasks:
            return None
            
        task_node = self.tasks[task_id]
        return {
            'task_id': task_id,
            'node_id': task_node.node_id,
            'node_type': task_node.node_type,
            'parent_task_id': task_node.parent_task_id,
            'items': task_node.items,
            'properties': task_node.properties
        }

    def get_task_with_children(self, task_id: str) -> Dict[str, Any]:
        """获取任务及其所有子任务的完整信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            task_info: 包含子任务完整信息的任务数据
        """
        task_info = self.get_task_by_id(task_id)
        if not task_info:
            return None
            
        # 递归获取所有子任务信息
        children_info = []
        for child_id in task_info['items']:
            child_info = self.get_task_with_children(child_id)
            if child_info:
                children_info.append(child_info)
                
        task_info['children_info'] = children_info
        return task_info
