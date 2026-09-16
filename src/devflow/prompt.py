IMPLEMENTATION_PROMPT_TEMPLATE = """Create a concrete implementation plan from this context:
{user_message}

For each change, use realistic paths and state the affected component and outcome. On a revision, preserve valid work from PREVIOUS PLAN and resolve every REQUIRED CHANGE without unrelated regeneration. Map each requested change to a concise `addressed_review_items` entry that names the concrete plan change. Stay within the request; do not add speculative database or frontend work.

Return only the ImplementationPlan schema. `api_changes`, `addressed_review_items`, and `notes` contain plain strings. Keep each list to 3-5 relevant items. Do not write source code or full file contents."""


TESTING_PROMPT_TEMPLATE = """Create a testing plan strictly from this implementation plan:
{implementation_plan}

Return only TestingPlan. Include 3-4 concise core cases; each has name, type (unit, integration, or edge), description, and expected. Do not write code or invent requirements."""


SECURITY_PROMPT_TEMPLATE = """Review this implementation plan for security:
{implementation_plan}

Return only SecurityReview. Report at most 3 material findings, each with severity, issue, location, and concise recommendation. Do not invent unrelated vulnerabilities or write code."""


CODE_REVIEW_PROMPT_TEMPLATE = """Perform a plan-level review of the current plans. Judge the current implementation, not historical findings.

IMPLEMENTATION:
{implementation_plan}

TESTING:
{testing_plan}

SECURITY:
{security_review}

PREVIOUS FEEDBACK:
{previous_feedback}

Return only CodeReview. `recommendation` is exactly approve, request_changes, or needs_discussion. Request changes only for unresolved material security, testing, quality, or completeness gaps. When PREVIOUS FEEDBACK exists, verify every item is addressed by the current plan and `addressed_review_items`; do not repeat a resolved item. Include at most 3 concise items; each has category, severity, comment, and suggestion. Review plans, not code diffs."""


CODE_GENERATION_PROMPT_TEMPLATE = """Generate production-ready code from the approved plan.

REQUIREMENT:
{requirement_raw}

PLAN:
{implementation_plan}

SECURITY CONSTRAINTS:
{security_review}

Return only CodeGenerationResult. Produce at most 3-5 essential files with valid path, language, purpose, and complete concise content. Follow the plan's stack. Enforce authorization/ownership and relevant high-priority security controls. Avoid placeholder-heavy code."""
