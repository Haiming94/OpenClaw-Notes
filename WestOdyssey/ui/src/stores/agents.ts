export interface AgentDef {
  id: string
  name: string
  emoji: string
  avatar?: string
  color: string
  description: string
  role: string
}

export const RESEARCH_AGENTS: AgentDef[] = [
  {
    id: 'sanzang',
    name: '唐僧',
    emoji: '🧘',
    avatar: '/avatars/sanzang.png',
    color: '#64B5F6',
    description: '科研战略与方向规划，定义研究问题、制定计划、协调优先级',
    role: '战略规划',
  },
  {
    id: 'wukong',
    name: '孙悟空',
    emoji: '💻',
    avatar: '/avatars/wukong.png',
    color: '#4DD0E1',
    description: '算法开发与编程实现，编写调试代码、构建实验 pipeline、训练模型',
    role: '算法开发',
  },
  {
    id: 'wuneng',
    name: '猪八戒',
    emoji: '✍️',
    avatar: '/avatars/wuneng.png',
    color: '#81C784',
    description: '学术写作与项目申报，撰写论文、润色语言、撰写基金申请书',
    role: '学术写作',
  },
  {
    id: 'wujing',
    name: '沙僧',
    emoji: '📚',
    avatar: '/avatars/wujing.png',
    color: '#7986CB',
    description: '文献管理与知识整合，系统性检索文献、构建知识库、生成综述',
    role: '文献管理',
  },
  {
    id: 'horse',
    name: '白龙马',
    emoji: '⚙️',
    avatar: '/avatars/horse.png',
    color: '#4DB6AC',
    description: '数据工程与流程自动化，自动化 workflow、管理计算资源、处理杂事',
    role: '数据工程',
  },
]

export const COORDINATOR_AGENT: AgentDef = {
  id: 'coordinator',
  name: '学术讨论空间',
  emoji: '🏛️',
  color: '#26C6DA',
  description: '科研团队学术讨论空间，负责任务分发、协调和汇总',
  role: '协调中心',
}

export const ALL_AGENTS: AgentDef[] = [...RESEARCH_AGENTS, COORDINATOR_AGENT]

export function getAgentById(id: string): AgentDef | undefined {
  return ALL_AGENTS.find((a) => a.id === id)
}
