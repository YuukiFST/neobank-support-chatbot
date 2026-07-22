# AI-Assisted Development

## How AI Was Used

This project was built with AI assistance at every stage:

### Design Phase
- **PRD authoring**: The product requirements document was co-designed through iterative "grilling" sessions with AI, stress-testing architectural decisions and identifying edge cases.
- **Wayfinder map**: AI helped create the ticket-based implementation plan, breaking down the PRD into actionable work items.

### Development Phase
- **Code generation**: AI assisted in generating boilerplate code, domain models, API contracts, and infrastructure configurations.
- **Test generation**: Unit tests, integration tests, and E2E test scaffolds were generated with AI assistance.
- **Architecture decisions**: AI helped evaluate tradeoffs (e.g., why Redis over Kafka for this scale, why LangGraph over CrewAI).

### Quality Phase
- **Code review**: AI performed security-focused code review, identifying potential PII leakage, injection vectors, and authorization gaps.
- **Test coverage**: AI helped design the eval set and scoring criteria for the LLM-as-judge evaluation.

### Tools Used
- **Claude/Anthropic**: Primary AI assistant for architecture, code generation, and review
- **GitHub Copilot**: Code completion and suggestions
- **LangChain/LangGraph**: Agent framework (not AI-generated, but informed by AI documentation)

### Evidence
- This file serves as evidence of AI-assisted development
- CI carries an optional AI code-review step
- The wayfinder map and PRD are artifacts of AI-assisted design
