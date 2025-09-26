# 13. LLM Integration Design

**Document Version:** 1.0.0
**Last Updated:** 2025-09-26
**Contributors:** BMAD Orchestrator
**Status:** Draft

## Change History

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-09-26 | 1.0.0 | Initial draft | BMAD Orchestrator |

## Table of Contents

1. [Overview and Requirements](#overview-and-requirements)
   - Purpose of LLM Integration
   - Integration Requirements
   - Security Considerations

2. [Integration Options Analysis](#integration-options-analysis)
   - Supabase Edge Functions Approach
   - Direct Client-side Integration
   - API Gateway Integration
   - Comparison Matrix

3. [Technical Design Specifications](#technical-design-specifications)
   - Configuration Management
   - Security Implementation
   - Performance Optimizations
   - Monitoring and Logging

4. [Implementation Recommendations](#implementation-recommendations)
   - Recommended Approach
   - Implementation Steps
   - Configuration Templates
   - Testing Strategy

5. [Integration with Existing Architecture](#integration-with-existing-architecture)
   - Architectural Impact
   - Required Changes
   - Migration Strategy
   - Monitoring and Maintenance

6. [Service Provider Integration](#service-provider-integration)
   - LLM Service Provider Setup
     - Provider Service Factory
     - Provider Dependencies
   - Integration with Features
     - Epic Title Generation
     - Prompt Builder Pattern
   - Configuration Management
     - Environment Settings
     - Settings Management

7. [Appendix](#appendix)
   - Reference Documentation
   - Security Compliance Checklist
   - Performance Benchmarks
   - Cost Analysis

## Overview and Requirements

### Purpose of LLM Integration

SprintSense currently implements several AI-powered features using traditional NLP and machine learning approaches. The integration of Large Language Models (LLMs) aims to enhance these capabilities with more sophisticated natural language understanding and generation capabilities.

#### Core Use Cases
1. **Enhanced Work Item Analysis**
   - Improve the existing AI prioritization service with better semantic understanding
   - Enhance the clustering algorithm's accuracy for epic suggestions
   - Provide more detailed and context-aware work item recommendations

2. **Intelligent Task Generation**
   - Generate detailed task breakdowns from epic descriptions
   - Suggest acceptance criteria based on requirements
   - Create test scenarios based on feature specifications

3. **Natural Language Interaction**
   - Allow users to describe features in natural language
   - Generate technical specifications from user stories
   - Provide contextual help and suggestions during sprint planning

#### Business Value
- Reduce time spent on manual task breakdown and specification writing
- Improve accuracy of work item relationships and dependencies
- Enhance sprint planning efficiency with AI-assisted estimation
- Provide more consistent and comprehensive documentation
- Enable natural language interfaces for increased accessibility

### Integration Requirements

#### Performance Requirements
1. **Response Time**
   - Synchronous operations: < 500ms (matching existing AI service SLA)
   - Asynchronous operations: < 5s for complex generations
   - Background tasks: No specific time constraint

2. **Scalability Needs**
   - Support concurrent requests from multiple team members
   - Handle teams with up to 1000 work items (current system limit)
   - Scale to support multiple projects within workspace

3. **Resource Constraints**
   - Memory usage: Within existing Redis cache limits
   - CPU utilization: < 30% increase over current AI services
   - Storage: Minimize token storage for cost efficiency

#### Cost Constraints
1. **Token Budget**
   - Define monthly token allocation per team
   - Implement token usage tracking and alerts
   - Provide cost estimation tools for self-hosted instances

2. **API Costs**
   - Optimize prompt design for token efficiency
   - Implement caching strategies for common operations
   - Allow configuration of different LLM providers based on cost preferences

#### Compliance Requirements
1. **Data Privacy**
   - All data processing must occur within project boundaries
   - No persistent storage of prompts or responses
   - Comply with workspace data retention policies

2. **Security Controls**
   - Role-based access control for LLM features
   - Audit logging of all LLM interactions
   - Sanitization of inputs and outputs

### Security Considerations

#### Data Privacy Requirements
1. **Data Handling**
   - No sensitive data in prompts (PII, secrets, etc.)
   - Implement data filtering and masking
   - Maintain data locality requirements

2. **Transmission Security**
   - Secure communication with LLM providers
   - End-to-end encryption for all requests
   - TLS 1.3 minimum for API communications

#### API Key Management
1. **Key Storage**
   - Use secure environment variables
   - Implement key rotation mechanism
   - Support multiple provider keys

2. **Access Control**
   - Role-based feature access
   - Usage quotas per team/user
   - Request authentication and authorization

#### User Data Protection
1. **Privacy Controls**
   - User opt-out mechanisms
   - Data minimization in prompts
   - Clear user notification of LLM usage

2. **Compliance Standards**
   - GDPR compliance for EU users
   - CCPA compliance for California users
   - SOC 2 compliance for enterprise customers

## Integration Options Analysis

Based on our current architecture and infrastructure, we have evaluated three primary approaches for LLM integration. Each approach has been analyzed considering our modular monolith architecture, existing Supabase integration, and self-hosting requirements.

### 1. Supabase Edge Functions Approach

#### Architecture Overview
```mermaid
graph TD
    subgraph "Client"
        A[React SPA]
    end

    subgraph "Edge Function"
        B[LLM Handler]
        C[Token Management]
        D[Response Processing]
    end

    subgraph "External"
        E[LLM Provider API]
    end

    A --> B
    B --> C
    B --> D
    B --> E
```

#### Characteristics
- **Deployment**: Leverages existing Supabase Edge Functions infrastructure
- **Scaling**: Automatic scaling through Supabase's infrastructure
- **Integration**: Direct integration with existing Supabase auth and database

#### Pros
1. Simplified deployment and management
2. Built-in monitoring and logging
3. Automatic scaling and failover
4. Consistent with current infrastructure
5. Reduced latency through edge deployment

#### Cons
1. Limited debugging capabilities
2. Higher cost for frequent requests
3. Cold start latency on first request
4. Less control over infrastructure
5. Limited local development experience

#### Cost Analysis
- Edge Function compute: $0.50 per 1M invocations
- Additional bandwidth costs
- LLM provider costs passed through

### 2. Direct Client-side Integration

#### Architecture Overview
```mermaid
graph TD
    subgraph "Client"
        A[React SPA]
        B[LLM Client]
        C[Token Management]
    end

    subgraph "Backend"
        D[Token Service]
        E[Usage Monitor]
    end

    subgraph "External"
        F[LLM Provider API]
    end

    A --> B
    B --> C
    C --> D
    B --> F
    B --> E
```

#### Characteristics
- **Deployment**: Client-side implementation
- **Scaling**: Per-user scaling
- **Integration**: Requires token management service

#### Pros
1. Reduced server load
2. Lower latency for users
3. Simpler deployment
4. Direct user interactions
5. Easier debugging

#### Cons
1. Security risks with API keys
2. Inconsistent performance
3. Higher client-side complexity
4. Limited token management
5. Increased frontend bundle size

#### Cost Analysis
- No additional infrastructure costs
- Direct LLM provider costs
- Potential for token misuse

### 3. API Gateway Integration

#### Architecture Overview
```mermaid
graph TD
    subgraph "Client"
        A[React SPA]
    end

    subgraph "Backend"
        B[FastAPI Gateway]
        C[LLM Service]
        D[Cache Layer]
        E[Token Manager]
    end

    subgraph "External"
        F[LLM Provider API]
    end

    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
```

#### Characteristics
- **Deployment**: Integrated with existing FastAPI backend
- **Scaling**: Controlled through existing infrastructure
- **Integration**: Full access to application context

#### Pros
1. Complete control over implementation
2. Integrated security model
3. Efficient caching strategies
4. Access to full application context
5. Consistent with current architecture

#### Cons
1. Higher maintenance overhead
2. Additional server resources required
3. More complex deployment
4. Potential bottleneck at API layer
5. Increased operational complexity

#### Cost Analysis
- Increased server resource usage
- Predictable infrastructure costs
- Optimizable token usage

### Comparison Matrix

| Criteria | Supabase Edge | Direct Client | API Gateway |
|----------|---------------|---------------|-------------|
| **Development Complexity** | Medium | High | Low |
| **Deployment Complexity** | Low | Low | Medium |
| **Maintenance Overhead** | Low | Medium | High |
| **Security** | High | Low | High |
| **Scalability** | High | Medium | Medium |
| **Cost Efficiency** | Medium | High | High |
| **Performance** | High | High | Medium |
| **Monitoring** | Built-in | Limited | Custom |
| **Local Testing** | Limited | Easy | Easy |
| **Context Access** | Limited | Limited | Full |

### Decision Criteria

Based on our current architecture and requirements, we evaluate each option against the following weighted criteria:

1. **Security (30%)**
   - API key management
   - Data privacy
   - Access control

2. **Integration (25%)**
   - Existing architecture fit
   - Development workflow
   - Maintenance requirements

3. **Performance (20%)**
   - Response times
   - Scalability
   - Resource efficiency

4. **Cost (15%)**
   - Infrastructure costs
   - Development effort
   - Operational overhead

5. **Developer Experience (10%)**
   - Local development
   - Debugging capabilities
   - Deployment process

### Scoring (1-5 scale)

| Criteria | Weight | Supabase Edge | Direct Client | API Gateway |
|----------|--------|---------------|---------------|-------------|
| Security | 30% | 4.5 (1.35) | 2.0 (0.60) | 4.5 (1.35) |
| Integration | 25% | 4.0 (1.00) | 3.0 (0.75) | 5.0 (1.25) |
| Performance | 20% | 4.0 (0.80) | 4.5 (0.90) | 3.5 (0.70) |
| Cost | 15% | 3.5 (0.53) | 4.0 (0.60) | 4.0 (0.60) |
| Dev Experience | 10% | 3.0 (0.30) | 4.0 (0.40) | 4.5 (0.45) |
| **Total** | 100% | **3.98** | **3.25** | **4.35** |

## Technical Design Specifications

Based on the selected API Gateway Integration approach, here are the detailed technical specifications for implementing LLM integration within our modular monolith architecture.

### Configuration Management

#### Environment Variables Structure
```env
# LLM Provider Configuration
LLM_PROVIDER=openai|anthropic|other
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4|claude-2|other
LLM_MAX_TOKENS=8192
LLM_TEMPERATURE=0.7

# Rate Limiting
LLM_RATE_LIMIT_REQUESTS=100
LLM_RATE_LIMIT_WINDOW=60  # seconds

# Caching Configuration
LLM_CACHE_TTL=3600  # seconds
LLM_CACHE_MAX_ITEMS=10000

# Monitoring
LLM_ENABLE_TELEMETRY=true
LLM_LOG_LEVEL=INFO

# Security
LLM_MAX_PROMPT_TOKENS=4096
LLM_ALLOWED_MODELS=["gpt-4","claude-2"]
LLM_KEY_ROTATION_INTERVAL=90  # days
```

#### Configuration Template
```python
# app/core/config/llm.py

from pydantic import BaseSettings, Field
from typing import List, Optional

class LLMSettings(BaseSettings):
    provider: str = Field(..., env='LLM_PROVIDER')
    api_key: str = Field(..., env='LLM_API_KEY')
    model: str = Field(..., env='LLM_MODEL')
    max_tokens: int = Field(8192, env='LLM_MAX_TOKENS')
    temperature: float = Field(0.7, env='LLM_TEMPERATURE')
    
    rate_limit_requests: int = Field(100, env='LLM_RATE_LIMIT_REQUESTS')
    rate_limit_window: int = Field(60, env='LLM_RATE_LIMIT_WINDOW')
    
    cache_ttl: int = Field(3600, env='LLM_CACHE_TTL')
    cache_max_items: int = Field(10000, env='LLM_CACHE_MAX_ITEMS')
    
    enable_telemetry: bool = Field(True, env='LLM_ENABLE_TELEMETRY')
    log_level: str = Field('INFO', env='LLM_LOG_LEVEL')
    
    max_prompt_tokens: int = Field(4096, env='LLM_MAX_PROMPT_TOKENS')
    allowed_models: List[str] = Field(['gpt-4', 'claude-2'], env='LLM_ALLOWED_MODELS')
    key_rotation_interval: int = Field(90, env='LLM_KEY_ROTATION_INTERVAL')
    
    class Config:
        env_file = '.env'
```

#### Secret Management
1. API Key Storage
   ```python
   # app/core/security/key_manager.py
   
   from cryptography.fernet import Fernet
   from datetime import datetime, timedelta
   
   class APIKeyManager:
       def __init__(self, encryption_key: bytes):
           self.fernet = Fernet(encryption_key)
           self.rotation_schedule = timedelta(days=settings.key_rotation_interval)
       
       def encrypt_key(self, api_key: str) -> bytes:
           return self.fernet.encrypt(api_key.encode())
       
       def decrypt_key(self, encrypted_key: bytes) -> str:
           return self.fernet.decrypt(encrypted_key).decode()
       
       def should_rotate(self, last_rotation: datetime) -> bool:
           return datetime.now() - last_rotation >= self.rotation_schedule
   ```

### Security Implementation

#### Authentication Flow
```mermaid
sequenceDiagram
    participant C as Client
    participant G as API Gateway
    participant A as Auth Service
    participant L as LLM Service
    participant P as LLM Provider

    C->>G: Request with JWT
    G->>A: Validate JWT
    A-->>G: User Context
    G->>L: Forward Request + Context
    L->>L: Rate Limit Check
    L->>L: Token Validation
    L->>P: LLM API Request
    P-->>L: LLM Response
    L-->>G: Processed Response
    G-->>C: Final Response
```

#### Authorization Rules
```python
# app/domains/llm/permissions.py

from enum import Enum
from typing import List

class LLMPermission(str, Enum):
    GENERATE = 'llm:generate'
    TRAIN = 'llm:train'
    MANAGE = 'llm:manage'

class LLMAuthorizer:
    def __init__(self, user_context: UserContext):
        self.context = user_context
        self.team_permissions = self._load_team_permissions()
    
    def can_generate(self, team_id: str) -> bool:
        return self._has_permission(team_id, LLMPermission.GENERATE)
    
    def can_train(self, team_id: str) -> bool:
        return self._has_permission(team_id, LLMPermission.TRAIN)
```

### Performance Optimizations

#### Rate Limiting Implementation
```python
# app/core/middleware/rate_limiter.py

from fastapi import Request
from redis import Redis
from datetime import datetime

class LLMRateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.window = settings.rate_limit_window
        self.max_requests = settings.rate_limit_requests
    
    async def check_rate_limit(self, request: Request) -> bool:
        key = f"ratelimit:{request.user.id}:{datetime.now().minute}"
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, self.window)
        return current <= self.max_requests
```

#### Caching Strategy
```python
# app/domains/llm/cache.py

from hashlib import sha256
from typing import Optional

class LLMCache:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.ttl = settings.cache_ttl
    
    def generate_cache_key(self, prompt: str, params: dict) -> str:
        content = f"{prompt}:{sorted(params.items())}"
        return f"llm:cache:{sha256(content.encode()).hexdigest()}"
    
    async def get_cached_response(self, key: str) -> Optional[str]:
        return await self.redis.get(key)
    
    async def cache_response(self, key: str, response: str) -> None:
        await self.redis.setex(key, self.ttl, response)
```

### Monitoring and Logging

#### Metrics Collection
```python
# app/core/monitoring/llm_metrics.py

from prometheus_client import Counter, Histogram
from typing import Dict

class LLMMetrics:
    def __init__(self):
        self.requests_total = Counter(
            'llm_requests_total',
            'Total LLM API requests',
            ['model', 'status']
        )
        self.tokens_used = Counter(
            'llm_tokens_total',
            'Total tokens used',
            ['model', 'type']
        )
        self.latency = Histogram(
            'llm_request_duration_seconds',
            'LLM request duration in seconds',
            ['model']
        )
```

#### Log Management
```python
# app/core/logging/llm_logger.py

import structlog
from typing import Any, Dict

logger = structlog.get_logger('llm_service')

class LLMLogger:
    def __init__(self):
        self.logger = logger.bind(service='llm')
    
    def log_request(self, request_id: str, context: Dict[str, Any]):
        self.logger.info('llm_request_started',
            request_id=request_id,
            user_id=context.get('user_id'),
            team_id=context.get('team_id'),
            model=context.get('model')
        )
    
    def log_response(self, request_id: str, metrics: Dict[str, Any]):
        self.logger.info('llm_request_completed',
            request_id=request_id,
            duration_ms=metrics.get('duration_ms'),
            tokens_used=metrics.get('tokens_used'),
            cache_hit=metrics.get('cache_hit')
        )
```

#### Alert Configuration
```yaml
# monitoring/alert_rules.yml

groups:
  - name: llm_alerts
    rules:
      - alert: HighLLMLatency
        expr: rate(llm_request_duration_seconds_sum[5m]) / rate(llm_request_duration_seconds_count[5m]) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High LLM API latency
          
      - alert: HighErrorRate
        expr: rate(llm_requests_total{status="error"}[5m]) / rate(llm_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
          
      - alert: TokenQuotaNearLimit
        expr: sum(increase(llm_tokens_total[24h])) > 0.8 * token_quota
        labels:
          severity: warning
```

### Privacy and Redaction Policy

#### Content Redaction System
```python
# app/core/privacy/redaction.py

from typing import Dict, List, Pattern, Set
import re
from pydantic import BaseModel, Field

class RedactionPattern(BaseModel):
    """Defines a pattern to be redacted from text."""
    name: str
    pattern: str
    replacement: str = Field(default="[REDACTED]")
    description: str
    priority: int = Field(default=0, ge=0, le=100)

class ContentRedactor:
    def __init__(self):
        self.patterns: Dict[str, RedactionPattern] = {
            # High-priority patterns (checked first)
            "api_key": RedactionPattern(
                name="api_key",
                pattern=r"(['\"]?(?:api[_-]?key|token|secret)['\"]?\s*[:=]\s*['\"]?)[^'\"\s]+",
                replacement="[API_KEY]",
                description="API keys and tokens",
                priority=100
            ),
            "email": RedactionPattern(
                name="email",
                pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                replacement="[EMAIL]",
                description="Email addresses",
                priority=90
            ),
            "ip_address": RedactionPattern(
                name="ip_address",
                pattern=r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                replacement="[IP_ADDRESS]",
                description="IP addresses",
                priority=80
            ),
            # Medium-priority patterns
            "password": RedactionPattern(
                name="password",
                pattern=r"(?i)password\s*[:=]\s*[^\s]+",
                replacement="[PASSWORD]",
                description="Password fields",
                priority=50
            ),
            # Project-specific patterns
            "team_secret": RedactionPattern(
                name="team_secret",
                pattern=r"team_[a-zA-Z0-9]{32}",
                replacement="[TEAM_SECRET]",
                description="Team-specific secret keys",
                priority=45
            )
        }
        self._compiled_patterns: Dict[str, Pattern] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile all regex patterns for performance."""
        for name, pattern in self.patterns.items():
            self._compiled_patterns[name] = re.compile(pattern.pattern)

    def redact_text(self, text: str) -> str:
        """Redact sensitive information from text."""
        result = text
        for name, pattern in sorted(
            self.patterns.items(),
            key=lambda x: x[1].priority,
            reverse=True
        ):
            result = self._compiled_patterns[name].sub(
                pattern.replacement,
                result
            )
        return result

    def get_sensitive_types(self, text: str) -> Set[str]:
        """Return set of sensitive data types found in text."""
        found_types = set()
        for name, pattern in self._compiled_patterns.items():
            if pattern.search(text):
                found_types.add(name)
        return found_types

class PromptSanitizer:
    def __init__(self, redactor: ContentRedactor):
        self.redactor = redactor
        self.max_prompt_length = 4096  # Configurable

    async def sanitize_prompt(
        self,
        prompt: str,
        context: Dict[str, str]
    ) -> str:
        """Sanitize prompt before sending to LLM."""
        # First pass: Redact sensitive information
        sanitized = self.redactor.redact_text(prompt)

        # Second pass: Validate length
        if len(sanitized) > self.max_prompt_length:
            sanitized = sanitized[:self.max_prompt_length]

        # Log detected sensitive data types (but not content)
        sensitive_types = self.redactor.get_sensitive_types(prompt)
        if sensitive_types:
            logger.warning(
                "Sensitive data types detected in prompt",
                types=list(sensitive_types),
                **context
            )

        return sanitized
```

#### Integration with LLM Service
```python
# app/domains/llm/service.py

from app.core.privacy.redaction import PromptSanitizer, ContentRedactor

class LLMService:
    def __init__(
        self,
        provider: ILLMProvider,
        sanitizer: PromptSanitizer = Depends(get_prompt_sanitizer),
        # ... other dependencies
    ):
        self.provider = provider
        self.sanitizer = sanitizer
        # ... other initializations

    async def generate(
        self,
        prompt: str,
        params: Dict[str, Any],
        context: Dict[str, str],
        cache_ttl: Optional[int] = 3600
    ) -> ILLMResponse:
        # Sanitize prompt before processing
        sanitized_prompt = await self.sanitizer.sanitize_prompt(
            prompt,
            context
        )

        # Process sanitized prompt
        # ... rest of the generate method
```

#### Privacy Monitoring and Alerts
```yaml
# monitoring/prometheus/privacy_rules.yml

groups:
  - name: privacy_alerts
    rules:
      - alert: SensitiveDataDetected
        expr: rate(llm_sensitive_data_detected_total[5m]) > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: Sensitive data detected in LLM prompts
          description: "{{ $value }} instances of sensitive data detected"

      - alert: HighSensitiveDataRate
        expr: rate(llm_sensitive_data_detected_total[1h]) > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High rate of sensitive data detection
          description: "Unusual spike in sensitive data detection rate"
```

#### Data Retention Policy
1. **Prompt Storage**
   - Raw prompts are never stored
   - Only sanitized versions may be cached
   - Cache TTL maximum of 24 hours for sanitized prompts

2. **Response Storage**
   - Responses are scanned for accidentally regenerated sensitive data
   - Responses containing sensitive data are not cached
   - All stored responses have an audit trail

3. **Audit Logs**
   - Keep privacy-related audit logs for 90 days
   - Audit logs only contain metadata, no prompt/response content
   - Regular audit log review process

4. **Emergency Response**
   - Immediate cache flush capability
   - Automated sensitive data alerts
   - Incident response procedures

#### Unit Tests Organization

```python
# tests/core/privacy/__init__.py

"""Privacy and redaction test suite.

Test organization:
- test_redaction_base.py: Core redaction functionality
- test_patterns/: Pattern-specific tests
  - test_api_keys.py: API key patterns
  - test_emails.py: Email patterns
  - test_network.py: IP and network patterns
  - test_auth.py: Authentication data patterns
  - test_project.py: Project-specific patterns
- test_redaction_integration.py: Integration tests
"""

from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / 'test_data'
```

```python
# tests/core/privacy/conftest.py

import pytest
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock
from app.core.privacy.redaction import ContentRedactor, PromptSanitizer

@pytest.fixture
def mock_logger(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("app.core.privacy.redaction.logger", mock)
    return mock

@pytest.fixture
def redactor() -> ContentRedactor:
    return ContentRedactor()

@pytest.fixture
def sanitizer(redactor) -> PromptSanitizer:
    return PromptSanitizer(redactor)

@pytest.fixture
def mock_llm_provider() -> AsyncMock:
    provider = AsyncMock()
    provider.complete.return_value = {
        "content": "Processed response",
        "tokens_used": 10,
        "model": "test-model"
    }
    return provider
```

```python
# tests/core/privacy/test_redaction_base.py

import pytest
from datetime import datetime
from app.core.privacy.redaction import RedactionPattern

class TestRedactionPattern:
    """Test basic RedactionPattern functionality."""
    
    def test_pattern_validation(self):
        """Test pattern validation rules."""
        pattern = RedactionPattern(
            name="test",
            pattern=r"test\d+",
            description="Test pattern"
        )
        assert pattern.name == "test"
        assert pattern.replacement == "[REDACTED]"
        
        with pytest.raises(ValueError):
            RedactionPattern(
                name="test",
                pattern=r"test\d+",
                description="Test pattern",
                priority=101  # Over max
            )
    
    def test_pattern_compilation(self):
        """Test regex pattern compilation."""
        pattern = RedactionPattern(
            name="test",
            pattern=r"test\d+",
            description="Test pattern"
        )
        import re
        compiled = re.compile(pattern.pattern)
        assert compiled.match("test123")
        assert not compiled.match("invalid")

class TestContentRedactor:
    """Test ContentRedactor base functionality."""
    
    def test_initialization(self, redactor):
        """Test redactor initialization."""
        assert len(redactor.patterns) > 0
        assert all(isinstance(p, RedactionPattern) 
                  for p in redactor.patterns.values())
    
    def test_pattern_priority_ordering(self, redactor):
        """Test patterns are processed in priority order."""
        # Add test patterns with different priorities
        redactor.patterns.update({
            "high": RedactionPattern(
                name="high",
                pattern=r"high_\w+",
                description="High priority",
                priority=100
            ),
            "low": RedactionPattern(
                name="low",
                pattern=r"low_\w+",
                description="Low priority",
                priority=1
            )
        })
        
        text = "low_value high_value"
        redacted = redactor.redact_text(text)
        
        # High priority pattern should be processed first
        assert "[REDACTED] [REDACTED]" in redacted
```

```python
# tests/core/privacy/test_patterns/test_api_keys.py

import pytest
from app.core.privacy.redaction import ContentRedactor

@pytest.mark.patterns
class TestAPIKeyPatterns:
    """Test API key and token redaction patterns."""
    
    @pytest.mark.parametrize("test_input,expected", [
        # Basic API Keys
        (
            'API_KEY="sk_live_12345"',
            '[API_KEY]'
        ),
        (
            'api_key: pk_test_abcde',
            '[API_KEY]'
        ),
        # OpenAI Style
        (
            'secret_key = "sk-0123456789abcdef"',
            '[API_KEY]'
        ),
        # Bearer Tokens
        (
            'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
            '[API_KEY]'
        ),
        # Mixed Content
        (
            'API_KEY=12345\nBearer token123',
            '[API_KEY]\n[API_KEY]'
        )
    ])
    def test_api_key_redaction(self, redactor, test_input, expected):
        """Test various API key formats are redacted."""
        redacted = redactor.redact_text(test_input)
        assert expected in redacted
```

```python
# tests/core/privacy/test_patterns/test_network.py

import pytest
from app.core.privacy.redaction import ContentRedactor

@pytest.mark.patterns
class TestNetworkPatterns:
    """Test network-related redaction patterns."""
    
    @pytest.mark.parametrize("test_input,expected", [
        # IPv4 Addresses
        (
            '192.168.1.1',
            '[IP_ADDRESS]'
        ),
        # CIDR Notation
        (
            '10.0.0.0/24',
            '[IP_ADDRESS]'
        ),
        # IPv6 Addresses
        (
            '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
            '[IP_ADDRESS]'
        ),
        # Database URLs
        (
            'postgresql://user:pass@db.internal:5432/mydb',
            '[DB_CONNECTION_STRING]'
        ),
        # Internal References
        (
            'server_id=prod-db-01.internal',
            '[INTERNAL_REFERENCE]'
        )
    ])
    def test_network_redaction(self, redactor, test_input, expected):
        """Test network identifier redaction."""
        redacted = redactor.redact_text(test_input)
        assert expected in redacted
```

```python
# tests/core/privacy/test_patterns/test_project.py

import pytest
from app.core.privacy.redaction import ContentRedactor

@pytest.mark.patterns
class TestProjectPatterns:
    """Test project-specific redaction patterns."""
    
    @pytest.mark.parametrize("test_input,expected", [
        # Team IDs
        (
            'team_5f3c9e1b-8520-4c58-bc45-d3c97c9f34a2',
            '[TEAM_ID]'
        ),
        # Sprint References
        (
            'sprint_2025_q3_week12_team5',
            '[SPRINT_REFERENCE]'
        ),
        # User IDs
        (
            'user_id=auth0|12345',
            '[USER_ID]'
        )
    ])
    def test_project_redaction(self, redactor, test_input, expected):
        """Test project identifier redaction."""
        redacted = redactor.redact_text(test_input)
        assert expected in redacted
        
    def test_mixed_project_data(self, redactor):
        """Test handling of mixed project identifiers."""
        text = (
            "team_abc123 working on sprint_2025_q1 with "
            "user_id=xyz789 accessing db_prod_01"
        )
        redacted = redactor.redact_text(text)
        
        assert "team_abc123" not in redacted
        assert "sprint_2025_q1" not in redacted
        assert "user_id=xyz789" not in redacted
        assert "db_prod_01" not in redacted
```

```python
# tests/core/privacy/test_redaction_integration.py

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Set
from datetime import datetime

from app.core.privacy.redaction import (
    RedactionPattern,
    ContentRedactor,
    PromptSanitizer
)

@pytest.fixture
def sample_patterns() -> Dict[str, RedactionPattern]:
    return {
        "api_key": RedactionPattern(
            name="api_key",
            pattern=r"api_key[=:]\s*[\w-]+",
            replacement="[API_KEY]",
            description="API key pattern",
            priority=100
        ),
        "email": RedactionPattern(
            name="email",
            pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            replacement="[EMAIL]",
            description="Email addresses",
            priority=90
        )
    }

@pytest.fixture
def mock_logger(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("app.core.privacy.redaction.logger", mock)
    return mock

class TestRedactionPattern:
    def test_pattern_validation(self):
        # Test valid pattern
        pattern = RedactionPattern(
            name="test",
            pattern=r"test\d+",
            description="Test pattern"
        )
        assert pattern.name == "test"
        assert pattern.replacement == "[REDACTED]"
        
        # Test invalid priority
        with pytest.raises(ValueError):
            RedactionPattern(
                name="test",
                pattern=r"test\d+",
                description="Test pattern",
                priority=101  # Over max
            )

class TestContentRedactor:
    def test_initialization(self, sample_patterns):
        redactor = ContentRedactor()
        assert len(redactor.patterns) >= 2
        assert all(isinstance(p, RedactionPattern) 
                  for p in redactor.patterns.values())

    @pytest.mark.parametrize("input_text,expected_output", [
        (
            "My api_key=1234567890",
            "My [API_KEY]"
        ),
        (
            "Contact user@example.com for support",
            "Contact [EMAIL] for support"
        ),
        (
            "Multiple patterns: api_key=secret user@example.com",
            "Multiple patterns: [API_KEY] [EMAIL]"
        ),
        (
            "No sensitive data here",
            "No sensitive data here"
        )
    ])
    def test_redact_text(self, input_text, expected_output):
        redactor = ContentRedactor()
        assert redactor.redact_text(input_text) == expected_output

    def test_pattern_priority(self):
        redactor = ContentRedactor()
        text = "SECRET_KEY=abc123 password=123456"
        redacted = redactor.redact_text(text)
        
        # Higher priority pattern (SECRET_KEY) should be processed first
        assert "[API_KEY]" in redacted
        assert "[PASSWORD]" in redacted

    def test_get_sensitive_types(self):
        redactor = ContentRedactor()
        text = "Contact admin@example.com, API_KEY=secret123"
        types = redactor.get_sensitive_types(text)
        
        assert "email" in types
        assert "api_key" in types
        assert len(types) == 2

    @pytest.mark.parametrize("pattern_type,test_input,expected_replacement", [
        # API Keys and Tokens
        (
            "api_key",
            'API_KEY="sk_live_12345"\napi_key: pk_test_abcde',
            '[API_KEY]'
        ),
        (
            "api_key",
            'secret_key = "sk-0123456789abcdef"',  # OpenAI-style key
            '[API_KEY]'
        ),
        (
            "api_key",
            'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',  # JWT token
            '[API_KEY]'
        ),
        # Email Addresses
        (
            "email",
            'user+label@example.com',  # Email with label
            '[EMAIL]'
        ),
        (
            "email",
            'user.name@subdomain.example.co.uk',  # Complex domain
            '[EMAIL]'
        ),
        (
            "email",
            'македонски@пример.мкд',  # Unicode email
            '[EMAIL]'
        ),
        # IP Addresses
        (
            "ip_address",
            '10.0.0.0/24 and 192.168.1.1',  # CIDR notation
            '[IP_ADDRESS] and [IP_ADDRESS]'
        ),
        (
            "ip_address",
            '2001:0db8:85a3:0000:0000:8a2e:0370:7334',  # IPv6
            '[IP_ADDRESS]'
        ),
        (
            "ip_address",
            'hostname: localhost (127.0.0.1)',  # Localhost
            'hostname: localhost ([IP_ADDRESS])'
        ),
        # Database Connection Strings
        (
            "db_connection",
            'postgresql://user:password@localhost:5432/db',
            '[DB_CONNECTION_STRING]'
        ),
        (
            "db_connection",
            'mysql://app_user:secret123@db.example.com:3306/prod_db',
            '[DB_CONNECTION_STRING]'
        ),
        # AWS-style Keys
        (
            "aws_key",
            'aws_access_key_id=AKIA1234567890EXAMPLE',
            '[AWS_KEY]'
        ),
        (
            "aws_key",
            'aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            '[AWS_KEY]'
        ),
        # Internal System References
        (
            "internal_ref",
            'server_id=prod-db-01.internal',
            '[INTERNAL_REFERENCE]'
        ),
        (
            "internal_ref",
            'Load balancer: internal-lb-1.prod.example.com',
            '[INTERNAL_REFERENCE]'
        ),
        # Authentication Data
        (
            "auth_data",
            'session_token=abc123def456',
            '[AUTH_TOKEN]'
        ),
        (
            "auth_data",
            'refresh_token: eyJhbGciOiJIUzI1NiJ9...',
            '[AUTH_TOKEN]'
        ),
        # Project-Specific Patterns
        (
            "team_id",
            'team_5f3c9e1b-8520-4c58-bc45-d3c97c9f34a2',
            '[TEAM_ID]'
        ),
        (
            "sprint_ref",
            'sprint_2025_q3_week12_team5',
            '[SPRINT_REFERENCE]'
        )
    ])
    def test_specific_patterns(self, pattern_type, test_input):
        redactor = ContentRedactor()
        redacted = redactor.redact_text(test_input)
        
        # Original sensitive data should not be present
        assert test_input not in redacted
        # Replacement marker should be present
        assert redactor.patterns[pattern_type].replacement in redacted

class TestPromptSanitizer:
    @pytest.fixture
    def sanitizer(self):
        redactor = ContentRedactor()
        return PromptSanitizer(redactor)

    @pytest.mark.asyncio
    async def test_sanitize_prompt(self, sanitizer, mock_logger):
        prompt = "Here's my api_key=secret123 and email@test.com"
        context = {"user_id": "123", "request_id": "abc"}
        
        sanitized = await sanitizer.sanitize_prompt(prompt, context)
        
        assert "api_key=secret123" not in sanitized
        assert "email@test.com" not in sanitized
        assert "[API_KEY]" in sanitized
        assert "[EMAIL]" in sanitized
        
        # Verify logging
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0]
        assert "Sensitive data detected" in call_args[0]

    @pytest.mark.asyncio
    async def test_max_length_enforcement(self, sanitizer):
        # Create prompt longer than max length
        long_prompt = "x" * (sanitizer.max_prompt_length + 100)
        context = {"user_id": "123"}
        
        sanitized = await sanitizer.sanitize_prompt(long_prompt, context)
        assert len(sanitized) <= sanitizer.max_prompt_length

    @pytest.mark.asyncio
    async def test_empty_prompt(self, sanitizer):
        sanitized = await sanitizer.sanitize_prompt("", {"user_id": "123"})
        assert sanitized == ""

    @pytest.mark.asyncio
    async def test_multiple_patterns_same_line(self, sanitizer):
        prompt = "User email@test.com has api_key=secret123 and password=abc123"
        sanitized = await sanitizer.sanitize_prompt(prompt, {"user_id": "123"})
        
        assert all(x in sanitized for x in ["[EMAIL]", "[API_KEY]", "[PASSWORD]"])
        assert all(x not in sanitized for x in 
                  ["email@test.com", "api_key=secret123", "password=abc123"])

@pytest.mark.integration
class TestRedactionIntegration:
    @pytest.mark.asyncio
    async def test_redaction_with_llm_service(
        self,
        sanitizer: PromptSanitizer,
        mock_llm_provider: AsyncMock
    ):
        # Setup mock LLM provider
        mock_llm_provider.complete.return_value = {
            "content": "Processed response",
            "tokens_used": 10
        }
        
        service = LLMService(
            provider=mock_llm_provider,
            sanitizer=sanitizer
        )
        
        # Test prompt with sensitive data
        prompt = "Process this: api_key=secret123"
        response = await service.generate(
            prompt=prompt,
            params={},
            context={"user_id": "123"}
        )
        
        # Verify sensitive data was redacted before reaching provider
        provider_calls = mock_llm_provider.complete.call_args_list
        assert len(provider_calls) == 1
        sent_prompt = provider_calls[0][0][0]
        assert "api_key=secret123" not in sent_prompt
        assert "[API_KEY]" in sent_prompt

    @pytest.mark.asyncio
    async def test_redaction_performance(self, sanitizer: PromptSanitizer):
        # Generate large text with some sensitive data
        large_text = "\n".join([
            f"Line {i}: api_key=secret{i} email{i}@test.com"
            for i in range(1000)
        ])
        
        # Measure sanitization time
        start_time = datetime.now()
        sanitized = await sanitizer.sanitize_prompt(
            large_text,
            {"user_id": "123"}
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        # Performance should be reasonable (adjust threshold as needed)
        assert duration < 1.0  # Should process 1000 lines in under 1 second
        assert len(sanitized) > 0
```

Test coverage ensures:
1. Pattern validation and initialization
2. Text redaction with various patterns
3. Priority-based processing
4. Sensitive data type detection
5. Length limits and edge cases
6. Integration with LLM service
7. Performance with large inputs

The tests follow our style guide and test naming conventions while maintaining high coverage of critical functionality.

### LLM Provider Abstraction

#### Provider Interface
```python
# app/domains/llm/providers/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class LLMProviderConfig(BaseModel):
    """Base configuration for LLM providers."""
    model: str
    api_key: str
    organization_id: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 2000

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMProviderConfig):
        self.config = config

    @abstractmethod
    async def complete(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate completion for given prompt."""
        pass

    @abstractmethod
    async def validate_key(self) -> bool:
        """Validate API key is active and has required permissions."""
        pass

    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        pass

    @abstractmethod
    def calculate_tokens(self, text: str) -> int:
        """Calculate number of tokens in text."""
        pass
```

#### OpenAI Implementation
```python
# app/domains/llm/providers/openai_provider.py

from typing import Dict, Any
import openai
from openai import AsyncOpenAI
from .base import BaseLLMProvider, LLMProviderConfig

class OpenAIConfig(LLMProviderConfig):
    """OpenAI-specific configuration."""
    api_version: Optional[str] = None
    azure_deployment: Optional[str] = None
    # Azure-specific settings if using Azure OpenAI
    azure_endpoint: Optional[str] = None

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config: OpenAIConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            organization=config.organization_id,
            timeout=config.timeout
        )

    async def complete(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=params.get("temperature", self.config.temperature),
                max_tokens=params.get("max_tokens", self.config.max_tokens)
            )
            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": response.model
            }
        except openai.APIError as e:
            logger.error(
                "OpenAI API error",
                error=str(e),
                prompt_length=len(prompt)
            )
            raise

    def calculate_tokens(self, text: str) -> int:
        """Calculate tokens using tiktoken."""
        import tiktoken
        encoding = tiktoken.encoding_for_model(self.config.model)
        return len(encoding.encode(text))
```

#### Anthropic Implementation
```python
# app/domains/llm/providers/anthropic_provider.py

from typing import Dict, Any
import anthropic
from .base import BaseLLMProvider, LLMProviderConfig

class AnthropicConfig(LLMProviderConfig):
    """Anthropic-specific configuration."""
    version: str = "2023-06-01"

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, config: AnthropicConfig):
        super().__init__(config)
        self.client = anthropic.AsyncAnthropic(
            api_key=config.api_key,
            timeout=config.timeout
        )

    async def complete(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = await self.client.messages.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=params.get("temperature", self.config.temperature),
                max_tokens=params.get("max_tokens", self.config.max_tokens)
            )
            return {
                "content": response.content[0].text,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "model": self.config.model
            }
        except anthropic.APIError as e:
            logger.error(
                "Anthropic API error",
                error=str(e),
                prompt_length=len(prompt)
            )
            raise
```

#### Google Gemini Implementation
```python
# app/domains/llm/providers/gemini_provider.py

from typing import Dict, Any
import anyio
import google.generativeai as genai
from .base import BaseLLMProvider, LLMProviderConfig

class GeminiConfig(LLMProviderConfig):
    """Google Gemini-specific configuration."""
    # Common Gemini models: "gemini-1.5-pro", "gemini-1.5-flash"
    safety_settings: Dict[str, str] | None = None

class GeminiProvider(BaseLLMProvider):
    def __init__(self, config: GeminiConfig):
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model)

    async def complete(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini SDK is sync; wrap in thread for async compatibility."""
        temperature = params.get("temperature", self.config.temperature)
        max_tokens = params.get("max_tokens", self.config.max_tokens)
        safety = params.get("safety_settings", getattr(self.config, "safety_settings", None))

        def _run_sync():
            return self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
                safety_settings=safety,
            )

        try:
            response = await anyio.to_thread.run_sync(_run_sync)
            text = response.text if hasattr(response, "text") else "".join(
                part.text for part in getattr(response, "candidates", []) if hasattr(part, "text")
            )
            usage = getattr(response, "usage_metadata", None)
            tokens_used = 0
            if usage:
                tokens_used = (getattr(usage, "prompt_token_count", 0) or 0) + (getattr(usage, "candidates_token_count", 0) or 0)
            return {
                "content": text,
                "tokens_used": tokens_used,
                "model": self.config.model,
            }
        except Exception as e:
            logger.error(
                "Gemini API error",
                error=str(e),
                prompt_length=len(prompt)
            )
            raise

    def calculate_tokens(self, text: str) -> int:
        # Placeholder: Gemini tokenization differs; use a simple heuristic if exact lib not available
        # Prefer provider-native token counting when available.
        return max(1, len(text.split()))
```

#### Provider Factory
```python
# app/domains/llm/providers/factory.py

from typing import Dict, Type
from .base import BaseLLMProvider, LLMProviderConfig
from .openai_provider import OpenAIProvider, OpenAIConfig
from .anthropic_provider import AnthropicProvider, AnthropicConfig
from .gemini_provider import GeminiProvider, GeminiConfig

class LLMProviderFactory:
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]) -> None:
        """Register a new provider implementation."""
        cls._providers[name] = provider_class

    @classmethod
    def create_provider(cls, provider_type: str, config: LLMProviderConfig) -> BaseLLMProvider:
        """Create provider instance based on type."""
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")

        provider_class = cls._providers[provider_type]
        return provider_class(config)
```

#### Integration Example
```python
# app/domains/llm/service.py

from .providers.factory import LLMProviderFactory
from .providers.base import LLMProviderConfig

class LLMService:
    def __init__(
        self,
        provider_type: str,
        config: LLMProviderConfig,
        sanitizer: PromptSanitizer = Depends(get_prompt_sanitizer)
    ):
        self.provider = LLMProviderFactory.create_provider(provider_type, config)
        self.sanitizer = sanitizer

    async def generate(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        # Sanitize and validate prompt
        sanitized_prompt = await self.sanitizer.sanitize_prompt(prompt)
        
        # Generate response using configured provider
        return await self.provider.complete(sanitized_prompt, params)
```

#### Configuration Example
```yaml
# config/llm.yml

default_provider: openai
providers:
  openai:
    model: gpt-4
    timeout: 30
    max_retries: 3
    temperature: 0.7
    max_tokens: 2000
    # Loaded from environment variables
    api_key: ${OPENAI_API_KEY}
    organization_id: ${OPENAI_ORG_ID}

  anthropic:
    model: claude-2
    timeout: 30
    max_retries: 3
    temperature: 0.7
    max_tokens: 2000
    version: "2023-06-01"
    # Loaded from environment variables
    api_key: ${ANTHROPIC_API_KEY}

  # Example of Azure OpenAI configuration
  azure_openai:
    model: gpt-4
    api_version: "2023-05-15"
    azure_deployment: "my-deployment"
    azure_endpoint: "https://my-instance.openai.azure.com"
    api_key: ${AZURE_OPENAI_API_KEY}

  # Google Gemini configuration
  gemini:
    model: gemini-1.5-pro
    temperature: 0.7
    max_tokens: 2000
    api_key: ${GOOGLE_GEMINI_API_KEY}
    safety_settings:
      HATE_SPEECH: BLOCK
      HARASSMENT: BLOCK
      SEXUAL_CONTENT: BLOCK
      DANGEROUS_CONTENT: BLOCK
```

This design provides:
1. **Provider Abstraction**: Common interface for all LLM providers
2. **Easy Extension**: New providers can be added by implementing BaseLLMProvider
3. **Configuration Flexibility**: Provider-specific settings via Pydantic models
4. **Runtime Selection**: Switch providers through configuration
5. **Error Handling**: Consistent error handling across providers
6. **Token Management**: Provider-specific token calculation
7. **Async Support**: All operations are async-first

### Data Models

#### New Database Schema
```sql
-- migrations/XXXXXX_add_llm_tables.sql

-- Track LLM interactions and usage
CREATE TABLE llm_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID REFERENCES teams(id),
    user_id UUID REFERENCES users(id),
    request_type VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    model VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    context JSONB,
    metadata JSONB
);

-- Store team-specific LLM settings
CREATE TABLE team_llm_settings (
    team_id UUID PRIMARY KEY REFERENCES teams(id),
    token_quota INTEGER NOT NULL DEFAULT 100000,
    allowed_models TEXT[] NOT NULL DEFAULT '{"gpt-4"}',
    rate_limit_override INTEGER,
    custom_parameters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_llm_interactions_team_id ON llm_interactions(team_id);
CREATE INDEX idx_llm_interactions_created_at ON llm_interactions(created_at);
```

## Implementation Recommendations

### Recommended Approach

#### Selection Rationale
Based on our scoring analysis and technical requirements, we recommend implementing the API Gateway Integration approach for the following reasons:

1. **Architecture Alignment**
   - Seamlessly integrates with our modular monolith pattern
   - Leverages existing FastAPI infrastructure
   - Maintains consistent security model

2. **Control and Flexibility**
   - Full control over request/response pipeline
   - Custom caching and rate limiting
   - Team-specific configuration management

3. **Security and Compliance**
   - Centralized API key management
   - Consistent audit logging
   - Granular access control

#### Risk Mitigation

1. **Performance Risks**
   ```python
   # app/core/middleware/circuit_breaker.py
   
   from fastapi import HTTPException
   from typing import Optional
   from datetime import datetime, timedelta
   
   class CircuitBreaker:
       def __init__(self):
           self.failure_count = 0
           self.last_failure = None
           self.state = 'closed'
           self.threshold = 5
           self.reset_timeout = timedelta(minutes=5)
       
       async def call(self, func, *args, **kwargs):
           if self.state == 'open':
               if datetime.now() - self.last_failure >= self.reset_timeout:
                   self.state = 'half-open'
               else:
                   raise HTTPException(status_code=503, detail="Service temporarily unavailable")
           
           try:
               result = await func(*args, **kwargs)
               if self.state == 'half-open':
                   self.state = 'closed'
                   self.failure_count = 0
               return result
           except Exception as e:
               self.handle_failure()
               raise e
   ```

2. **Token Management**
   ```python
   # app/domains/llm/token_manager.py
   
   from datetime import datetime
   from typing import Dict
   
   class TokenQuotaManager:
       def __init__(self, redis_client):
           self.redis = redis_client
       
       async def check_quota(self, team_id: str, tokens: int) -> bool:
           key = f"llm:quota:{team_id}:{datetime.now().month}"
           current = await self.redis.incrby(key, tokens)
           quota = await self.get_team_quota(team_id)
           return current <= quota
       
       async def get_usage_stats(self, team_id: str) -> Dict:
           return {
               'current': await self.get_current_usage(team_id),
               'quota': await self.get_team_quota(team_id),
               'reset_date': self.get_next_reset_date()
           }
   ```

3. **Error Handling**
   ```python
   # app/domains/llm/error_handler.py
   
   from fastapi import HTTPException
   from typing import Dict, Any
   
   class LLMErrorHandler:
       ERROR_MAPPING = {
           'token_quota_exceeded': (402, 'Token quota exceeded'),
           'rate_limit_exceeded': (429, 'Rate limit exceeded'),
           'model_not_allowed': (403, 'Model not allowed for team'),
           'invalid_request': (400, 'Invalid request format')
       }
       
       def handle_error(self, error_type: str, context: Dict[str, Any]) -> None:
           status_code, message = self.ERROR_MAPPING.get(
               error_type, (500, 'Internal server error')
           )
           raise HTTPException(status_code=status_code, detail={
               'message': message,
               'context': context
           })
   ```

#### Success Criteria

1. **Performance Metrics**
   - API response time < 500ms (p95)
   - Cache hit rate > 40%
   - Error rate < 0.1%

2. **Security Goals**
   - 100% key rotation compliance
   - Zero exposed credentials
   - Complete audit trail

3. **Business Metrics**
   - Token utilization efficiency > 90%
   - Feature adoption rate > 60%
   - User satisfaction score > 4.5/5

### Implementation Steps

#### Phase 1: Initial Setup (Week 1)

##### Required Code Style Setup

1. **Update ESLint Configuration**
   ```json
   // .eslintrc.json additions
   {
     "rules": {
       "@typescript-eslint/no-explicit-any": "error",
       "@typescript-eslint/naming-convention": [
         "error",
         {
           "selector": "interface",
           "format": ["PascalCase"],
           "prefix": ["I"]
         }
       ]
     }
   }
   ```

2. **Update Prettier Configuration**
   ```json
   // .prettierrc additions
   {
     "printWidth": 88,
     "tabWidth": 2,
     "semi": false,
     "singleQuote": true
   }
   ```

3. **Configure Python Linting**
   ```toml
   # pyproject.toml updates
   [tool.black]
   line-length = 88
   target-version = ['py311']
   include = '\.pyi?$'

   [tool.isort]
   profile = "black"
   multi_line_output = 3
   include_trailing_comma = true
   force_grid_wrap = 0
   use_parentheses = true
   ensure_newline_before_comments = true
   line_length = 88

   [tool.mypy]
   python_version = "3.11"
   disallow_untyped_defs = true
   disallow_any_unimported = true
   no_implicit_optional = true
   check_untyped_defs = true
   warn_return_any = true
   warn_unused_ignores = true
   show_error_codes = true
   ```

##### Initial Project Setup

1. **Environment Configuration**
   ```bash
   # Setup script: setup_llm_integration.sh
   #!/bin/bash
   
   # Create required directories
   mkdir -p app/domains/llm
   mkdir -p app/core/monitoring/llm
   
   # Copy configuration templates
   cp config/templates/llm.env .env.llm
   
   # Initialize Redis for caching
   docker-compose up -d redis
   
   # Create database migrations
   alembic revision --autogenerate -m "add_llm_tables"
   ```

2. **Core Dependencies**
   ```toml
   # pyproject.toml additions
   [tool.poetry.dependencies]
   openai = "^1.3.0"
   anthropic = "^0.5.0"
   redis = "^5.0.1"
   prometheus-client = "^0.17.1"
   cryptography = "^41.0.0"
   ```

#### Phase 2: Core Integration (Weeks 2-3)

1. **Service Layer Implementation**

   First, define the core interfaces:
   ```python
   # app/domains/llm/interfaces.py
   from typing import Protocol, Dict, Any, Optional
   from datetime import datetime
   from pydantic import BaseModel

   class ILLMResponse(BaseModel):
       content: str
       tokens_used: int
       model: str
       created_at: datetime
       metadata: Dict[str, Any]

   class ILLMProvider(Protocol):
       async def complete(self, prompt: str, params: Dict[str, Any]) -> ILLMResponse:
           ...

       async def validate_key(self, key: str) -> bool:
           ...

       async def get_model_info(self) -> Dict[str, Any]:
           ...

   class ILLMCache(Protocol):
       async def get(self, key: str) -> Optional[ILLMResponse]:
           ...

       async def set(self, key: str, value: ILLMResponse, ttl: int) -> None:
           ...

       async def invalidate(self, pattern: str) -> int:
           ...
   ```

   Then implement the service layer:
   ```python
   # app/domains/llm/service.py
   from typing import Dict, Any, Optional
   from datetime import datetime
   import structlog
   from fastapi import Depends, BackgroundTasks

   from app.core.security import get_current_user
   from app.core.metrics import get_metrics
   from .interfaces import ILLMProvider, ILLMCache, ILLMResponse
   from .token_manager import TokenQuotaManager
   from .error_handler import LLMErrorHandler

   logger = structlog.get_logger(__name__)

   class LLMService:
       def __init__(
           self,
           provider: ILLMProvider,
           cache: ILLMCache,
           token_manager: TokenQuotaManager,
           error_handler: LLMErrorHandler,
           background_tasks: BackgroundTasks,
           metrics = Depends(get_metrics),
           current_user = Depends(get_current_user)
       ):
           self.provider = provider
           self.cache = cache
           self.token_manager = token_manager
           self.error_handler = error_handler
           self.background_tasks = background_tasks
           self.metrics = metrics
           self.current_user = current_user

       async def generate(
           self,
           prompt: str,
           params: Dict[str, Any],
           cache_ttl: Optional[int] = 3600
       ) -> ILLMResponse:
           # Check permissions and quotas
           if not await self.token_manager.check_quota(
               self.current_user.team_id,
               estimated_tokens=len(prompt.split())
           ):
               self.error_handler.handle_error(
                   'token_quota_exceeded',
                   {'team_id': self.current_user.team_id}
               )

           # Try cache first
           cache_key = self._generate_cache_key(prompt, params)
           if cache_ttl and (cached := await self.cache.get(cache_key)):
               self.metrics.increment('llm_cache_hits')
               return cached

           # Generate new response
           try:
               with self.metrics.timer('llm_request_duration'):
                   response = await self.provider.complete(prompt, params)

               # Cache if needed
               if cache_ttl:
                   await self.cache.set(cache_key, response, cache_ttl)

               # Schedule usage tracking
               self.background_tasks.add_task(
                   self._track_usage,
                   response.tokens_used,
                   response.model
               )

               return response

           except Exception as e:
               logger.error(
                   "LLM request failed",
                   error=str(e),
                   user_id=self.current_user.id,
                   team_id=self.current_user.team_id
               )
               raise

       def _generate_cache_key(self, prompt: str, params: Dict[str, Any]) -> str:
           normalized_params = {
               k: v for k, v in sorted(params.items())
               if k not in {'temperature', 'top_p'}
           }
           content = f"{prompt}:{normalized_params}"
           return f"llm:cache:{sha256(content.encode()).hexdigest()}"

       async def _track_usage(
           self,
           tokens_used: int,
           model: str
       ) -> None:
           self.metrics.increment('llm_tokens_total', tokens_used)
           self.metrics.increment(
               'llm_requests_total',
               tags={'model': model}
           )
   
   from typing import Dict, Any
   from .providers import LLMProvider
   from .cache import LLMCache
   from .token_manager import TokenQuotaManager
   
   class LLMService:
       def __init__(self, provider: LLMProvider, cache: LLMCache,
                    token_manager: TokenQuotaManager):
           self.provider = provider
           self.cache = cache
           self.token_manager = token_manager
       
       async def generate(self, prompt: str, params: Dict[str, Any]):
           cache_key = self.cache.generate_key(prompt, params)
           if cached := await self.cache.get(cache_key):
               return cached
           
           response = await self.provider.complete(prompt, params)
           await self.cache.set(cache_key, response)
           return response
   ```

2. **API Endpoint Implementation**
   ```python
   # app/api/v1/endpoints/llm.py
   
   from fastapi import APIRouter, Depends, BackgroundTasks
   from ...domains.llm import LLMService, LLMAuthorizationError
   
   router = APIRouter(prefix="/llm", tags=["llm"])
   
   @router.post("/generate")
   async def generate_text(request: GenerateRequest,
                          service: LLMService = Depends(get_llm_service),
                          background_tasks: BackgroundTasks):
       try:
           response = await service.generate(
               request.prompt,
               request.parameters
           )
           background_tasks.add_task(log_llm_usage, request, response)
           return response
       except LLMAuthorizationError as e:
           raise HTTPException(status_code=403, detail=str(e))
   ```

#### Phase 3: Testing and Validation (Week 4)

1. **Unit Tests**
   ```python
   # tests/domains/llm/test_service.py
   
   import pytest
   from unittest.mock import Mock, AsyncMock
   from app.domains.llm import LLMService
   
   @pytest.mark.asyncio
   async def test_llm_service_caching():
       mock_provider = AsyncMock()
       mock_cache = AsyncMock()
       mock_token_manager = AsyncMock()
       
       service = LLMService(mock_provider, mock_cache, mock_token_manager)
       await service.generate("test prompt", {})
       
       mock_cache.get.assert_called_once()
       mock_provider.complete.assert_called_once()
   ```

2. **Integration Tests**
   ```python
   # tests/api/test_llm_integration.py
   
   from fastapi.testclient import TestClient
   from app.main import app
   
   def test_llm_generate_endpoint():
       client = TestClient(app)
       response = client.post("/api/v1/llm/generate", json={
           "prompt": "Test prompt",
           "parameters": {"temperature": 0.7}
       })
       assert response.status_code == 200
       assert "content" in response.json()
   ```

#### Phase 4: Production Deployment (Week 5)

1. **Migration Strategy**
   ```sql
   -- migrations/deploy_llm_integration.sql
   
   BEGIN;
   
   -- Apply schema changes
   \i migrations/XXXXXX_add_llm_tables.sql
   
   -- Set up initial team quotas
   INSERT INTO team_llm_settings (team_id, token_quota)
   SELECT id, 100000 FROM teams;
   
   COMMIT;
   ```

2. **Monitoring Setup**
   ```yaml
   # monitoring/prometheus/llm_rules.yml
   
   groups:
     - name: llm_alerts
       rules:
         - alert: LLMHighLatency
           expr: rate(llm_request_duration_seconds_sum[5m]) / rate(llm_request_duration_seconds_count[5m]) > 0.5
           labels:
             severity: warning
   ```

### Testing Strategy

#### Unit Testing Approach
```python
# tests/conftest.py

import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_llm_provider():
    provider = AsyncMock()
    provider.complete.return_value = {
        "content": "Test response",
        "tokens_used": 10
    }
    return provider

@pytest.fixture
def mock_token_manager():
    manager = AsyncMock()
    manager.check_quota.return_value = True
    return manager
```

#### Integration Testing Plan
```python
# tests/integration/test_llm_flow.py

import pytest
from app.domains.llm import LLMService

@pytest.mark.integration
async def test_full_llm_flow():
    # Test complete flow from request to response
    service = LLMService()
    response = await service.generate(
        prompt="Test integration flow",
        params={"temperature": 0.7}
    )
    
    # Verify response format
    assert "content" in response
    assert "usage" in response
    
    # Verify metrics
    metrics = await service.get_metrics()
    assert metrics["requests_total"] > 0
    assert metrics["tokens_used"] > 0
```

#### Performance Test Scenarios
```python
# tests/performance/test_llm_performance.py

import asyncio
import pytest
from app.domains.llm import LLMService

@pytest.mark.performance
async def test_concurrent_requests():
    service = LLMService()
    tasks = [
        service.generate(f"Test prompt {i}", {})
        for i in range(50)
    ]
    
    start_time = time.time()
    responses = await asyncio.gather(*tasks)
    duration = time.time() - start_time
    
    # Verify performance meets requirements
    assert duration < 25  # 50 requests in under 25 seconds
    assert all(r["content"] for r in responses)
```

#### Security Test Cases
```python
# tests/security/test_llm_security.py

import pytest
from app.domains.llm import LLMService, SecurityError

@pytest.mark.security
class TestLLMSecurity:
    async def test_token_quota_enforcement(self):
        service = LLMService()
        with pytest.raises(SecurityError):
            await service.generate_batch(
                ["prompt"] * 1000,  # Exceed quota
                {}
            )
    
    async def test_key_rotation(self):
        service = LLMService()
        old_key = await service.get_current_key()
        await service.rotate_key()
        new_key = await service.get_current_key()
        
        assert old_key != new_key
        assert await service.validate_key(new_key)
```

## Integration with Existing Architecture

### Architectural Impact

#### Component Integration
```mermaid
graph TD
    subgraph "Frontend"
        UI[UI Components]
        UIState[State Management]
    end

    subgraph "API Layer"
        API[FastAPI Services]
        Cache[Redis Cache]
        Auth[Auth Middleware]
    end

    subgraph "LLM Integration"
        LLMService[LLM Service]
        TokenMgr[Token Manager]
        PromptBuilder[Prompt Builder]
        LLMProvider[Provider Factory]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL)]
        Migration[Migration Service]
    end

    UI --> API
    API --> LLMService
    LLMService --> LLMProvider
    LLMService --> TokenMgr
    LLMService --> PromptBuilder
    TokenMgr --> Cache
    API --> DB
    LLMService --> DB
```

#### Required Changes

1. **Database Schema Updates**
   ```sql
   -- migrations/XXXXXX_add_llm_related_columns.sql
   
   -- Add LLM-related fields to existing tables
   ALTER TABLE epics ADD COLUMN generated_title BOOLEAN DEFAULT FALSE;
   ALTER TABLE epics ADD COLUMN llm_generation_metadata JSONB;
   
   -- Add audit triggers
   CREATE TRIGGER epic_llm_audit_trigger
       BEFORE UPDATE ON epics
       FOR EACH ROW
       WHEN (OLD.generated_title IS DISTINCT FROM NEW.generated_title)
       EXECUTE FUNCTION audit_epic_llm_changes();
   ```

2. **API Endpoint Modifications**
   ```python
   # app/api/v1/endpoints/epics.py
   
   from fastapi import APIRouter, Depends, BackgroundTasks
   from app.domains.llm import LLMService
   from app.domains.epics import EpicTitleGenerator
   
   router = APIRouter(prefix="/epics", tags=["epics"])
   
   @router.post("/{epic_id}/generate-title")
   async def generate_epic_title(
       epic_id: str,
       background_tasks: BackgroundTasks,
       llm_service: LLMService = Depends(get_llm_service)
   ):
       epic = await get_epic(epic_id)
       generator = EpicTitleGenerator(llm_service)
       
       title = await generator.generate_title(
           TitleGenerationRequest(
               epic_description=epic.description,
               category=epic.category
           )
       )
       
       background_tasks.add_task(update_epic_title, epic_id, title)
       return {"title": title}
   ```

3. **Frontend Integration**
   ```typescript
   // src/features/epics/hooks/useLLMGeneration.ts
   
   import { useMutation } from '@tanstack/react-query'
   import { generateEpicTitle } from '../api'
   
   export const useLLMGeneration = (epicId: string) => {
     const mutation = useMutation({
       mutationFn: () => generateEpicTitle(epicId),
       onSuccess: (data) => {
         // Update local state
         queryClient.setQueryData(
           ['epics', epicId],
           (old: Epic) => ({
             ...old,
             title: data.title,
             generated_title: true
           })
         )
       }
     })
     
     return mutation
   }
   ```

### Migration Strategy

#### Phase 1: Infrastructure Setup

1. **Database Migration**
   ```bash
   # migration_scripts/01_setup_llm.sh
   
   # Apply schema changes
   psql -f migrations/XXXXXX_add_llm_tables.sql
   
   # Create indexes
   psql -f migrations/XXXXXX_add_llm_indexes.sql
   
   # Initialize settings
   psql -f migrations/XXXXXX_init_llm_settings.sql
   ```

2. **Cache Configuration**
   ```yaml
   # config/redis.yml
   
   llm_cache:
     key_prefix: "llm:"
     default_ttl: 3600
     max_memory: "512mb"
     eviction_policy: "volatile-lru"
   ```

#### Phase 2: Feature Rollout

1. **Feature Flag Configuration**
   ```yaml
   # config/feature_flags.yml
   
   llm_integration:
     enabled: true
     features:
       epic_title_generation:
         enabled: false
         rollout_percentage: 0
       prompt_suggestions:
         enabled: false
         rollout_percentage: 0
   ```

2. **Gradual Rollout Plan**
   ```python
   # app/core/feature_flags.py
   
   from typing import Dict
   
   class LLMFeatureManager:
       def __init__(self, redis_client):
           self.redis = redis_client
           
       async def should_enable_feature(
           self,
           feature_name: str,
           team_id: str
       ) -> bool:
           if not await self.is_feature_enabled(feature_name):
               return False
               
           rollout = await self.get_rollout_percentage(feature_name)
           return self.is_team_in_rollout(team_id, rollout)
           
       def is_team_in_rollout(self, team_id: str, percentage: int) -> bool:
           if percentage >= 100:
               return True
               
           team_hash = hash(team_id) % 100
           return team_hash < percentage
   ```

#### Phase 3: Monitoring and Validation

1. **Metric Collection**
   ```python
   # app/core/monitoring/llm_metrics.py
   
   from prometheus_client import Counter, Histogram, Gauge
   
   class LLMMetrics:
       def __init__(self):
           # Usage metrics
           self.requests_total = Counter(
               'llm_requests_total',
               'Total LLM requests',
               ['feature', 'status']
           )
           self.tokens_used = Counter(
               'llm_tokens_total',
               'Total tokens used',
               ['feature']
           )
           
           # Performance metrics
           self.request_duration = Histogram(
               'llm_request_duration_seconds',
               'Request duration in seconds',
               ['feature']
           )
           
           # Cache metrics
           self.cache_hit_ratio = Gauge(
               'llm_cache_hit_ratio',
               'Cache hit ratio'
           )
   ```

2. **Health Checks**
   ```python
   # app/core/health/llm_checks.py
   
   from typing import Dict, Any
   
   class LLMHealthCheck:
       async def check_health(self) -> Dict[str, Any]:
           return {
               "provider_status": await self.check_provider(),
               "cache_status": await self.check_cache(),
               "token_quota": await self.check_quota(),
               "latency": await self.check_latency()
           }
           
       async def check_provider(self) -> Dict[str, str]:
           try:
               await self.provider.validate_key()
               return {"status": "healthy"}
           except Exception as e:
               return {
                   "status": "unhealthy",
                   "error": str(e)
               }
   ```

### Monitoring and Maintenance

#### Monitoring Dashboard

```yaml
# monitoring/grafana/llm_dashboard.yml

title: LLM Integration Metrics
panels:
  - title: Request Rate
    type: graph
    targets:
      - expr: sum(rate(llm_requests_total[5m])) by (feature)
        legendFormat: "{{feature}}"
    
  - title: Error Rate
    type: graph
    targets:
      - expr: |
          sum(rate(llm_requests_total{status="error"}[5m])) /
          sum(rate(llm_requests_total[5m]))
        legendFormat: "Error %"
    
  - title: Token Usage
    type: graph
    targets:
      - expr: sum(increase(llm_tokens_total[24h])) by (feature)
        legendFormat: "{{feature}}"
    
  - title: Response Time
    type: graph
    targets:
      - expr: histogram_quantile(0.95,
          sum(rate(llm_request_duration_seconds_bucket[5m])) by (le))
        legendFormat: "p95"
```

#### Alerting Rules

```yaml
# monitoring/prometheus/llm_alerts.yml

groups:
  - name: llm_alerts
    rules:
      - alert: LLMHighErrorRate
        expr: |
          sum(rate(llm_requests_total{status="error"}[5m])) /
          sum(rate(llm_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High LLM error rate
          
      - alert: LLMHighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(llm_request_duration_seconds_bucket[5m])) by (le)
          ) > 2
        for: 5m
        labels:
          severity: warning
          
      - alert: LLMTokenQuotaNearLimit
        expr: |
          sum(increase(llm_tokens_total[24h])) /
          avg_over_time(llm_token_quota[24h]) > 0.8
        labels:
          severity: warning
          
      - alert: LLMCacheEfficiency
        expr: llm_cache_hit_ratio < 0.3
        for: 30m
        labels:
          severity: warning
```

#### Maintenance Tasks

1. **Token Usage Optimization**
   ```python
   # app/tasks/llm_maintenance.py
   
   from app.core.celery import celery_app
   from app.domains.llm import TokenAnalyzer
   
   @celery_app.task
   async def analyze_token_usage():
       analyzer = TokenAnalyzer()
       report = await analyzer.generate_usage_report()
       
       if report.efficiency < 0.7:
           await analyzer.suggest_optimizations()
           
   @celery_app.task
   async def cleanup_expired_cache():
       await cache.cleanup_expired()
       await cache.optimize()
   ```

2. **Regular Health Checks**
   ```python
   # app/tasks/llm_health.py
   
   @celery_app.task
   async def check_llm_health():
       health_check = LLMHealthCheck()
       status = await health_check.check_health()
       
       if not status["provider_status"]["healthy"]:
           notify_admin(
               "LLM Provider Unhealthy",
               status["provider_status"]
           )
   ```

3. **Performance Optimization**
   ```python
   # app/tasks/llm_optimization.py
   
   @celery_app.task
   async def optimize_cache_settings():
       analyzer = CacheAnalyzer()
       stats = await analyzer.analyze()
       
       if stats.hit_ratio < 0.3:
           await analyzer.adjust_ttl()
           await analyzer.adjust_max_size()
   ```

## Service Provider Integration

### LLM Service Provider Setup

#### Provider Service Factory
```python
# app/domains/llm/providers/factory.py

from typing import Dict, Type, Optional
from pydantic import BaseSettings

class LLMServiceFactory:
    _providers: Dict[str, Type[BaseLLMProvider]] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[BaseLLMProvider]) -> None:
        cls._providers[name] = provider_class
    
    @classmethod
    def create(cls, settings: BaseSettings) -> BaseLLMProvider:
        provider_type = settings.llm_provider.lower()
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_type}")
            
        return cls._providers[provider_type](settings)

# Register built-in providers
LLMServiceFactory.register("openai", OpenAIProvider)
LLMServiceFactory.register("anthropic", AnthropicProvider)
LLMServiceFactory.register("gemini", GeminiProvider)
```

#### Provider Dependencies
```python
# app/domains/llm/dependencies.py

from fastapi import Depends
from app.core.config import get_settings
from .cache import LLMCache
from .token_manager import TokenQuotaManager
from .providers.factory import LLMServiceFactory

async def get_llm_provider(settings = Depends(get_settings)):
    return LLMServiceFactory.create(settings)

async def get_llm_cache(redis = Depends(get_redis)):
    return LLMCache(redis)

async def get_token_manager(redis = Depends(get_redis)):
    return TokenQuotaManager(redis)

async def get_llm_service(
    provider = Depends(get_llm_provider),
    cache = Depends(get_llm_cache),
    token_manager = Depends(get_token_manager)
):
    return LLMService(provider, cache, token_manager)
```

### Integration with Features

#### Epic Title Generation
```python
# app/domains/epics/title_generator.py

from typing import Optional
from pydantic import BaseModel
from app.domains.llm import LLMService

class TitleGenerationRequest(BaseModel):
    epic_description: str
    category: Optional[str] = None
    context: Optional[dict] = None

class EpicTitleGenerator:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        
    async def generate_title(self, request: TitleGenerationRequest) -> str:
        prompt = self._build_title_prompt(request)
        response = await self.llm.generate(
            prompt=prompt,
            params={
                "temperature": 0.7,
                "max_tokens": 60
            }
        )
        return self._process_title_response(response)
        
    def _build_title_prompt(self, request: TitleGenerationRequest) -> str:
        prompt_parts = [
            "Generate a concise epic title based on the following description.",
            "The title should be clear, specific, and follow a consistent format.",
            f"\nDescription: {request.epic_description}"
        ]
        
        if request.category:
            prompt_parts.append(f"Category: {request.category}")
            
        if request.context:
            context_str = "\n".join(f"{k}: {v}" for k, v in request.context.items())
            prompt_parts.append(f"Additional Context:\n{context_str}")
            
        return "\n".join(prompt_parts)
        
    def _process_title_response(self, response: dict) -> str:
        # Clean and validate the generated title
        title = response["content"].strip()
        if len(title) > 100:  # Maximum title length
            title = title[:97] + "..."
        return title
```

#### Prompt Builder Pattern

##### Base Prompt Builder
```python
# app/domains/llm/prompts/base.py

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel

class PromptContext(BaseModel):
    team_id: str
    user_id: str
    project_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class BasePromptBuilder(ABC):
    def __init__(self, context: PromptContext):
        self.context = context
        self._segments = []
        
    @abstractmethod
    def build(self) -> str:
        """Build the final prompt string."""
        pass
        
    def add_segment(self, segment: str) -> 'BasePromptBuilder':
        self._segments.append(segment.strip())
        return self
        
    def add_context(self, context: Dict[str, Any]) -> 'BasePromptBuilder':
        context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
        return self.add_segment(f"Context:\n{context_str}")
        
    def _join_segments(self, separator: str = "\n\n") -> str:
        return separator.join(filter(None, self._segments))
```

##### Specific Implementation
```python
# app/domains/llm/prompts/epic_title.py

from .base import BasePromptBuilder, PromptContext

class EpicTitlePromptBuilder(BasePromptBuilder):
    def __init__(self, context: PromptContext):
        super().__init__(context)
        self.add_segment(
            "You are a technical product manager helping to organize work items. "
            "Generate a concise and specific epic title based on the provided description."
        )
        
    def with_description(self, description: str) -> 'EpicTitlePromptBuilder':
        return self.add_segment(f"Description:\n{description}")
        
    def with_category(self, category: str) -> 'EpicTitlePromptBuilder':
        return self.add_segment(f"Category: {category}")
        
    def with_examples(self, examples: list) -> 'EpicTitlePromptBuilder':
        if not examples:
            return self
            
        examples_str = "\n".join(f"- {ex}" for ex in examples)
        return self.add_segment(f"Example Titles:\n{examples_str}")
        
    def build(self) -> str:
        self.add_segment(
            "The title should be:\n"
            "- Clear and specific\n"
            "- Under 100 characters\n"
            "- Start with a verb in present tense\n"
            "- Focus on the outcome or value"
        )
        return self._join_segments()
```

##### Usage Example
```python
# Example usage in epic title generator

from app.domains.llm.prompts import EpicTitlePromptBuilder, PromptContext

class EpicTitleGenerator:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        
    async def generate_title(self, request: TitleGenerationRequest) -> str:
        context = PromptContext(
            team_id=request.team_id,
            user_id=request.user_id,
            project_id=request.project_id
        )
        
        prompt = (
            EpicTitlePromptBuilder(context)
            .with_description(request.description)
            .with_category(request.category)
            .with_examples(request.examples)
            .build()
        )
        
        response = await self.llm.generate(
            prompt=prompt,
            params=self._get_generation_params()
        )
        return self._process_title_response(response)
        
    def _get_generation_params(self) -> dict:
        return {
            "temperature": 0.7,
            "max_tokens": 60,
            "stop_sequences": ["\n"]
        }
```

### Configuration Management

#### Environment Settings
```env
# .env.llm

# Provider Selection
LLM_PROVIDER=openai  # or anthropic, gemini

# OpenAI Settings
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_ORG_ID=org-...

# Anthropic Settings
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-2

# Google Settings
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro

# General Settings
LLM_CACHE_TTL=3600
LLM_RATE_LIMIT=100
LLM_TIMEOUT=30
```

#### Settings Management
```python
# app/core/config/llm.py

from pydantic import BaseSettings, Field
from typing import Optional

class LLMSettings(BaseSettings):
    # Provider Selection
    llm_provider: str = Field(..., env='LLM_PROVIDER')
    
    # OpenAI Settings
    openai_api_key: Optional[str] = Field(None, env='OPENAI_API_KEY')
    openai_model: Optional[str] = Field('gpt-4', env='OPENAI_MODEL')
    openai_org_id: Optional[str] = Field(None, env='OPENAI_ORG_ID')
    
    # Anthropic Settings
    anthropic_api_key: Optional[str] = Field(None, env='ANTHROPIC_API_KEY')
    anthropic_model: Optional[str] = Field('claude-2', env='ANTHROPIC_MODEL')
    
    # Google Settings
    google_api_key: Optional[str] = Field(None, env='GOOGLE_API_KEY')
    gemini_model: Optional[str] = Field('gemini-1.5-pro', env='GEMINI_MODEL')
    
    # General Settings
    cache_ttl: int = Field(3600, env='LLM_CACHE_TTL')
    rate_limit: int = Field(100, env='LLM_RATE_LIMIT')
    timeout: int = Field(30, env='LLM_TIMEOUT')
    
    class Config:
        env_file = '.env.llm'

def get_llm_settings() -> LLMSettings:
    return LLMSettings()
```

## Appendix

### Reference Documentation

- Providers and SDKs
  - OpenAI Python SDK: https://github.com/openai/openai-python
  - Anthropic Python SDK: https://github.com/anthropic-ai/anthropic-sdk-python
  - Google Generative AI (Gemini) SDK: https://github.com/google/generative-ai-python
  - tiktoken (tokenizer for OpenAI models): https://github.com/openai/tiktoken

- FastAPI and Middleware
  - FastAPI: https://fastapi.tiangolo.com/
  - BackgroundTasks: https://fastapi.tiangolo.com/advanced/background-tasks/
  - Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/

- Observability
  - Prometheus client (Python): https://github.com/prometheus/client_python
  - Grafana dashboards: https://grafana.com/docs/grafana/latest/dashboards/

- Caching and Rate Limiting
  - Redis: https://redis.io/docs/latest/
  - Redis Python (redis-py): https://github.com/redis/redis-py

- Security and Compliance
  - OWASP ASVS: https://owasp.org/ASVS/
  - OWASP Top 10: https://owasp.org/www-project-top-ten/
  - GDPR overview: https://gdpr.eu/
  - CCPA overview: https://oag.ca.gov/privacy/ccpa

- Testing
  - Pytest: https://docs.pytest.org/
  - HTTPX/TestClient: https://www.python-httpx.org/ and https://fastapi.tiangolo.com/advanced/testing/

### Security Compliance Checklist

Use this as a go/no-go checklist before enabling LLM features beyond internal testing:

- Secrets and Keys
  - [ ] API keys are stored in environment variables only and never in code
  - [ ] Key rotation policy is implemented and documented (90 days)
  - [ ] Least-privilege access to secrets manager and CI variables

- Data Privacy
  - [ ] Prompt sanitization and redaction are enabled and covered by tests
  - [ ] Raw prompts/responses are not persisted; only sanitized cache with TTL
  - [ ] User opt-out mechanism exists and is enforced per-team/user
  - [ ] DSR (data subject request) pathways do not require LLM data deletion beyond cache

- Transport and AuthZ
  - [ ] TLS 1.3 enforced for outbound provider requests
  - [ ] JWT validation in API layer; provider not reachable directly by clients
  - [ ] Role-based authorization for generate/train/manage operations

- Auditing and Monitoring
  - [ ] LLM request/response metadata is logged with privacy-safe fields
  - [ ] Metrics for error rate, latency, token usage, and cache ratio are live in Grafana
  - [ ] Alerts configured for high error rate, high latency, low cache ratio, quota near limit

- Abuse and Cost Controls
  - [ ] Per-user/team rate limits enforced server-side
  - [ ] Per-team monthly token quota enforced and visible to admins
  - [ ] Circuit breaker in place for provider outages

- SDLC and Testing
  - [ ] Unit/integration/security tests passing and meet coverage thresholds
  - [ ] Threat model updated for LLM attack surface (prompt injection, data exfiltration)
  - [ ] Runbooks for incident response and cache flush procedures

### Performance Benchmarks

Benchmark goals and methodology to validate the non-functional requirements.

- Test Environment
  - API: FastAPI app with uvicorn workers=4
  - Cache: Redis with 512MB, volatile-lru
  - Network: 100ms p95 egress latency assumed to providers

- Scenarios
  1. Single request latency
     - Input size: 300–500 tokens; Output size: up to 200 tokens
     - Goal: p95 < 500ms with warm cache; < 1.5s cold path including provider
  2. Concurrency test
     - 50 concurrent generate calls
     - Goal: Total duration < 25s; error rate < 0.1%
  3. Cache effectiveness
     - 60% repeated prompts by normalized params
     - Goal: Cache hit ratio > 40%; average latency improvement > 50%

- Methodology (example)
  ```bash
  # Locust or k6 recommended; example with k6 pseudo-config
  vus=50 duration=60s ramping
  payload: prompts.jsonl (mixed new/repeat)
  measurements: p50/p95 latency, error %, cache hit ratio (Prometheus scrape)
  ```

- Acceptance Criteria
  - p95 latency under SLA, error rate < 0.1%, cache hit ratio >= 40%

### Cost Analysis

Ballpark costs vary by provider and configuration; numbers here are illustrative—consult provider pricing pages for exact rates.

- Token Consumption Modeling
  - Monthly active teams: T
  - Avg requests per team per month: R
  - Avg prompt tokens: P; Avg completion tokens: C
  - Total tokens = T * R * (P + C)

- Provider Examples
  - OpenAI GPT-4 family
    - Assume $X per 1K input tokens, $Y per 1K output tokens
    - Monthly cost ≈ T * R * (P/1000 * X + C/1000 * Y)
  - Anthropic Claude family
    - Similar split-rate model; check latest pricing
  - Google Gemini
    - Model-dependent pricing; some flat tiers available

- Optimization Levers
  - Prompt compression and templates to reduce P
  - Higher cache TTL for idempotent operations
  - Prefer cheaper models for non-critical tasks; promote on cache hit
  - Quota tiers per workspace with admin-visible dashboards

- Example Scenario
  - T=20 teams, R=2,000/month, P=300, C=150
  - Total tokens = 20 * 2,000 * 450 = 18,000,000
  - With blended cost $0.005 per 1K tokens: ~ $90/month

- Governance
  - Budget alerts at 50%, 80%, 100%
  - Automatic throttling beyond 120% to protect spend
  - Monthly report with feature-level token attribution
