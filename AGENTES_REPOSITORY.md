# 🤖 Repositório de Agentes de IA

Um repositório centralizado e bem documentado de agentes de IA, frameworks e ferramentas para automação, desenvolvimento, design e muito mais. Atualizado constantemente conforme descobrimos novos agentes.

**Última atualização:** 18 de Maio de 2026

## 📌 Novos ativos locais (Finance Web)

- **Agent:** `.github/agents/finance-web-temporal-analysis-architect.md`
  - Foco em arquitetura e entrega de análise temporal (MoM/YoY/YTD, tendências e rankings).
- **Skill:** `.github/skills/finance-web-temporal-analysis-delivery/SKILL.md`
  - Playbook de implementação fullstack da seção `/analysis`.
- **Instruções globais:** `.github/copilot-instructions.md`
  - Regras operacionais do Copilot para manter padrão entre backend e frontend.

---

## 📑 Índice

- [⭐ Repositórios Essenciais](#-repositórios-essenciais)
- [Categorias Principais](#categorias-principais)
- [Task & Problem Decomposition](#-task--problem-decomposition---novo)
- [Spec-Driven Development (SDD)](#-spec-driven-development-sdd---novo) ⭐ NOVO
- [Skills Locais do Finance Web](#-skills-locais-do-finance-web) ⭐ NOVO
- [Como Contribuir](#como-contribuir)
- [Comparação Rápida](#comparação-rápida)
- [Guia de Integração](#guia-de-integração)
- [Recursos Adicionais](#recursos-adicionais)

---

## ⭐ Repositórios Essenciais

### **[500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects)** 🔥
- **⭐ Stars:** 28.5k+
- **Linguagem:** Python, Jupyter Notebooks
- **Descrição:** Coleção curada de 500+ casos de uso reais de agentes de IA organizados por **indústria** e **framework**
- **Exclusividade:** É o repositório mais completo para descobrir aplicações práticas
- **O que Inclui:**
  - **20+ indústrias:** Healthcare, Finance, Education, Retail, Manufacturing, Real Estate, Agriculture, Legal, HR, Hospitality, Gaming, Cybersecurity, E-commerce, Logistics, Supply Chain, e mais
  - **4 Frameworks principais:** CrewAI, Autogen, Agno, LangGraph
  - **MindMap visual** dos casos de uso por indústria
  - **Links diretos** para projetos open-source de cada caso de uso
  - **Jupyter Notebooks** com exemplos funcionais
  - **Atualizado frequentemente** (última atualização 3 meses atrás)
- **Exemplos de Casos de Uso:**
  - Healthcare: HIA (Health Insights Agent), AI Health Assistant
  - Finance: Automated Trading Bot, Stock Analysis Tool
  - Education: Virtual AI Tutor, Study Partner, Research Scholar Agent
  - E muito mais...
- **Por Que é Especial:**
  1. Maior coleção de casos de uso práticos
  2. Organizado tanto por **indústria** quanto por **framework**
  3. Links diretos para implementações reais
  4. Código funcional em cada exemplo
  5. Perfeito para validar se seu caso de uso já existe
- **Nível de Complexidade:** ⭐⭐ (Beginner-Intermediário para entender, ⭐⭐⭐⭐ para implementar)
- **Recomendação:** **USE ISTO COMO PRIMEIRA BUSCA** para qualquer caso de uso

---

### **[awesome-design-md](https://github.com/VoltAgent/awesome-design-md)** ⭐⭐⭐
- **⭐ Stars:** 56k+
- **Especialização:** Design Systems para Agentes de IA
- **Diferencial:** Se você quer gerar UIs consistentes com IA, este é o melhor
- **Veja seção [Agentes de Design & UI](#agentes-de-design--ui) para mais detalhes**

---

### **[awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)**
- **⭐ Stars:** 105k+
- **Especialização:** Aplicações LLM e RAG prontas para clonar
- **Diferencial:** Clone, customize e deploy imediatamente
- **Veja seção [Agentes Gerais & Orquestração](#agentes-gerais--orquestração) para mais detalhes**

---

### **[visual-agent-orchestrator](https://github.com/chiarorosa/visual-agent-orchestrator)** ⭐ SDD PRÁTICO
- **⭐ Stars:** 8 (mas com alto impacto teórico)
- **Especialização:** Spec-Driven Development para Agentes
- **Diferencial:** Implementação prática de SDD com orquestração visual
- **Veja seção [Spec-Driven Development (SDD)](#spec-driven-development-sdd) para mais detalhes**

---

## 📂 Categorias Principais

### 1️⃣ **[Agentes Gerais & Orquestração](#agentes-gerais--orquestração)**
### 2️⃣ **[Agentes de Design & UI](#agentes-de-design--ui)**
### 3️⃣ **[Agentes de Desenvolvimento](#agentes-de-desenvolvimento)**
### 4️⃣ **[Agentes de Automação & Workflows](#agentes-de-automação--workflows)**
### 5️⃣ **[Agentes de Dados & Analytics](#agentes-de-dados--analytics)**
### 6️⃣ **[Agentes Especializados](#agentes-especializados)**
### 7️⃣ **[Frameworks & Bibliotecas Base](#frameworks--bibliotecas-base)**
### 8️⃣ **[RAG & Retrieval Augmented Generation](#rag--retrieval-augmented-generation)**
### 9️⃣ **[Prompt Engineering](#prompt-engineering)**
### 🔟 **[Model Context Protocol (MCP)](#model-context-protocol-mcp)**
### 1️⃣1️⃣ **[Frameworks Específicos](#frameworks-específicos)**
### 1️⃣2️⃣ **[Spec-Driven Development (SDD)](#spec-driven-development-sdd)** ⭐ NOVO
### 1️⃣3️⃣ **[Comunidade & Contribuintes](#comunidade--contribuintes)**
### 1️⃣4️⃣ **[Skills Locais do Finance Web](#-skills-locais-do-finance-web)** ⭐ NOVO

---

## 🌍 Agentes Gerais & Orquestração

### **[500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects)** 🔥🔥🔥 IMPRESCINDÍVEL
- **⭐ Stars:** 28.5k+
- **Linguagem:** Python, Jupyter Notebooks
- **Tipo:** Enciclopédia de Casos de Uso
- **Descrição:** 500+ casos de uso reais de agentes organizados por **indústria** e **framework**
- **Casos de Uso por Indústria:**
  - 🏥 **Healthcare:** HIA (Health Insights), AI Health Assistant, MediSuite-Ai-Agent
  - 💰 **Finance:** Automated Trading Bot, Stock Analysis, Financial Reasoning Agent
  - 🎓 **Education:** Virtual AI Tutor, Study Partner, Research Scholar Agent
  - 🛍️ **E-commerce:** Personal Shopper, Shopping Partner
  - 🏭 **Manufacturing:** Factory Process Monitoring
  - 🚚 **Logistics:** Delivery Optimization, Supply Chain
  - 🏡 **Real Estate:** Property Pricing Agent
  - 🌾 **Agriculture:** Smart Farming Assistant
  - ⚖️ **Legal:** Legal Document Review
  - 🏥 **Health Insurance:** MediSuite, Lina-Egyptian-Medical-Chatbot
  - E 10+ mais indústrias...
- **Frameworks com Exemplos:**
  - **CrewAI:** 30+ exemplos (Email Responder, Lead Scoring, Job Posting Generator, Trip Planner, etc)
  - **Autogen:** 40+ exemplos (Code Generation, Multi-Agent Chat, Nested Chats, etc)
  - **Agno:** 20+ exemplos (Support Agent, YouTube Analyzer, Finance Agent, etc)
  - **LangGraph:** 20+ exemplos (Chatbot, Code Assistant, RAG, etc)
- **Diferencial:**
  1. Melhor para validar: "Seu caso de uso já existe?"
  2. Código funcionál em cada exemplo
  3. MindMap visual dos casos
  4. Fácil buscar por indústria ou framework
  5. Links diretos para implementação
- **Nível de Complexidade:** ⭐⭐⭐ (Médio - entender e adaptar)
- **👉 RECOMENDAÇÃO:** Use como PRIMEIRA BUSCA para qualquer caso de uso
- **Link Direto:** https://github.com/ashishpatel26/500-AI-Agents-Projects

---
- **⭐ Stars:** 105k+
- **Linguagem:** Python
- **Descrição:** 100+ aplicações de IA e RAG prontas para clonar, customizar e deployar
- **Casos de Uso:**
  - Chatbots inteligentes
  - Sistemas de RAG (Retrieval Augmented Generation)
  - Aplicações multi-agentes
  - Processamento de documentos
- **Stack Popular:** LangChain, LlamaIndex, OpenAI, Claude
- **Como Usar:** Clone projetos específicos, customize conforme necessário
- **Nível de Complexidade:** ⭐⭐⭐ (Médio-Avançado)

---

### **[awesome-copilot](https://github.com/github/awesome-copilot)** 🌟
- **⭐ Stars:** 30k+
- **Linguagem:** Python
- **Descrição:** Instruções, agentes e skills oficiais do GitHub Copilot da comunidade
- **Características:**
  - Skills reutilizáveis
  - Agentes customizáveis
  - Instruções prontas para usar
  - Integração nativa com VS Code
- **Casos de Uso:**
  - Desenvolvimento acelerado
  - Refatoração de código
  - Geração de testes
  - Documentação automática
- **Nível de Complexidade:** ⭐⭐ (Beginner-Intermediário)
- **Link Adicional:** https://github.com/github/awesome-copilot

---

### **[awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents)**
- **⭐ Stars:** 27k+
- **Linguagem:** Python, Documentação
- **Descrição:** Lista curada de agentes autônomos de IA com categorias
- **Categorias Cobertas:**
  - Agentes de Pesquisa
  - Agentes de Coding
  - Agentes de Trading
  - Agentes Multimodais
- **Útil para:** Pesquisa e descoberta de novos agentes
- **Nível de Complexidade:** ⭐ (Iniciante - Referência)

---

### **[awesome-ai-apps](https://github.com/Arindam200/awesome-ai-apps)**
- **⭐ Stars:** 10k+
- **Linguagem:** Python
- **Descrição:** Projetos completos com RAG, agentes, workflows e casos de uso reais
- **Destaques:**
  - Exemplos de implementação
  - Diferentes arquiteturas
  - Boas práticas documentadas
  - Suporte a MCP (Model Context Protocol)
- **Nível de Complexidade:** ⭐⭐⭐ (Médio)

---

### **[awesome-claude-agents](https://github.com/vijaythecoder/awesome-claude-agents)**
- **⭐ Stars:** 4.1k+
- **Linguagem:** Python
- **Descrição:** Time orquestrado de sub-agentes alimentados por Claude
- **Características Especiais:**
  - Orquestração de múltiplos agentes
  - Hierarquia de tarefas
  - Especialização por agente
- **Ideal para:** Proyectos complexos que exigem múltiplas perspectivas
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Avançado)

---

### **[awesome-agents](https://github.com/kyrolabs/awesome-agents)**
- **⭐ Stars:** 2.1k+
- **Descrição:** Lista simples, direta e atualizada de agentes de IA
- **Bom para:** Começar do zero, visão geral rápida
- **Atualizado:** Frequentemente (2 dias atrás conforme última data)
- **Nível de Complexidade:** ⭐ (Iniciante)

---

### **[awesome_ai_agents](https://github.com/jim-schwoebel/awesome_ai_agents)**
- **⭐ Stars:** 1.5k+
- **Descrição:** 1.500+ recursos sobre agentes, multi-agentes e agent-based modeling
- **Cobertura:**
  - Agent-based modeling
  - Multi-agent systems
  - Ferramentas e frameworks
  - Pesquisa acadêmica
- **Nível de Complexidade:** ⭐⭐ (Intermediário - Referência)

---

## 🎨 Agentes de Design & UI

### **[awesome-design-md](https://github.com/VoltAgent/awesome-design-md)** ⭐⭐⭐
- **⭐ Stars:** 56k+
- **Descrição:** Coleção de arquivos DESIGN.md para agentes de IA gerarem UIs consistentes
- **Conceito Único:**
  - DESIGN.md é um formato introduzido pelo Google Stitch
  - Plain-text markdown lido por agentes de IA
  - Sem dependências de Figma, JSON ou ferramentas especiais
- **O que Inclui:**
  - Paleta de cores com roles semânticos
  - Hierarquia tipográfica completa
  - Estilos de componentes (botões, cards, inputs)
  - Princípios de layout e spacing
  - Guia de responsividade
  - Prompts prontos para agentes
- **Marcas Incluídas:** Apple, Spotify, Vercel, Stripe, Figma, Netflix, Tesla, BMW, Airbnb, e muitas outras
- **Como Usar:**
  1. Copie o `DESIGN.md` da marca desejada
  2. Coloque na raiz do seu projeto
  3. Diga ao seu agente de IA: "use este DESIGN.md para gerar a página"
- **Nível de Complexidade:** ⭐⭐ (Beginner-Intermediário)
- **Revolucionário:** Este é possivelmente o conceito mais inovador da lista

---

### **[Awesome-Design-Tools](https://github.com/goabstract/Awesome-Design-Tools)**
- **⭐ Stars:** 39.6k+
- **Descrição:** Ferramentas e plugins de design para todo tipo de necessidade
- **Categorias:**
  - Wireframing & Mockups
  - Prototyping
  - Design Systems
  - Collaboration Tools
  - Animation
  - Assets & Resources
- **Nível de Complexidade:** ⭐ (Iniciante - Referência de Ferramentas)

---

### **[awesome-design-systems](https://github.com/alexpate/awesome-design-systems)**
- **⭐ Stars:** 23.4k+
- **Descrição:** Coleção de design systems reais e implementados
- **Includes:**
  - Design systems de grandes empresas
  - Pattern libraries
  - Component libraries
  - Documentação de implementação
- **Útil para:** Estudar como empresas estruturam seus designs
- **Nível de Complexidade:** ⭐⭐ (Intermediário - Estudo)

---

### **[Awesome-Design-Tokens](https://github.com/sturobson/Awesome-Design-Tokens)**
- **⭐ Stars:** 1.2k+
- **Descrição:** Recursos sobre Design Tokens e como usá-los
- **Tópicos:**
  - Design Token Architecture
  - Tools & Frameworks
  - Best Practices
  - Implementações
- **Nível de Complexidade:** ⭐⭐⭐ (Médio-Avançado)

---

## 💻 Agentes de Desenvolvimento

### **[Cursor](https://www.cursor.com/)**
- **⭐ Popularidade:** Muito Alta
- **Descrição:** Editor de código AI-first
- **Características:**
  - Copilot integrado (AI pair programmer)
  - Chat contextual
  - Refatoração assistida
  - Geração de código
- **Nível de Complexidade:** ⭐ (Iniciante)

---

### **[Lovable](https://lovable.dev/)**
- **⭐ Popularidade:** Alta
- **Descrição:** Builder AI full-stack
- **Características:**
  - Gera UI e backend simultaneamente
  - Deploy automático
  - Integração com banco de dados
  - Preview em tempo real
- **Stack:** React, Node.js, Supabase
- **Nível de Complexidade:** ⭐ (Iniciante)

---

### **[Raycast](https://raycast.com/)**
- **⭐ Popularidade:** Muito Alta
- **Descrição:** Launcher de produtividade com IA
- **Características:**
  - Extensões customizáveis
  - Scripts automáticos
  - Integração com ferramentas
  - AI Commands
- **Plataforma:** macOS, Windows
- **Nível de Complexidade:** ⭐ (Iniciante)

---

## 🔄 Agentes de Automação & Workflows

### **[awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents)**
- **⭐ Stars:** 2.9k+
- **Linguagem:** HTML, Docker
- **Descrição:** 162 templates prontos para produção com configs SOUL.md
- **Categorias:**
  - Bots de Telegram
  - Automação de tarefas
  - Processamento de dados
  - Integrações
- **Exclusividade:** SOUL.md configs (similar ao DESIGN.md mas para agentes)
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[Zapier](https://zapier.com/)**
- **⭐ Popularidade:** Muito Alta
- **Descrição:** Plataforma de automação e integração
- **Características:**
  - Suporte a 6.000+ apps
  - Zaps automáticos
  - Multi-step workflows
  - AI Actions
- **Nível de Complexidade:** ⭐ (Iniciante)

---

### **[Composio](https://github.com/getdesign.md/composio)**
- **Descrição:** Plataforma de integração de ferramentas para agentes de IA
- **Características:**
  - Conexão fácil com APIs
  - Pre-built integrations
  - Workflow automation
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

## 📊 Agentes de Dados & Analytics

### **[PostHog](https://posthog.com/)**
- **⭐ Popularidade:** Alta (Open Source)
- **Descrição:** Analytics e Product Intelligence com IA
- **Features:**
  - Event tracking
  - Session replay
  - Heatmaps
  - Feature flags com IA
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[ClickHouse](https://clickhouse.com/)**
- **⭐ Stars:** Milhões de downloads
- **Descrição:** Database de analytics rápido
- **Ideal para:** Processamento de grandes volumes de dados
- **Nível de Complexidade:** ⭐⭐⭐ (Avançado)

---

## 🎯 Agentes Especializados

### **[Awesome-GPT-Agents](https://github.com/fr0gger/Awesome-GPT-Agents)**
- **⭐ Stars:** 6.4k+
- **Especialização:** Cibersegurança
- **Descrição:** Agentes GPT especializados em segurança
- **Casos de Uso:**
  - Análise de vulnerabilidades
  - Penetration testing
  - Security audits
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Avançado)

---

### **[E2B Sandbox](https://e2b.dev/)**
- **Descrição:** Sandbox seguro para executar código de agentes
- **Características:**
  - Execução isolada de código
  - Suporte a 30+ linguagens
  - Integração com agentes de IA
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

## 🔧 Frameworks & Bibliotecas Base

### **[awesome-langchain](https://github.com/kyrolabs/awesome-langchain)** 🔥
- **⭐ Stars:** 9.2k+
- **Descrição:** Coleção completa de ferramentas e projetos com LangChain framework
- **Cobertura:**
  - Ferramentas LangChain
  - Projetos integrados
  - Exemplos práticos
  - Extensões da comunidade
- **Por Que Importante:** LangChain é a base de muitos agentes modernos
- **Nível de Complexidade:** ⭐⭐⭐ (Médio-Avançado)

---

### **[awesome-LangGraph](https://github.com/von-development/awesome-LangGraph)** 🔥
- **⭐ Stars:** 1.7k+
- **Linguagem:** JavaScript
- **Descrição:** Índice completo do ecossistema LangChain + LangGraph com conceitos, projetos, tools, templates e guias
- **Cobertura:**
  - LangGraph fundamentals
  - Projetos com LangGraph
  - Templates prontos
  - Guias de implementação
  - Apps multi-agentes
- **Diferencial:** Especializado em LangGraph (framework para grafos de agentes)
- **Nível de Complexidade:** ⭐⭐⭐ (Médio-Avançado)

---

### **[awesome-llm-agents](https://github.com/kaushikb11/awesome-llm-agents)**
- **⭐ Stars:** 1.4k+
- **Descrição:** Lista curada de frameworks de agentes LLM (Autogen, CrewAI, LangChain, etc)
- **Comparação:** Compara diferentes frameworks lado-a-lado
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-ai-sdks](https://github.com/e2b-dev/awesome-ai-sdks)**
- **⭐ Stars:** 1.1k+
- **Descrição:** Database de SDKs, frameworks, bibliotecas e ferramentas para criar, monitorar, debugar e deployar agentes autônomos
- **Categorias:**
  - SDKs de IA
  - Frameworks de agentes
  - Ferramentas de monitoramento
  - Plataformas de deployment
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-LLM-resources](https://github.com/WangRongsheng/awesome-LLM-resources)**
- **⭐ Stars:** 8.0k+
- **Linguagem:** Chinês + Inglês
- **Descrição:** Melhor resumo global de recursos LLM (Multimodal, Agents, Auxiliary Programming, AI Review, Data Processing, Model Training, Inference, o1 models, MCP)
- **Cobertura:**
  - Geração multimodal
  - Agentes e workflows
  - Programação assistida
  - Revisão por IA
  - Processamento de dados
  - Treinamento de modelos
  - MCP (Model Context Protocol)
- **Nível de Complexidade:** ⭐⭐⭐ (Avançado)

---

## 📊 RAG & Retrieval Augmented Generation

### **[Awesome-LLM-RAG-Application](https://github.com/lizhe2004/Awesome-LLM-RAG-Application)** 🔥
- **⭐ Stars:** 1.6k+
- **Descrição:** Recursos sobre aplicações LLM com padrão RAG
- **Cobertura:**
  - Implementações RAG
  - Architectures
  - Best practices
  - Caso de uso reais
- **Ideal para:** Aprender implementação prática de RAG
- **Nível de Complexidade:** ⭐⭐⭐ (Médio-Avançado)

---

### **[Awesome-GraphRAG](https://github.com/DEEP-PolyU/Awesome-GraphRAG)** 🔥
- **⭐ Stars:** 2.2k+
- **Descrição:** Recursos curados em Graph RAG (retrieval-augmented generation baseado em grafos de conhecimento)
- **Inclui:**
  - Surveys
  - Papers
  - Benchmarks
  - Projetos open-source
- **Diferencial:** Técnica avançada usando knowledge graphs
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Avançado)

---

### **[Awesome-RAG](https://github.com/Danielskry/Awesome-RAG)**
- **⭐ Stars:** 1.1k+
- **Descrição:** Lista curada de aplicações RAG em IA Generativa
- **Cobertura:**
  - RAG fundamentals
  - Implementações
  - Ferramentas
  - Estudos de caso
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[Awesome-LLM-RAG](https://github.com/jxzhangjhu/Awesome-LLM-RAG)**
- **⭐ Stars:** 1.3k+
- **Descrição:** Lista curada de RAG avançado em Large Language Models com embeddings e técnicas
- **Cobertura:**
  - Embeddings
  - Retrieval techniques
  - Papers acadêmicos
  - Implementações
- **Nível de Complexidade:** ⭐⭐⭐ (Avançado)

---

### **[RAG-Survey](https://github.com/hymie122/RAG-Survey)**
- **⭐ Stars:** 1.7k+
- **Descrição:** Coleção de papers awesome sobre RAG para AIGC
- **Taxonomia:**
  - RAG foundations
  - Enhancements
  - Applications
- **Ideal para:** Pesquisa e entendimento teórico
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Acadêmico)

---

### **[awesome-n8n-templates](https://github.com/enescingoz/awesome-n8n-templates)** 🔥
- **⭐ Stars:** 21.2k+
- **Descrição:** 280+ templates prontos para automação n8n (Gmail, Telegram, Slack, Discord, OpenAI, etc)
- **Útil para:** Criar workflows RAG e agentes sem código
- **Integrations:** Gmail, Telegram, Slack, Discord, WhatsApp, Google Drive, Notion, OpenAI, etc
- **Nível de Complexidade:** ⭐ (Iniciante)

---

## 💬 Prompt Engineering

### **[awesome-prompts](https://github.com/ai-boost/awesome-prompts)** 🔥
- **⭐ Stars:** 7.6k+
- **Descrição:** Lista curada de prompts ChatGPT dos GPTs top-rated no GPT Store
- **Inclui:**
  - Prompt Engineering
  - Prompt Attack & Protect
  - Advanced prompts
  - Técnicas de jailbreak
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[Awesome-Prompt-Engineering](https://github.com/promptslab/Awesome-Prompt-Engineering)** 🔥
- **⭐ Stars:** 5.7k+
- **Linguagem:** TypeScript
- **Descrição:** Recursos hand-curated para Prompt Engineering com foco em GPT, ChatGPT, LLMs
- **Cobertura:**
  - Técnicas de prompting
  - Prompt chains
  - Few-shot learning
  - Tools e recursos
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-gpt-prompt-engineering](https://github.com/snwfdhmp/awesome-gpt-prompt-engineering)**
- **⭐ Stars:** 1.5k+
- **Linguagem:** Python
- **Descrição:** Lista curada de recursos, ferramentas e padrões para prompt engineering em LLMs
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[Awesome-Context-Engineering](https://github.com/Meirtz/Awesome-Context-Engineering)** 🔥
- **⭐ Stars:** 3.0k+
- **Descrição:** Survey complessivo sobre Context Engineering: de prompt engineering a production-grade AI systems
- **Inclui:**
  - Centenas de papers
  - Frameworks
  - Best practices
  - Técnicas avançadas
- **Diferencial:** Conecta prompt engineering com sistemas de produção
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Avançado)

---

## 🔌 Model Context Protocol (MCP)

### **[awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)** 🌟🌟🌟 MONUMENTAL
- **⭐ Stars:** 84,900+
- **Descrição:** Coleção massiva de servidores MCP (Model Context Protocol)
- **Importância:** MCP é o novo padrão aberto para conectar agentes a ferramentas e contextos
- **Diferencial:** Maior repositório MCP do GitHub! 
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-mcp-clients](https://github.com/punkpeye/awesome-mcp-clients)** 🔥
- **⭐ Stars:** 6.3k+
- **Descrição:** Coleção de clients MCP (complementa os servers)
- **Útil para:** Implementar clientes que se conectam aos servidores MCP
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[Awesome-MCP-ZH](https://github.com/yzfly/Awesome-MCP-ZH)** 🔥
- **⭐ Stars:** 6.8k+
- **Linguagem:** Chinês
- **Descrição:** Recursos MCP curados (MCP Servers, MCP Clients, Claude MCP, DeepSeek MCP)
- **Cobertura Completa:** Guias, servidores, clientes, recursos
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-mcp-servers (appcypher)](https://github.com/appcypher/awesome-mcp-servers)** 🔥
- **⭐ Stars:** 5.4k+
- **Descrição:** Lista curada de servidores Model Context Protocol
- **Bem Documentado:** Melhor alternativa se punkpeye for confuso
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-mcp-servers (wong2)](https://github.com/wong2/awesome-mcp-servers)** 🔥
- **⭐ Stars:** 3.9k+
- **Descrição:** Outra coleção curada de servidores MCP
- **Alternativa:** Mais uma opção bem mantida
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)** 🔥
- **⭐ Stars:** 54.3k+
- **Linguagem:** Python
- **Descrição:** Lista curada de Claude Skills para customizar workflows do Claude
- **Relação:** Skills são extensões que funcionam com MCP
- **Inclui:**
  - Automação
  - Integrações
  - Workflows
  - SaaS integrations
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[mcpso - MCP Server Store](https://github.com/chatmcp/mcpso)**
- **⭐ Stars:** 1.9k+
- **Linguagem:** TypeScript
- **Descrição:** Diretório de awesome MCP Servers com descoberta
- **Diferencial:** Like "App Store" para MCP servers
- **Nível de Complexidade:** ⭐ (Iniciante)

---

### **[awesome-remote-mcp-servers](https://github.com/jaw9c/awesome-remote-mcp-servers)**
- **⭐ Stars:** 1.0k+
- **Descrição:** Servidores MCP remotos
- **Especialização:** Para usar MCP servers na nuvem/remoto
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-mcp-servers (TensorBlock)](https://github.com/TensorBlock/awesome-mcp-servers)**
- **⭐ Stars:** 617
- **Descrição:** Coleção compressiva de servidores MCP
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

## 🤖 Frameworks Específicos

### **[awesome-crewai](https://github.com/crewAIInc/awesome-crewai)** 🔥
- **⭐ Stars:** 481
- **Descrição:** Lista curada de projetos open-source construídos pela comunidade CrewAI
- **Oficial:** Mantido oficialmente pela CrewAI Inc
- **Cobertura:** Aplicações, ferramentas, extensões CrewAI
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-multi-agent-papers](https://github.com/kyegomez/awesome-multi-agent-papers)** 🔥
- **⭐ Stars:** 1.3k+
- **Linguagem:** TeX
- **Descrição:** Compilação dos melhores papers sobre multi-agent systems
- **Cobertura:**
  - Transformers
  - Multi-agent architectures
  - Swarm intelligence
  - Attention mechanisms
- **Ideal para:** Pesquisa teórica e papers acadêmicos
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Acadêmico)

---

### **[awesome-agent-quickstart](https://github.com/ababdotai/awesome-agent-quickstart)**
- **⭐ Stars:** 59
- **Linguagem:** Python
- **Descrição:** Hello world para frameworks agentic - minimal but runnable!
- **Cobertura:** LangGraph, Agno, AutoGen, Smolagents, OpenAI Agents, etc
- **Diferencial:** Comparação prática lado-a-lado de todos os frameworks
- **Ideal para:** Decidir qual framework usar
- **Nível de Complexidade:** ⭐ (Iniciante)

---

### **[Awesome-Agentic-AI-Learning-Resource](https://github.com/DharminJoshi/Awesome-Agentic-AI-Learning-Resource-By-DevKay)**
- **⭐ Stars:** 62
- **Descrição:** Roadmap curado para dominar Agentic AI - de ML fundamentals a production-ready agents
- **Cobertura:**
  - ML fundamentals
  - LLM foundations
  - Agentic AI concepts
  - Production deployment
- **Nível de Complexidade:** ⭐⭐⭐ (Educacional)

---

### **[awesome-agent-orchestration](https://github.com/vivy-yi/awesome-agent-orchestration)**
- **⭐ Stars:** 3
- **Descrição:** Lista curada de frameworks de orquestração de agentes: AutoGen, CrewAI, MetaGPT, LangGraph, Swarms
- **Cobertura:**
  - Multi-Agent Systems
  - Swarm Intelligence
  - A2A Protocol
  - MCP
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-ai-agent-frameworks](https://github.com/Vincentwei1021/awesome-ai-agent-frameworks)** 🆕
- **⭐ Stars:** 0 (Muito novo)
- **Linguagem:** Chinês
- **Descrição:** Guia de seleção de frameworks de IA em chinês - Scion/AutoGen/CrewAI/LangGraph/MetaGPT/Dify/Coze com análise profunda e árvore de decisão
- **Diferencial:** Comparação estruturada com matriz de decisão
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-local-ai](https://github.com/ethicals7s/awesome-local-ai)**
- **⭐ Stars:** 54
- **Descrição:** 152 ferramentas open-source para rodar LLMs 100% localmente - sem cloud, sem API keys, sem censura
- **Cobertura:**
  - LLM inference local
  - Voice models
  - Quantization
  - Self-hosted solutions
- **Nível de Complexidade:** ⭐⭐⭐ (Avançado)

---

### **[Awesome-Swarms-List](https://github.com/The-Swarm-Corporation/Awesome-Swarms-List)** 🔥
- **⭐ Stars:** 17
- **Descrição:** Aplicações, ferramentas e recursos para Swarms framework
- **Diferencial:** Framework de swarm intelligence
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[END-TO-END-GENERATIVE-AI-PROJECTS](https://github.com/GURPREETKAURJETHRA/END-TO-END-GENERATIVE-AI-PROJECTS)**
- **⭐ Stars:** 543
- **Linguagem:** Python
- **Descrição:** Projetos end-to-end com Generative AI em LLM Models com deployment (Gemini, Llama, Mistral, etc)
- **Cobertura:**
  - Fine-tuning
  - LORA
  - Deployment
  - Casos de uso reais
- **Nível de Complexidade:** ⭐⭐⭐ (Avançado)

---

### **[awesome-chatgpt-zh](https://github.com/EmbraceAGI/awesome-chatgpt-zh)** 🔥
- **⭐ Stars:** 11.5k+
- **Linguagem:** Chinês
- **Descrição:** Guia ChatGPT em chinês - orientação de prompt, guia de aplicação, recursos curados
- **Cobertura:**
  - Prompt engineering chinês
  - Desenvolvimento de aplicações
  - Recursos e ferramentas
- **Nível de Complexidade:** ⭐⭐ (Intermediário)

---

### **[awesome-llm-and-aigc](https://github.com/coderonion/awesome-llm-and-aigc)**
- **⭐ Stars:** 809
- **Descrição:** Coleção de projetos públicos sobre LLM, Vision Language Model (VLM), Vision Language Action (VLA)
- **Cobertura:**
  - LLM architectures
  - CUDA & GPU
  - YOLO & vision
  - Triton optimization
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Avançado)

---

## 🧩 Task & Problem Decomposition ⭐ NOVO

### **O que é Task/Problem Decomposition?**

Task Decomposition é o padrão de **quebrar problemas grandes em subtarefas menores**, resolvendo cada uma independentemente e agregando as soluções. É fundamental para agentes resolvem problemas complexos de forma estruturada.

**Padrões Relacionados:**
- **Chain-of-Thought (CoT)** - Raciocínio passo a passo explícito
- **Tree-of-Thought (ToT)** - Exploração de múltiplos caminhos de decomposição
- **Hierarchical Task Decomposition** - Hierarquia de tarefas (grandes → pequenas)
- **Auto Task Decomposition** - Agente decide automaticamente como decompor

---

### **[tree-of-thought-llm](https://github.com/princeton-nlp/tree-of-thought-llm)** 🌳 SEMINAL
- **⭐ Stars:** 5.906+
- **Linguagem:** Python
- **Descrição:** Implementação oficial do paper NeurIPS 2023 "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"
- **O que Oferece:**
  - Framework para decomposição hierárquica
  - Exploração de múltiplos caminhos de resolução
  - Benchmarks de problemas complexos
  - Base teórica sólida (paper publicado)
- **Casos de Uso:** Problemas matemáticos, lógica, planning
- **Nível de Complexidade:** ⭐⭐⭐ (Médio-Avançado)
- **Link:** https://github.com/princeton-nlp/tree-of-thought-llm

---

### **[open-multi-agent](https://github.com/JackChen-me/open-multi-agent)** 🤖 AUTO DECOMPOSITION
- **⭐ Stars:** 5.728+
- **Linguagem:** TypeScript
- **Descrição:** Motor de orquestração multi-agente com **auto task decomposition** - Agentes decidem automaticamente como decompor tarefas!
- **Diferencial:** Decomposição automática + Orquestração paralela
- **O que Oferece:**
  - Auto task decomposition inteligente
  - Suporte a múltiplos modelos LLM
  - Execução paralela de sub-agentes
  - Agregação de resultados
- **Muito Ativo:** Atualizado a poucas horas!
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Avançado)
- **Link:** https://github.com/JackChen-me/open-multi-agent

---

### **[Awesome-LLM-Reasoning](https://github.com/atfortes/Awesome-LLM-Reasoning)** 📚 CURATED
- **⭐ Stars:** 3.591+
- **Tipo:** Curated List
- **Descrição:** Coleção curada de recursos sobre Chain-of-Thought, OpenAI o1, DeepSeek-R1 e técnicas avançadas de raciocínio
- **O que Inclui:**
  - Tutoriais de CoT
  - Papers de raciocínio avançado
  - Implementações práticas
  - Comparação de técnicas
  - Recursos sobre DeepSeek-R1 (novo!)
- **Muito Ativo:** Atualizado em Maio 2025
- **Nível de Complexidade:** ⭐⭐ (Intermediário - Referência)
- **Link:** https://github.com/atfortes/Awesome-LLM-Reasoning

---

### **[chain-of-thought-hub](https://github.com/FranxYao/chain-of-thought-hub)** 📊 BENCHMARK
- **⭐ Stars:** 2.770+
- **Linguagem:** Jupyter Notebook
- **Descrição:** Benchmarking da capacidade de raciocínio complexo de LLMs com chain-of-thought prompting
- **O que Oferece:**
  - Benchmarks estruturados para CoT
  - Avaliação de qualidade de raciocínio
  - Datasets de teste
  - Comparação entre modelos
- **Ideál para:** Validar qualidade de decomposição
- **Nível de Complexidade:** ⭐⭐⭐ (Médio-Avançado)
- **Link:** https://github.com/FranxYao/chain-of-thought-hub

---

### **[griptape](https://github.com/griptape-ai/griptape)** 🛠️ FRAMEWORK MODULAR
- **⭐ Stars:** 2.514+
- **Linguagem:** Python
- **Descrição:** Framework modular em Python para agentes IA com chain-of-thought, ferramentas, memória e decomposição de tarefas automática
- **O que Oferece:**
  - Chain-of-Thought integrado
  - Decomposição de tarefas automática
  - Acesso a ferramentas/APIs
  - Memória persistente
  - Multi-agente support
- **Muito Ativo:** Atualizado a poucas horas!
- **Nível de Complexidade:** ⭐⭐⭐ (Médio-Avançado)
- **Link:** https://github.com/griptape-ai/griptape

---

### **[LightAgent](https://github.com/wanxingai/LightAgent)** ⚡ LEVE & PODEROSO
- **⭐ Stars:** 855+
- **Linguagem:** Python
- **Descrição:** Framework leve para agentes IA com tree-of-thought, memória, ferramentas e suporte a multi-agente
- **O que Oferece:**
  - Tree-of-Thought nativo
  - Lightweight (fácil integrar)
  - Memória e ferramentas
  - Multi-agente
  - Simples de usar
- **Muito Ativo:** Atualizado há 3 dias
- **Nível de Complexidade:** ⭐⭐ (Intermediário)
- **Link:** https://github.com/wanxingai/LightAgent

---

## 📋 Spec-Driven Development (SDD) ⭐ NOVO

### **O que é Spec-Driven Development?**

Spec-Driven Development (SDD) é uma metodologia onde **especificações formais guiam o desenvolvimento de agentes de IA**. Em vez de deixar agentes improvisarem, você define exatamente como devem se comportar através de especificações estruturadas.

**Princípios-Chave:**
- 📐 **Especificações Formais** - Descrições estruturadas do comportamento esperado
- 🔄 **Orquestração Visual** - Diagramas e fluxos visuais dos agentes
- ✅ **Validação Automática** - Testar agentes contra especificações
- 🎯 **Reprodutibilidade** - Mesmas especificações = Mesmo comportamento

### **[visual-agent-orchestrator](https://github.com/chiarorosa/visual-agent-orchestrator)** 🌟 RECOMENDADO
- **⭐ Stars:** 8
- **Linguagem:** Python
- **Descrição:** Visual Multi-Agent Team Builder - Study Case para SDD com Antigravity, Opencode e Openspec
- **Exclusividade:** Implementação prática de Spec-Driven Development!
- **O que Oferece:**
  - Orquestração visual de múltiplos agentes
  - Integração com frameworks SDD (Antigravity, Openspec, Opencode)
  - Especificações estruturadas para agentes
  - Exemplos de casos de uso reais
- **Ideál para:** Aprender a implementar SDD em projetos reais
- **Nível de Complexidade:** ⭐⭐⭐ (Médio-Avançado)
- **Link:** https://github.com/chiarorosa/visual-agent-orchestrator

---

### **[mca-method](https://github.com/chiarorosa/mca-method)** 🎓 EDUCACIONAL
- **⭐ Stars:** 3
- **Linguagem:** Python, Jupyter Notebooks
- **Descrição:** MCA Method (Mentor, Copilot, Agent) - Framework pedagógico para transformar LLMs em mentores educacionais eficazes através de diretrizes estruturadas
- **Foco:** Educação em Programação com IA
- **Relevância para SDD:** Usa especificações estruturadas para definir comportamento de agentes educacionais
- **O que Inclui:**
  - Framework pedagógico estruturado
  - Metodologia MCA (Mentor-Copilot-Agent)
  - Prompt engineering educacional
  - Exemplos de agentes mentorados
- **Nível de Complexidade:** ⭐⭐⭐ (Educacional)
- **Link:** https://github.com/chiarorosa/mca-method

---

### **[mcp-server-one](https://github.com/chiarorosa/mcp-server-one)** 🔌 MCP + SDD
- **⭐ Stars:** 1
- **Linguagem:** Python
- **Descrição:** Um servidor Model Context Protocol (MCP) que fornece acesso a várias APIs públicas através de uma interface padronizada
- **Relação com SDD:** MCP é a base para especificar integrações em agentes
- **Características:**
  - Servidor MCP customizado
  - Acesso padronizado a múltiplas APIs
  - Interface consistente para agentes
  - Fácil de estender
- **Nível de Complexidade:** ⭐⭐ (Intermediário)
- **Link:** https://github.com/chiarorosa/mcp-server-one

---

## 👥 Comunidade & Contribuintes

### **Contribuintes Especiais**

Estes repositórios foram adicionados por contribuintes que conhecem profundamente agentes de IA:

### **[antigravity-awesome-skills](https://github.com/chiarorosa/antigravity-awesome-skills)** 🛠️ SKILLS MASSIVAS
- **⭐ Stars:** Forked de sickn33/antigravity-awesome-skills
- **Linguagem:** Python
- **Descrição:** Libraria GitHub instalável com **1.370+ agentic skills** para Claude Code, Cursor, Codex CLI, Gemini CLI, Antigravity e mais
- **O que Oferece:**
  - 1.370+ skills prontas para agentes
  - Instalador CLI
  - Bundles pré-configurados
  - Skills oficiais e da comunidade
  - Suporte a múltiplos clientes de IA
- **Ideál para:** Expandir capacidades de agentes rapidamente
- **Nível de Complexidade:** ⭐⭐ (Intermediário)
- **Link:** https://github.com/chiarorosa/antigravity-awesome-skills

---

### **[agno-workshop](https://github.com/chiarorosa/agno-workshop)** 📚 WORKSHOP PRÁTICO
- **⭐ Stars:** 5
- **Linguagem:** Python
- **Descrição:** Workshop project com AGNO + UV environment
- **O que Inclui:**
  - Setup completo com UV (gerenciador de pacotes)
  - Exemplos práticos com AGNO framework
  - Ambiente reprodutível
  - Boas práticas de organização
- **Ideál para:** Aprender AGNO na prática
- **Nível de Complexidade:** ⭐⭐⭐ (Intermediário)
- **Link:** https://github.com/chiarorosa/agno-workshop

---

### **[openai-agents-python](https://github.com/chiarorosa/openai-agents-python)** 🤖 ESTUDO DE CASO
- **⭐ Stars:** Fork do projeto original
- **Linguagem:** Python
- **Descrição:** 0.2.3 - Estudo de Caso: A lightweight, powerful framework for multi-agent workflows
- **Características:**
  - Framework leve para multi-agentes
  - Workflows poderosos
  - Integração com OpenAI
  - Padrões de design de agentes
- **Ideál para:** Entender padrões de multi-agentes do OpenAI
- **Nível de Complexidade:** ⭐⭐⭐ (Avançado)
- **Link:** https://github.com/chiarorosa/openai-agents-python

---

### **[machine-learning-aulas](https://github.com/chiarorosa/machine-learning-aulas)** 📖 DIDÁTICO
- **⭐ Stars:** 27 (muito relevante!)
- **Linguagem:** Python, Jupyter Notebooks
- **Descrição:** Repositório didático e executável para aprendizado progressivo de Machine Learning em Python
- **O que Oferece:**
  - Aulas estruturadas progressivamente
  - Notebooks executáveis
  - Exemplos práticos
  - Foco educacional
- **Ideál para:** Fundações de ML para agentes
- **Nível de Complexidade:** ⭐⭐ (Iniciante-Intermediário)
- **Link:** https://github.com/chiarorosa/machine-learning-aulas

---

### **[weft](https://github.com/chiarorosa/weft)** 🦀 LINGUAGEM DE IA
- **⭐ Stars:** Fork de WeaveMindAI/weft
- **Linguagem:** Rust
- **Descrição:** A programming language for AI systems - Linguagem especializada para construir sistemas de IA
- **Diferencial:** Linguagem composta especificamente para agentes
- **Características:**
  - Sintaxe otimizada para IA
  - Performance em Rust
  - Abstrações de alto nível para agentes
  - Type safety
- **Ideál para:** Projetos que requerem linguagem especializada em IA
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Avançado)
- **Link:** https://github.com/chiarorosa/weft

---

### **[voxa-app](https://github.com/chiarorosa/voxa-app)** 🎤 INTELIGÊNCIA DE VOZ
- **⭐ Stars:** Projeto recente
- **Linguagem:** C#
- **Descrição:** Inteligência que acompanha cada palavra - Aplicação de processamento de fala com IA
- **Características:**
  - Processamento de áudio em tempo real
  - Inteligência contextual
  - Integração com agentes
  - Stack C# moderno
- **Ideál para:** Agentes com interface de voz
- **Nível de Complexidade:** ⭐⭐⭐ (Avançado)
- **Link:** https://github.com/chiarorosa/voxa-app

---

### **[buzz](https://github.com/chiarorosa/buzz)** 🎵 TRANSCRIÇÃO & TRADUÇÃO
- **⭐ Stars:** Fork bem mantido
- **Linguagem:** Python
- **Descrição:** Buzz transcreve e traduz áudio offline no seu computador pessoal - Powered by OpenAI's Whisper
- **Características:**
  - 100% offline
  - Sem dependências de cloud
  - Suporte a múltiplos idiomas
  - Integração fácil com agentes
- **Ideál para:** Agentes que precisam processar áudio
- **Nível de Complexidade:** ⭐⭐ (Intermediário)
- **Link:** https://github.com/chiarorosa/buzz

---

### **[context7](https://github.com/chiarorosa/context7)** 📚 CONTEXT PARA AGENTES
- **⭐ Stars:** Fork mantido
- **Linguagem:** JavaScript
- **Descrição:** Context7 MCP Server - Documentação de código atualizada para LLMs e editores de código IA
- **O que Oferece:**
  - Servidor MCP para contexto
  - Documentação automática de código
  - Integração com LLMs
  - Suporte para code editors com IA
- **Ideál para:** Fornecer contexto relevante a agentes
- **Nível de Complexidade:** ⭐⭐ (Intermediário)
- **Link:** https://github.com/chiarorosa/context7

---

### **[MiroFish](https://github.com/chiarorosa/MiroFish)** 🐠 SWARM INTELLIGENCE
- **⭐ Stars:** Fork mantido
- **Linguagem:** Python
- **Descrição:** A Simple and Universal Swarm Intelligence Engine, Predicting Anything
- **Características:**
  - Swarm intelligence patterns
  - Previsões baseadas em enxame
  - Universal e extensível
  - Integração com agentes
- **Ideál para:** Multi-agentes com comportamento emergente
- **Nível de Complexidade:** ⭐⭐⭐ (Avançado)
- **Link:** https://github.com/chiarorosa/MiroFish

---

### **[ufpel-thesis](https://github.com/chiarorosa/ufpel-thesis)** 🎓 DOUTORADO
- **⭐ Stars:** Pesquisa acadêmica
- **Linguagem:** Python, LaTeX
- **Descrição:** Doutorado em Computação - PPGC/UFPel | Codificador Aomedia Video 1 (av1) e Redes Neurais Convolucionais
- **Relevância:** Pesquisa fundamentada em IA e processamento de vídeo
- **Características:**
  - Research em CNN
  - Codificação de vídeo com IA
  - Tese completa e documentada
  - Implementações acadêmicas
- **Ideál para:** Entender fundamentos teóricos de IA
- **Nível de Complexidade:** ⭐⭐⭐⭐ (Acadêmico)
- **Link:** https://github.com/chiarorosa/ufpel-thesis

---

**Autor Principal:** Pablo De Chiaro Rosa ([@chiarorosa](https://github.com/chiarorosa))  
**Foco:** Spec-Driven Development, Agentic AI, Open-source research, Educational frameworks

---

## 🏗️ Skills Locais do Finance Web

Esta secção documenta os **agentes e skills internos do próprio repositório**, pensados para acelerar execução no stack real do projeto: **Laravel 13 + Next.js 15 + DDD + TanStack Query + shadcn/ui + OpenAPI + foco forte em segurança e escalabilidade**.

Ao contrário das listas externas acima, estes assets já conhecem as convenções e a organização do Finance Web. O objetivo é reduzir deriva de arquitetura, acelerar tarefas repetitivas e manter backend, frontend, documentação e UX sempre alinhados.

### **Agentes locais disponíveis**

| Agente | Arquivo | Melhor uso | Nível |
|--------|---------|------------|-------|
| `finance-web-standards-guardian` | `.cursor/agents/finance-web-standards-guardian.md` | Guardião central do repositório. Use antes de planejar, implementar, revisar ou refatorar qualquer slice backend/frontend. | ⭐⭐⭐⭐ |
| `finance-web-code-reviewer` | `.cursor/agents/finance-web-code-reviewer.md` | Revisão de branch inteira, commits já enviados, PR, diff, feature ou refactor com foco em bugs, regressões, segurança, contratos e testes faltantes. | ⭐⭐⭐⭐ |
| `finance-web-root-cause-investigator` | `.cursor/agents/finance-web-root-cause-investigator.md` | Investigação de causa raiz de bug/regressão com reprodução controlada, evidência técnica e correção mínima segura. | ⭐⭐⭐⭐ |
| `finance-web-release-readiness-guardian` | `.cursor/agents/finance-web-release-readiness-guardian.md` | Gate de prontidão para deploy/merge grande: contrato, migração, segurança, testes, observabilidade e rollback. | ⭐⭐⭐⭐ |
| `cybersecurity` | `.cursor/agents/cybersecurity.md` | Red team autorizado contra o próprio produto: mapear rotas, testar auth, BOLA/IDOR, lógica de negócio e hardening operacional. | ⭐⭐⭐⭐ |

### **Skills locais atuais**

| Skill | Arquivo | Quando usar | Valor principal |
|------|---------|-------------|-----------------|
| `finance-web-backend-ddd-delivery` | `.cursor/skills/finance-web-backend-ddd-delivery/SKILL.md` | CRUDs, filtros, integrações, relatórios, serviços e refactors no Laravel | Garante DDD, Form Requests, Policies, StatusHttp, OpenAPI e disciplina de memória no backend |
| `finance-web-frontend-ddd-delivery` | `.cursor/skills/finance-web-frontend-ddd-delivery/SKILL.md` | Telas, componentes, hooks, formulários, navegação e UX | Garante RouteRegistry, TanStack Query, estados completos e consistência visual do app |
| `finance-web-api-contract-sync` | `.cursor/skills/finance-web-api-contract-sync/SKILL.md` | Toda mudança que cruza backend e frontend | Mantém request/response, OpenAPI, types, hooks, erros e UI em sincronia |
| `finance-web-productivity-workflow` | `.cursor/skills/finance-web-productivity-workflow/SKILL.md` | Implementação diária, debug, pequenos refactors e reviews | Força fluxo produtivo: ancoragem local, diffs pequenos, validação cedo e fechamento objetivo |
| `finance-web-token-efficiency` | `.cursor/skills/finance-web-token-efficiency/SKILL.md` | Tarefas pequenas e médias em que o custo de contexto importa | Reduz leitura redundante, buscas amplas e respostas inchadas sem perder rigor técnico |
| `finance-web-docs-and-status-keeper` | `.cursor/skills/finance-web-docs-and-status-keeper/SKILL.md` | Roadmap, status, arquitetura, segurança, catálogo interno e documentação operacional | Evita drift entre código, backlog, docs e convenções |
| `finance-web-import-review-ux` | `.cursor/skills/finance-web-import-review-ux/SKILL.md` | Evolução da revisão de importação de extratos | Preserva o contrato visual e responsivo do fluxo mais sensível do produto |
| `finance-web-goals-and-budgets-delivery` | `.cursor/skills/finance-web-goals-and-budgets-delivery/SKILL.md` | Entregas da Fase 10 (metas e orçamento por categoria) | Padroniza contrato, cálculo de progresso, alertas e sincronia backend/frontend |
| `finance-web-admin-audit-ops` | `.cursor/skills/finance-web-admin-audit-ops/SKILL.md` | Operações administrativas com governança e segurança | Estrutura trilha de auditoria, papéis/permissões e impersonation controlado |
| `finance-web-statement-parser-onboarding` | `.cursor/skills/finance-web-statement-parser-onboarding/SKILL.md` | Onboarding de novos bancos/formatos na importação | Garante parser resiliente, deduplicação explicável e compatibilidade com UX de revisão |
| `finance-web-error-handling-and-resilience` | `.cursor/skills/finance-web-error-handling-and-resilience/SKILL.md` | Tratamento de falhas e resiliência fullstack | Alinha payload de erro, estados de UX, retries conscientes e observabilidade mínima |

### **Mapa rápido por tipo de tarefa**

| Cenário | Skill/agente recomendado |
|--------|--------------------------|
| Criar endpoint novo no backend | `finance-web-standards-guardian` + `finance-web-backend-ddd-delivery` |
| Criar tela nova no dashboard | `finance-web-standards-guardian` + `finance-web-frontend-ddd-delivery` |
| Revisar branch, commits já enviados, PR, diff ou implementação | `finance-web-code-reviewer` |
| Alterar payload de API consumido no frontend | `finance-web-api-contract-sync` |
| Corrigir bug rápido sem perder padrão | `finance-web-productivity-workflow` |
| Sincronizar PostgreSQL local com produção (dump Neon) | `finance-web-productivity-workflow` → `finance-web-backend/scripts/sync-prod-db-to-local.ps1` |
| Fazer task curta gastando menos contexto | `finance-web-token-efficiency` |
| Atualizar roadmap, status ou docs após entrega | `finance-web-docs-and-status-keeper` |
| Revisar importação de extratos e buckets da tabela | `finance-web-import-review-ux` |
| Investigar bug difícil sem causa óbvia | `finance-web-root-cause-investigator` |
| Fazer gate técnico antes de deploy/release | `finance-web-release-readiness-guardian` |
| Entregar Fase 10 (metas e orçamento) | `finance-web-goals-and-budgets-delivery` |
| Evoluir painel admin com trilha de auditoria | `finance-web-admin-audit-ops` |
| Adicionar banco novo no parser de extrato | `finance-web-statement-parser-onboarding` |
| Padronizar erros e recuperar melhor de falhas | `finance-web-error-handling-and-resilience` |
| Fazer auditoria ofensiva na API e fluxos críticos | `cybersecurity` |

### **Workflow recomendado dentro deste repositório**

```markdown
1. Comece pelo guardião: finance-web-standards-guardian
2. Escolha o skill principal do slice:
  - backend -> finance-web-backend-ddd-delivery
  - frontend -> finance-web-frontend-ddd-delivery
  - fullstack/contrato -> finance-web-api-contract-sync
3. Se o objetivo principal for revisão técnica da branch, dos commits já enviados ou do diff atual, rode finance-web-code-reviewer
4. Se a tarefa for pequena ou media e voce quiser reduzir custo de contexto, acrescente finance-web-token-efficiency
5. Use finance-web-productivity-workflow para manter o trabalho curto, validado e sem deriva
6. Se a entrega tocar docs, backlog ou catálogo interno, feche com finance-web-docs-and-status-keeper
7. Para statement import, acrescente finance-web-import-review-ux
8. Para bugs/regressoes sem causa clara, use finance-web-root-cause-investigator
9. Antes de release/hotfix, rode finance-web-release-readiness-guardian
10. Para hardening ofensivo e segurança prática, rode cybersecurity
```

### **Por que estes skills fazem sentido para o Finance Web**

- O backend já opera com convenções fortes de **DDD + MVC + Services + Repositories + Policies** e com atenção explícita ao teto operacional de memória do serviço da API.
- O frontend já depende de **RouteRegistry**, **TanStack Query**, **DDD por domínio**, **shadcn/ui** e estados de UX bem definidos.
- O projeto possui superfícies sensíveis de produto, como **importação de extratos**, **contrapartes**, **dados financeiros** e **admin/auditoria**, onde drift de contrato ou UX custa caro.
- O repositório é rico em documentação viva (`ARQUITETURA`, `CONVENCOES`, `SEGURANCA`, `openapi`, `PROJECT_STATUS`, `PRÓXIMAS_IMPLEMENTAÇÕES`), então faz sentido ter um skill dedicado a manter tudo sincronizado.

### **Pacote novo adicionado nesta atualização**

- `finance-web-goals-and-budgets-delivery`
- `finance-web-admin-audit-ops`
- `finance-web-statement-parser-onboarding`
- `finance-web-error-handling-and-resilience`
- `finance-web-root-cause-investigator`
- `finance-web-release-readiness-guardian`

Nota: o skill `finance-web-token-efficiency` permanece como camada transversal para reduzir custo de contexto nas tarefas operacionais do dia a dia.

### **Estratégia de uso recomendada**

Para este projeto, a melhor abordagem não é depender apenas de grandes listas externas. O ganho real vem de combinar:

1. **Repositórios externos** para inspiração e padrões amplos.
2. **Agentes locais** para governança técnica do Finance Web.
3. **Skills locais** para execução repetível, rápida e aderente ao código já existente.

---

## 📊 Comparação Rápida

| Repositório | ⭐ Stars | Tipo | Complexidade | Melhor Para |
|--------|------|---------|-------------|-----------|
| **punkpeye/awesome-mcp-servers** | **84,900+** | **MCP** | **⭐⭐** | **Todos MCP servers** |
| awesome-llm-apps | 105k+ | Apps RAG | ⭐⭐⭐ | Clonar & customizar |
| awesome-design-md | 56k+ | Design | ⭐⭐ | Gerar UIs com IA |
| awesome-claude-skills | 54.3k+ | Skills | ⭐⭐ | Claude integrations |
| awesome-copilot | 30k+ | Dev | ⭐⭐ | Coding acelerado |
| 500-AI-Agents-Projects | 28.5k+ | Casos de Uso | ⭐⭐⭐ | Validar casos de uso |
| Awesome-Design-Tools | 39.6k+ | Design | ⭐ | Ferramentas design |
| awesome-ai-agents | 27k+ | Geral | ⭐ | Pesquisa rápida |
| awesome-chatgpt-zh | 11.5k+ | ChatGPT | ⭐⭐ | Prompt chinês |
| awesome-ai-apps | 10k+ | Apps | ⭐⭐⭐ | Projetos completos |
| awesome-langchain | 9.2k+ | Framework | ⭐⭐⭐ | LangChain projects |
| awesome-LLM-resources | 8.0k+ | Recursos | ⭐⭐⭐⭐ | Overview completo |
| awesome-prompts | 7.6k+ | Prompts | ⭐⭐ | GPT prompts |
| awesome-MCP-ZH | 6.8k+ | MCP | ⭐⭐ | MCP chinês |
| awesome-mcp-clients | 6.3k+ | MCP | ⭐⭐ | MCP clients |
| awesome-mcp-servers (appcypher) | 5.4k+ | MCP | ⭐⭐ | MCP servers |
| Awesome-Prompt-Engineering | 5.7k+ | Prompts | ⭐⭐ | Prompt engineering |
| awesome-mcp-servers (wong2) | 3.9k+ | MCP | ⭐⭐ | MCP servers |
| Awesome-Context-Engineering | 3.0k+ | Context | ⭐⭐⭐⭐ | Context + Production |
| awesome-openclaw-agents | 2.9k+ | Automação | ⭐⭐ | Templates prontos |
| Awesome-GraphRAG | 2.2k+ | RAG | ⭐⭐⭐⭐ | Graph RAG avançado |
| mcpso | 1.9k+ | MCP | ⭐ | MCP discovery |
| RAG-Survey | 1.7k+ | RAG | ⭐⭐⭐⭐ | Papers RAG |
| awesome-LangGraph | 1.7k+ | Framework | ⭐⭐⭐ | LangGraph projects |
| Awesome-LLM-RAG-Application | 1.6k+ | RAG | ⭐⭐⭐ | RAG implementação |
| awesome-gpt-prompt-engineering | 1.5k+ | Prompts | ⭐⭐ | Prompt patterns |
| awesome-llm-agents | 1.4k+ | Framework | ⭐⭐ | Framework comparison |
| awesome-multi-agent-papers | 1.3k+ | Papers | ⭐⭐⭐⭐ | Multi-agent papers |
| Awesome-LLM-RAG | 1.3k+ | RAG | ⭐⭐⭐ | RAG avançado |
| awesome-agents | 2.1k+ | Geral | ⭐ | Quick overview |
| awesome-ai-sdks | 1.1k+ | SDKs | ⭐⭐ | Agent SDKs |
| Awesome-RAG | 1.1k+ | RAG | ⭐⭐ | RAG basics |
| awesome-remote-mcp-servers | 1.0k+ | MCP | ⭐⭐ | Remote MCP |
| END-TO-END-GENERATIVE-AI-PROJECTS | 543 | Projetos | ⭐⭐⭐ | End-to-end projects |
| awesome-crewai | 481 | CrewAI | ⭐⭐ | CrewAI projects |
| TensorBlock/awesome-mcp-servers | 617 | MCP | ⭐⭐ | MCP servers |
| awesome_ai_agents | 1.5k+ | Geral | ⭐⭐ | Recursos gerais |
| awesome-claude-agents | 4.1k+ | Orquestração | ⭐⭐⭐⭐ | Multi-agentes |
| Awesome-GPT-Agents | 6.4k+ | Cibersegurança | ⭐⭐⭐⭐ | Security agents |
| **visual-agent-orchestrator** | **8** | **SDD** | **⭐⭐⭐** | **Spec-Driven Development** |
| **agno-workshop** | **5** | **Workshop** | **⭐⭐⭐** | **AGNO prático** |
| **machine-learning-aulas** | **27** | **Educacional** | **⭐⭐** | **ML fundamentos** |
| **antigravity-awesome-skills** | **1.370+ skills** | **Skills** | **⭐⭐** | **1.370+ agentic skills** |
| **weft** | **Rust** | **Linguagem** | **⭐⭐⭐⭐** | **Linguagem para IA** |
| **mca-method** | **3** | **Educação** | **⭐⭐⭐** | **MCA Framework educacional** |

---

## 🛠️ Guia de Integração

### **Para Projetos Frontend (React/Next.js)**

```markdown
1. Use awesome-design-md para consistência de UI
2. Integre Cursor ou Lovable para desenvolvimento
3. Use Raycast para automação local
```

### **Para Projetos Backend/API**

```markdown
1. Explore awesome-llm-apps para padrões
2. Use awesome-copilot para code generation
3. Implemente Composio para integrações
```

### **Para Automação & Workflows**

```markdown
1. Considere Zapier para integrações simples
2. Use awesome-openclaw-agents para templates
3. Implemente PostHog para tracking
```

### **Para o próprio Finance Web**

```markdown
1. Use finance-web-standards-guardian como primeira camada de alinhamento
2. Para backend Laravel, acione finance-web-backend-ddd-delivery
3. Para frontend Next.js, acione finance-web-frontend-ddd-delivery
4. Em mudanças fullstack, acople finance-web-api-contract-sync
5. Para revisão de branch, commits já enviados, PR, diff ou código já escrito, use finance-web-code-reviewer
6. Se a tarefa for curta ou repetitiva, ligue finance-web-token-efficiency para reduzir custo de contexto
7. Feche a entrega com finance-web-productivity-workflow + finance-web-docs-and-status-keeper
8. Em statement import, acrescente finance-web-import-review-ux
9. Em auditoria ofensiva, use cybersecurity
```

---

## 📚 Recursos Adicionais

### **Frameworks Complementares**

- **[LangChain](https://github.com/langchain-ai/langchain)** - Framework para construir apps com LLMs
- **[LlamaIndex](https://github.com/run-llama/llama_index)** - Framework para RAG
- **[Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)** - SDK oficial para Claude

### **Conceitos Importantes**

- **DESIGN.md** - Novo formato para design systems legível por IA
- **SOUL.md** - Configuração para agentes (usado em awesome-openclaw-agents)
- **RAG** - Retrieval Augmented Generation
- **Multi-Agent Systems** - Múltiplos agentes colaborando
- **Agent Orchestration** - Coordenação entre agentes

### **Documentação Oficial**

- [Google Stitch - DESIGN.md Format](https://stitch.withgoogle.com/docs/design-md/format/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Anthropic Claude Docs](https://docs.anthropic.com/)

---

## 💡 Como Contribuir

Este repositório está sempre em desenvolvimento. Para adicionar novos agentes:

### **Template para Novo Agente:**

```markdown
### **[Nome do Agente](link-github)**
- **⭐ Stars:** X.XXk+
- **Linguagem:** Linguagem(ns)
- **Descrição:** Descrição breve do que faz
- **Características:**
  - Feature 1
  - Feature 2
  - Feature 3
- **Casos de Uso:** Quando usar
- **Nível de Complexidade:** ⭐⭐⭐ (Beginner/Intermediário/Avançado)
- **Link Adicional:** (opcional)
```

### **Checklist Antes de Adicionar:**

- [ ] Repositório tem mínimo 100 stars (ou é muito relevante)
- [ ] Está ativo/em manutenção
- [ ] Tem documentação clara
- [ ] Agregar valor único ao repositório

---

## 🎯 Próximos Passos

- [ ] **NOVO:** Estudar **Task Decomposition** com:
  - [ ] Tree-of-Thought (princeton-nlp/tree-of-thought-llm) ⭐5.9k
  - [ ] Auto Decomposition (open-multi-agent) ⭐5.7k  
  - [ ] LightAgent (wanxingai/LightAgent) ⭐855
- [ ] Explorar os **84k+ MCP servers** disponíveis
- [ ] Clonar 1-2 projetos de **500-AI-Agents-Projects** como base
- [ ] **NOVO:** Estudar Spec-Driven Development com **visual-agent-orchestrator**
- [ ] Definir qual framework usar (**CrewAI/AutoGen/LangGraph/AGNO**)
- [ ] Estudar **RAG** se necessário (Awesome-LLM-RAG-Application)
- [ ] Implementar **Prompt Engineering** (awesome-prompts)
- [ ] Deploy com containerização e monitoramento
- [ ] Criar **MCP server** customizado se necessário
- [ ] Integrar com projeto Finance-Web
- [ ] Monitorar novos releases dos frameworks
- [ ] Explorar **1.370+ agentic skills** (antigravity-awesome-skills)

---

## 🔍 Workflow de Descoberta OTIMIZADO

Quando procurar por um novo agente ou caso de uso:

```
PASSO 1: VALIDAR CASO DE USO
└─ 500-AI-Agents-Projects
   ├─ Procure por indústria relevante
   ├─ Veja casos similares
   └─ Pegue código base para adaptar

PASSO 2: DEFINIR DECOMPOSIÇÃO ⭐ NOVO
├─ Seu problema é complexo? → Estude Tree-of-Thought
├─ Precisa de decomposição automática? → Use open-multi-agent
├─ Quer comparar técnicas? → Awesome-LLM-Reasoning (3.5k⭐)
└─ Precisa de benchmark? → chain-of-thought-hub (2.7k⭐)

PASSO 3: ESCOLHER FRAMEWORK  
├─ awesome-agent-quickstart (compare lado-a-lado)
├─ Ou visite:
│  ├─ CrewAI → awesome-crewai
│  ├─ LangChain → awesome-langchain  
│  ├─ LangGraph → awesome-LangGraph
│  ├─ AutoGen → awesome-multi-agent-papers
│  ├─ Griptape → griptape-ai/griptape (2.5k⭐)
│  └─ Comparação → awesome-agent-orchestration

PASSO 4: BUSCAR INTEGRAÇÕES (MCP)
├─ punkpeye/awesome-mcp-servers (84.9k⭐ - MASSIVO!)
├─ Alternativas: appcypher, wong2, yzfly/Awesome-MCP-ZH
└─ Ou descobrir via: mcpso (MCP Server Store)

PASSO 5: IMPLEMENTAR PADRÃO
├─ RAG → Awesome-LLM-RAG-Application (1.6k⭐)
├─ GraphRAG avançado → Awesome-GraphRAG (2.2k⭐)
├─ Prompts → awesome-prompts (7.6k⭐)
├─ Design UI → awesome-design-md (56k⭐)
└─ Automação → awesome-n8n-templates (21.2k⭐)

PASSO 6: OTIMIZAR & DEPLOY
├─ Context Engineering → Awesome-Context-Engineering
├─ Executar localmente → awesome-local-ai
├─ Sandbox seguro → E2B Sandbox
└─ Monitorar → awesome-ai-apps

PASSO 6: REFERÊNCIA (quando tiver dúvidas)
├─ Overview completo → awesome-LLM-resources (WangRongsheng)
├─ Papers acadêmicos → awesome-multi-agent-papers
├─ Prompt Engineering → Awesome-Prompt-Engineering
└─ Código mínimo → awesome-agent-quickstart
```

---

## 📝 Notas

- **Atualização:** Verificar novas descobertas regularmente
- **Relevância:** Removemos agentes descontinuados
- **Comunidade:** Sugestões sempre bem-vindas
- **Padrão:** Ordenamos por relevância e stars, mas destacamos favoritos com 🌟

---

**Criado em:** 16 de Abril de 2026  
**Mantido por:** Equipe Finance-Web  
**Última atualização:** 16 de Abril de 2026 (Adicionadas seções SDD e Comunidade - 60+ repositórios)

---

## 🏆 TOP Repositórios por Impacto & Prioridade

```
🌟🌟🌟 MONUMENTAL (Não pode perder!)
└─ punkpeye/awesome-mcp-servers (84,900⭐)
   └─ Maior biblioteca de integrações para agentes no GitHub!

🔥🔥🔥 CRÍTICO (Use como primeira busca)
├─ awesome-llm-apps (105k⭐) → Apps prontas para clonar
├─ 500-AI-Agents-Projects (28.5k⭐) → Validar seus casos de uso  
├─ awesome-design-md (56k⭐) → Gerar UI com IA
└─ awesome-copilot (30k⭐) → Development com IA

🔥🔥 MUITO IMPORTANTE (Tenha sempre em mãos)
├─ awesome-claude-skills (54.3k⭐) → Integrar com Claude
├─ awesome-langchain (9.2k⭐) → Projetos LangChain
├─ awesome-LLM-resources (8.0k⭐) → Overview completo
├─ awesome-prompts (7.6k⭐) → GPT prompts curados
├─ awesome-mcp-clients (6.3k⭐) → Clientes MCP
├─ awesome-MCP-ZH (6.8k⭐) → MCP em chinês
└─ awesome-mcp-servers (appcypher) (5.4k⭐) → MCP alternativa

🔥 IMPORTANTE (Consulte conforme necessário)
├─ awesome-ai-agents (27k⭐) → Pesquisa rápida
├─ awesome-openclaw-agents (2.9k⭐) → Templates prontos
├─ Awesome-Prompt-Engineering (5.7k⭐) → Técnicas de prompt
├─ Awesome-GraphRAG (2.2k⭐) → RAG avançado com grafos
├─ awesome-LangGraph (1.7k⭐) → LangGraph projects
├─ Awesome-Context-Engineering (3.0k⭐) → Production-grade systems
├─ awesome-llm-agents (1.4k⭐) → Comparação de frameworks
├─ awesome-multi-agent-papers (1.3k⭐) → Papers acadêmicos
└─ awesome-agent-quickstart (59⭐) → Hello world de frameworks

💡 ESPECIALIZADO (Quando precisa de algo específico)
├─ awesome-crewai (481⭐) → Projetos CrewAI
├─ Awesome-LLM-RAG-Application (1.6k⭐) → Implementações RAG
├─ awesome-local-ai (54⭐) → Rodar tudo localmente
├─ awesome-n8n-templates (21.2k⭐) → 280+ workflows prontos
├─ END-TO-END-GENERATIVE-AI-PROJECTS (543⭐) → Projetos completos
└─ awesome-agent-orchestration (3⭐) → Orquestração avançada
```

---

---

## 📞 Contato & Links Rápidos - TOP Repositórios

### MCP (Model Context Protocol) - 🌟 PRIORIDADE #1
- [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) - 84.9k⭐
- [appcypher/awesome-mcp-servers](https://github.com/appcypher/awesome-mcp-servers) - 5.4k⭐
- [yzfly/Awesome-MCP-ZH](https://github.com/yzfly/Awesome-MCP-ZH) - 6.8k⭐

### Casos de Uso & Projetos
- [500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects) - 28.5k⭐
- [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) - 105k⭐
- [awesome-ai-apps](https://github.com/Arindam200/awesome-ai-apps) - 10k⭐

### Design & UI
- [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) - 56k⭐
- [Awesome-Design-Tools](https://github.com/goabstract/Awesome-Design-Tools) - 39.6k⭐

### Frameworks Base
- [awesome-langchain](https://github.com/kyrolabs/awesome-langchain) - 9.2k⭐
- [awesome-LangGraph](https://github.com/von-development/awesome-LangGraph) - 1.7k⭐

### RAG & Retrieval
- [Awesome-LLM-RAG-Application](https://github.com/lizhe2004/Awesome-LLM-RAG-Application) - 1.6k⭐
- [Awesome-GraphRAG](https://github.com/DEEP-PolyU/Awesome-GraphRAG) - 2.2k⭐

### Prompt Engineering
- [awesome-prompts](https://github.com/ai-boost/awesome-prompts) - 7.6k⭐
- [Awesome-Prompt-Engineering](https://github.com/promptslab/Awesome-Prompt-Engineering) - 5.7k⭐
- [Awesome-Context-Engineering](https://github.com/Meirtz/Awesome-Context-Engineering) - 3.0k⭐

### Automação & Workflows
- [awesome-n8n-templates](https://github.com/enescingoz/awesome-n8n-templates) - 21.2k⭐
- [awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents) - 2.9k⭐

### Recursos Gerais & Comparação
- [awesome-LLM-resources](https://github.com/WangRongsheng/awesome-LLM-resources) - 8.0k⭐
- [awesome-agent-quickstart](https://github.com/ababdotai/awesome-agent-quickstart) - 59⭐
- [awesome-multi-agent-papers](https://github.com/kyegomez/awesome-multi-agent-papers) - 1.3k⭐

### Outros Links Importantes
- [GitHub Awesome Lists Oficiais](https://github.com/topics/awesome)
- [GitHub Discussions](https://github.com/discussions)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

## 📊 Estatísticas do Repositório

- **Total de Repositórios Catalogados:** 50+
- **Repositórios com 50k+ Stars:** 4 (llm-apps, design-md, claude-skills, Design-Tools)
- **Repositórios com MCP:** 10+
- **Repositórios com RAG:** 5+
- **Repositórios com Prompt Engineering:** 3+
- **Maior Repositório:** punkpeye/awesome-mcp-servers (84.9k⭐)
- **Total aproximado de Stars:** 800k+ (de todos listados!)

---

⭐ **Se este repositório foi útil para você, dê uma estrela e compartilhe!**

---

## 🎓 Para Aprender Mais

1. **Comece pelos Fundamentos:** awesome-agent-quickstart (código mínimo)
2. **Entenda a Teoria:** awesome-multi-agent-papers
3. **Explore Casos Reais:** 500-AI-Agents-Projects
4. **Integre com MCP:** punkpeye/awesome-mcp-servers
5. **Implementar RAG:** Awesome-LLM-RAG-Application
6. **Otimize Prompts:** awesome-prompts + Awesome-Prompt-Engineering
7. **Prepare para Produção:** Awesome-Context-Engineering

**Boa sorte e ótimas construções de agentes! 🚀**
