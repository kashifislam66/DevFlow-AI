from pydantic import BaseModel, Field
from typing import List, Optional, Union

class ImplementationPlan(BaseModel):
    summary: str
    new_files: List[str] = []
    modified_files: List[str] = []
    api_changes: List[str] = []
    db_changes: List[str] = []
    frontend_changes: List[str] = []
    addressed_review_items: List[str] = []
    notes: Optional[Union[str, List[str]]] = None

class TestCase(BaseModel):
    name: str
    type: str          # unit | integration | edge
    description: str
    expected: str

class TestingPlan(BaseModel):
    summary: str
    test_cases: List[TestCase]
    notes: Optional[str] = None


class SecurityFinding(BaseModel):
    severity: str          # high | medium | low
    issue: str
    location: str          # file / endpoint / area
    recommendation: str

class SecurityReview(BaseModel):
    summary: str
    findings: List[SecurityFinding]
    overall_risk: str      # high | medium | low

class CodeReviewItem(BaseModel):
    category: str      # security | testing | quality | completeness
    severity: str      # high | medium | low
    comment: str
    suggestion: str

class CodeReview(BaseModel):
    summary: str
    items: List[CodeReviewItem]
    recommendation: str   # approve | request_changes | needs_discussion

class GeneratedFile(BaseModel):
    path: str                 # e.g. backend/app/api/invoices/download.py
    language: str             # python | php | javascript | typescript
    purpose: str              # short why this file
    content: str              # full suggested code

class CodeGenerationResult(BaseModel):
    summary: str
    files: List[GeneratedFile]
    notes: Optional[str] = None
