# SprintSense Coding Standards

## Purpose & Scope

This document establishes comprehensive coding standards for the SprintSense project to ensure:
- **Consistent code quality** across frontend (TypeScript/React) and backend (Python/FastAPI) components
- **Zero linting errors** in AI-generated code
- **Reduced iteration cycles** during development and PR reviews
- **Maintainable, secure, and performant** codebase

This document works in conjunction with [`claude_suggestions.md`](../../claude_suggestions.md) and serves as the authoritative reference for all AI code generation workflows.

---

## Shared Principles

### Naming Conventions

| Component | Convention | Example | ESLint/Linter Rule |
|-----------|------------|---------|-------------------|
| **Frontend Files** | PascalCase for components | `UserProfile.tsx` | N/A |
| **Frontend Variables/Functions** | camelCase | `getUserData()` | `@typescript-eslint/naming-convention` |
| **Backend Files** | snake_case | `user_profile.py` | N/A |
| **Backend Functions/Variables** | snake_case | `get_user_data()` | `N806` (flake8) |
| **Constants** | SCREAMING_SNAKE_CASE | `API_BASE_URL` | `@typescript-eslint/naming-convention`, `N806` |
| **Database Tables/Columns** | snake_case | `user_profiles.created_at` | N/A |

### Dependency Injection & Anti-Patterns

#### ✅ **DO: Use Proper Dependency Injection**

**Frontend (React):**
```tsx
// ✅ GOOD: Context + custom hooks
const useUserStore = () => {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUserStore must be used within UserProvider')
  }
  return context
}

// Usage in components
const UserProfile: React.FC = () => {
  const { user, updateUser } = useUserStore()
  // Component logic...
}
```

**Backend (FastAPI):**
```python
# ✅ GOOD: Dependency injection with FastAPI Depends
from fastapi import Depends
from app.core.database import get_db

async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> UserProfile:
    # Function logic...
    pass

@router.get("/users/{user_id}")
async def read_user(user_id: int, user_service = Depends(get_user_service)):
    return await user_service.get_user(user_id)
```

#### ❌ **AVOID: Anti-Patterns**

```tsx
// ❌ BAD: Global state variables
let globalUser = null  // Violates: no-global-assign

// ❌ BAD: Tight coupling
class UserComponent extends React.Component {  // Violates: prefer function components
  constructor(props) {
    super(props)
    this.apiClient = new ApiClient()  // Tight coupling
  }
}
```

```python
# ❌ BAD: Global variables and tight coupling
global_db_connection = None  # Violates: global-statement (flake8 W603)

def get_user_data():  # Missing type hints: mypy error
    return global_db_connection.query(...)  # Tight coupling
```

### Error Handling Strategy

#### Frontend Error Handling
```tsx
// ✅ GOOD: Typed error boundaries and error states
interface ApiError {
  message: string
  code: string
  details?: Record<string, unknown>
}

const useApiCall = <T>(apiCall: () => Promise<T>) => {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<ApiError | null>(null)
  const [loading, setLoading] = useState(false)
  
  const execute = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiCall()
      setData(result)
    } catch (err) {
      setError(err as ApiError)
    } finally {
      setLoading(false)
    }
  }, [apiCall])
  
  return { data, error, loading, execute }
}
```

#### Backend Error Handling
```python
# ✅ GOOD: Custom exceptions with proper types
from typing import Dict, Any
from fastapi import HTTPException, status

class SprintSenseException(Exception):
    """Base exception for SprintSense application."""
    
    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class UserNotFoundError(SprintSenseException):
    """Raised when user is not found."""
    pass

# In route handlers
@router.get("/users/{user_id}")
async def get_user(user_id: int) -> UserResponse:
    try:
        user = await user_service.get_user(user_id)
        return UserResponse.model_validate(user)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "details": e.details}
        )
```

### Testing Requirements

#### Minimum Coverage & Structure
- **Backend**: 80% test coverage (pytest-cov)
- **Frontend**: 70% test coverage (vitest)
- **Test file naming**: `test_*.py` (backend), `*.test.ts[x]` (frontend)

#### Testing Patterns
```python
# ✅ GOOD: Backend test structure
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_user_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/users/1")
    
    assert response.status_code == 200
    assert response.json()["id"] == 1
```

```tsx
// ✅ GOOD: Frontend test structure
import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { UserProfile } from './UserProfile'

describe('UserProfile', () => {
  it('should render user data when loaded', async () => {
    const mockUser = { id: 1, name: 'John Doe' }
    vi.mocked(useUserStore).mockReturnValue({
      user: mockUser,
      loading: false,
      error: null
    })
    
    render(<UserProfile />)
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })
  })
})
```

### Security Best Practices

#### SQL Injection Prevention
```python
# ✅ GOOD: Parameterized queries with SQLAlchemy
from sqlalchemy import text

async def get_users_by_status(db: AsyncSession, status: str) -> List[User]:
    query = text("SELECT * FROM users WHERE status = :status")
    result = await db.execute(query, {"status": status})
    return result.fetchall()
```

#### Secrets Management
```python
# ✅ GOOD: Environment-based configuration
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Frontend TypeScript/React Standards

### File Naming & Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components
│   └── feature/         # Feature-specific components
├── pages/              # Route-level components
├── hooks/              # Custom React hooks  
├── services/           # API clients and business logic
├── stores/             # State management
├── types/              # TypeScript type definitions
├── utils/              # Pure utility functions
└── __tests__/          # Test files
```

#### File Naming Rules
- **Components**: PascalCase (`UserProfile.tsx`)
- **Hooks**: camelCase starting with "use" (`useUserData.ts`)
- **Utilities**: camelCase (`formatDate.ts`)
- **Types**: camelCase with `.types.ts` suffix (`user.types.ts`)

### Strict TypeScript Rules

#### Type Safety (ESLint: `@typescript-eslint/no-explicit-any`)
```tsx
// ❌ AVOID: Using 'any'
const processData = (data: any) => {
  return data.someProperty  // No type safety
}

// ✅ GOOD: Proper typing
interface UserData {
  id: number
  name: string
  email: string
}

const processUserData = (data: UserData): string => {
  return data.name  // Type-safe access
}

// ✅ GOOD: Generic constraints for flexibility
interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}

const fetchData = async <T>(url: string): Promise<ApiResponse<T>> => {
  // Implementation...
}
```

#### Strict Null Checks
```tsx
// ✅ GOOD: Proper null handling
const UserCard: React.FC<{ user?: User }> = ({ user }) => {
  if (!user) {
    return <div>Loading...</div>
  }
  
  return (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  )
}
```

### React Component Patterns

#### Function Components Only (ESLint: `react/prefer-stateless-function`)
```tsx
// ❌ AVOID: Class components
class UserProfile extends React.Component {
  render() {
    return <div>User Profile</div>
  }
}

// ✅ GOOD: Function components with hooks
const UserProfile: React.FC = () => {
  const [user, setUser] = useState<User | null>(null)
  
  return <div>User Profile</div>
}
```

#### Hook Rules (ESLint: `react-hooks/rules-of-hooks`)
```tsx
// ✅ GOOD: Custom hook pattern
const useUserData = (userId: number) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true)
        const userData = await userService.getUser(userId)
        setUser(userData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }
    
    fetchUser()
  }, [userId])
  
  return { user, loading, error }
}
```

### Anti-Generic UI Patterns (from claude_suggestions.md)

#### ✅ **Creative UI Requirements**
```tsx
// ✅ GOOD: Custom color palette and animations
const theme = createTheme({
  palette: {
    primary: {
      main: '#6366f1',      // Custom indigo
      light: '#a5b4fc',
      dark: '#4338ca',
    },
    secondary: {
      main: '#f59e0b',      // Custom amber
      light: '#fcd34d',
      dark: '#d97706',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
          },
        },
      },
    },
  },
})

// ✅ GOOD: Micro-interactions
const AnimatedCard: React.FC = ({ children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -2, boxShadow: "0 8px 25px rgba(0,0,0,0.1)" }}
    >
      {children}
    </motion.div>
  )
}
```

#### ❌ **Forbidden Generic Patterns**
```tsx
// ❌ AVOID: Generic Bootstrap/MUI defaults
const GenericCard = () => (
  <Card>  {/* Default MUI styling */}
    <CardContent>
      <Typography variant="h5">Title</Typography>  {/* Generic layout */}
      <Typography variant="body2">Description</Typography>
    </CardContent>
  </Card>
)

// ❌ AVOID: Standard blue/white/gray schemes
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },  // Generic MUI blue
    secondary: { main: '#dc004e' }, // Generic MUI pink
  }
})
```

---

## Backend Python/FastAPI Standards

### Pydantic Models & Type Annotations

#### Strict Type Annotations (mypy: `disallow_untyped_defs`)
```python
# ✅ GOOD: Complete type annotations
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=0, le=150)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

# ✅ GOOD: Service layer with proper types
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreateRequest) -> UserResponse:
        db_user = User(**user_data.model_dump())
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return UserResponse.model_validate(db_user)
```

#### Router Organization & Dependency Injection
```python
# ✅ GOOD: Structured router with dependencies
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreateRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create a new user account."""
    try:
        return await user_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### Async Best Practices

#### Database Interactions
```python
# ✅ GOOD: Proper async/await with connection management
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_users(self) -> List[User]:
        query = select(User).where(User.is_active == True)
        result = await self.db.execute(query)
        return result.scalars().all()
```

#### Background Tasks
```python
# ✅ GOOD: Background task structure
from fastapi import BackgroundTasks
import structlog

logger = structlog.get_logger(__name__)

async def send_welcome_email(user_email: str, user_name: str) -> None:
    """Send welcome email to new user."""
    try:
        # Email sending logic here
        logger.info("Welcome email sent", user_email=user_email)
    except Exception as e:
        logger.error("Failed to send welcome email", user_email=user_email, error=str(e))

@router.post("/users/")
async def create_user(
    user_data: UserCreateRequest,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    user = await user_service.create_user(user_data)
    background_tasks.add_task(send_welcome_email, user.email, user.name)
    return user
```

### Formatting & Linting Rules

#### Black Formatting (Enforced)
- **Line length**: 88 characters
- **String quotes**: Double quotes preferred
- **Trailing commas**: In multi-line collections

#### isort Import Organization
```python
# ✅ GOOD: Import order (isort profile="black")
# 1. Standard library
import asyncio
from datetime import datetime
from typing import List, Optional

# 2. Third-party packages
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select

# 3. Local application imports
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
```

#### Common flake8 Rules to Avoid
- **E501**: Line too long (>88 chars) - Use Black formatter
- **F401**: Module imported but unused - Remove unused imports
- **F841**: Local variable assigned but never used - Remove or prefix with `_`
- **W503**: Line break before binary operator - Follow Black style

```python
# ❌ AVOID: Long lines (E501)
user_data = {"name": "Very Long Name Here", "email": "very.long.email.address@company.com", "department": "Engineering"}

# ✅ GOOD: Properly formatted
user_data = {
    "name": "Very Long Name Here",
    "email": "very.long.email.address@company.com", 
    "department": "Engineering"
}
```

---

## Linting & Formatting Integration

### Pre-commit Hooks Configuration

Your `.pre-commit-config.yaml` runs:
1. **Basic checks**: trailing whitespace, file endings, YAML syntax
2. **Python**: Black → isort → flake8 → mypy (in that order)
3. **Frontend**: ESLint + Prettier (via npm scripts)

### Local Development Scripts

#### Frontend Linting
```bash
# Check only
npm run lint                    # ESLint check
npm run format:check           # Prettier check

# Fix automatically  
npm run lint:fix               # ESLint auto-fix
npm run format                 # Prettier auto-format
```

#### Backend Linting
```bash
# Individual tools
poetry run black .             # Format code
poetry run isort .             # Sort imports  
poetry run flake8 app/         # Lint check
poetry run mypy app/           # Type check

# Combined check
poetry run pre-commit run --all-files
```

### CI Pipeline Integration

Your `.github/workflows/ci.yml` includes:
1. **Frontend**: `npm run lint` and `npm run format:check`
2. **Backend**: `poetry run flake8` and type checking
3. **Tests**: Both frontend and backend test suites
4. **Build verification**: Ensure deployable artifacts

### AI Agent Integration Workflow

#### For AI Code Generation:
1. **Generate code** following these standards
2. **Auto-format**: Run `npm run format` (frontend) or `poetry run black . && poetry run isort .` (backend)
3. **Lint check**: Run `npm run lint` (frontend) or `poetry run flake8` (backend) 
4. **Type check**: Run `npm run type-check` (frontend) or `poetry run mypy` (backend)
5. **Only commit** if all checks pass

---

## Patterns to Follow vs Anti-Patterns

### Quick Reference Tables

#### Frontend Patterns

| Pattern | ✅ Good | ❌ Avoid | ESLint Rule |
|---------|---------|----------|-------------|
| **Components** | Function components with hooks | Class components | `react/prefer-stateless-function` |
| **State** | useState, useContext, Zustand | Global variables, this.state | `no-global-assign` |
| **Types** | Strict interfaces, no `any` | Loose typing, `any` everywhere | `@typescript-eslint/no-explicit-any` |
| **Imports** | Named imports, tree-shaking | Default imports for utilities | `import/no-default-export` |
| **Event Handlers** | useCallback for optimization | Inline functions in JSX | `react-hooks/exhaustive-deps` |

#### Backend Patterns

| Pattern | ✅ Good | ❌ Avoid | Linter Rule |
|---------|---------|----------|-------------|
| **Functions** | Full type annotations | Missing types | mypy `disallow_untyped_defs` |
| **Imports** | Organized by isort | Random order | isort violations |
| **Line Length** | ≤88 characters | >88 characters | flake8 E501 |
| **Variables** | snake_case | camelCase | flake8 N806 |
| **Strings** | f-strings for formatting | % or .format() | flake8 F541 |

### AI Generation Checklist

Before accepting AI-generated code, verify:

- [ ] **Naming conventions** follow language standards
- [ ] **Type annotations** are complete and accurate
- [ ] **Import statements** are organized and necessary
- [ ] **Error handling** uses project patterns
- [ ] **Testing patterns** match project structure
- [ ] **No forbidden anti-patterns** from `claude_suggestions.md`
- [ ] **Creativity requirements** met (frontend UI components)
- [ ] **Security best practices** implemented
- [ ] **Linting passes** without warnings or errors
- [ ] **Formatting** matches project style (Black/Prettier)

---

## Code Sample Library

### Frontend Examples

#### ✅ Compliant Component Example
```tsx
import React, { useCallback, useState } from 'react'
import { 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  CircularProgress 
} from '@mui/material'
import { motion } from 'framer-motion'
import { User } from '../types/user.types'
import { useUserData } from '../hooks/useUserData'

interface UserCardProps {
  userId: number
  onSelect?: (user: User) => void
}

export const UserCard: React.FC<UserCardProps> = ({ 
  userId, 
  onSelect 
}) => {
  const { user, loading, error } = useUserData(userId)
  const [isHovered, setIsHovered] = useState(false)
  
  const handleSelect = useCallback(() => {
    if (user && onSelect) {
      onSelect(user)
    }
  }, [user, onSelect])
  
  if (loading) {
    return (
      <Card sx={{ minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
      </Card>
    )
  }
  
  if (error) {
    return (
      <Card sx={{ minHeight: 200, bgcolor: 'error.light' }}>
        <CardContent>
          <Typography color="error">
            Failed to load user: {error}
          </Typography>
        </CardContent>
      </Card>
    )
  }
  
  if (!user) {
    return null
  }
  
  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: '0 8px 25px rgba(99, 102, 241, 0.15)' }}
      transition={{ type: 'spring', stiffness: 300 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Card sx={{ 
        minHeight: 200,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom>
            {user.name}
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            {user.email}
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.7 }}>
            Joined {new Date(user.createdAt).toLocaleDateString()}
          </Typography>
          
          <Button
            variant="contained"
            sx={{
              mt: 2,
              bgcolor: 'rgba(255,255,255,0.2)',
              backdropFilter: 'blur(10px)',
              '&:hover': {
                bgcolor: 'rgba(255,255,255,0.3)',
              }
            }}
            onClick={handleSelect}
          >
            View Profile
          </Button>
        </CardContent>
        
        {isHovered && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{
              position: 'absolute',
              top: 10,
              right: 10,
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: '#4ade80'
            }}
          />
        )}
      </Card>
    </motion.div>
  )
}
```

#### ❌ Non-Compliant Example (Multiple Issues)
```tsx
// ❌ Multiple violations - DO NOT USE
import * as React from 'react'  // ❌ Should use named imports
import Card from '@mui/material/Card'  // ❌ Should import from index

interface Props {  // ❌ Generic interface name
  userId: any  // ❌ Using 'any' type
}

class UserCard extends React.Component<Props> {  // ❌ Class component
  state = {  // ❌ Untyped state
    user: null,
    loading: true
  }
  
  componentDidMount() {  // ❌ Lifecycle methods instead of hooks
    this.fetchUser()
  }
  
  fetchUser = async () => {  // ❌ Arrow function property
    const response = await fetch(`/users/${this.props.userId}`)
    const user = await response.json()  // ❌ No error handling
    this.setState({ user, loading: false })  // ❌ Direct state mutation
  }
  
  render() {
    return (
      <Card style={{ padding: 20 }}>  {/* ❌ Inline styles, generic design */}
        <h3>{this.state.user?.name}</h3>  {/* ❌ Plain HTML elements */}
        <p>{this.state.user?.email}</p>
      </Card>
    )
  }
}

export default UserCard  // ❌ Default export for component
```

### Backend Examples

#### ✅ Compliant API Handler Example
```python
"""User management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserCreateRequest, UserUpdateRequest
from app.services.user_service import UserService
from app.services.notification_service import NotificationService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Get user service instance."""
    return UserService(db)


def get_notification_service() -> NotificationService:
    """Get notification service instance.""" 
    return NotificationService()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> List[UserResponse]:
    """
    Retrieve a list of users.
    
    - **skip**: Number of users to skip (pagination)
    - **limit**: Maximum number of users to return
    - **active_only**: Filter for active users only
    """
    try:
        users = await user_service.get_users(
            skip=skip,
            limit=limit,
            active_only=active_only
        )
        
        logger.info(
            "Users retrieved successfully",
            user_count=len(users),
            requested_by=current_user.id
        )
        
        return [UserResponse.model_validate(user) for user in users]
    
    except Exception as e:
        logger.error(
            "Failed to retrieve users",
            error=str(e),
            requested_by=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    notification_service: NotificationService = Depends(get_notification_service),
) -> UserResponse:
    """
    Create a new user account.
    
    - **name**: User's full name
    - **email**: User's email address (must be unique)
    - **role**: User's role in the system
    """
    try:
        # Check if email already exists
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Create new user
        new_user = await user_service.create_user(user_data)
        
        # Schedule background notification
        background_tasks.add_task(
            notification_service.send_welcome_email,
            email=new_user.email,
            name=new_user.name
        )
        
        logger.info(
            "User created successfully",
            user_id=new_user.id,
            email=new_user.email,
            created_by=current_user.id
        )
        
        return UserResponse.model_validate(new_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to create user",
            error=str(e),
            email=user_data.email,
            created_by=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get user by ID."""
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse.model_validate(user)
```

#### ❌ Non-Compliant Example (Multiple Issues)
```python
# ❌ Multiple violations - DO NOT USE

import json  # ❌ Unused import (F401)
from fastapi import *  # ❌ Wildcard import (F403)

app = FastAPI()  # ❌ Global app instance

def get_user(user_id):  # ❌ Missing type annotations
    # ❌ No error handling, SQL injection risk
    query = f"SELECT * FROM users WHERE id = {user_id}"  
    return db.execute(query).fetchone()  # ❌ Global db reference

@app.get("/users/{user_id}")  # ❌ Using global app
def read_user(user_id):  # ❌ Missing type annotations and dependencies
    user = get_user(user_id)
    if user == None:  # ❌ Should use 'is None'
        return {"error": "User not found"}  # ❌ Inconsistent error format
    return user  # ❌ No response model validation

# ❌ Line too long - violates E501
very_long_variable_name_that_exceeds_the_maximum_line_length = "This line is way too long and should be broken up"
```

---

## Relation to AI Generation Guidelines  

This document works in conjunction with [`claude_suggestions.md`](../../claude_suggestions.md):

### **Quality Validation Integration**
The AI generation process should follow:
1. **Code Generation** → Follow patterns in this document
2. **Linting Check** → Pass all rules defined here  
3. **Creative Validation** → Meet creativity standards (frontend only)
4. **Architecture Review** → Align with system design
5. **Integration Testing** → Ensure compatibility

### **Creativity Requirements** (Frontend)
- **Anti-Generic Patterns**: Avoid Bootstrap defaults, standard color schemes
- **Brand Integration**: Custom themes, micro-interactions, asymmetrical layouts
- **Target Score**: Minimum 8/10 creativity score per `claude_suggestions.md`

### **Cross-Reference Rules**
- **Forbidden Generic Patterns**: Enforced through linting + creative review
- **Quality Standards**: Automated via CI pipeline
- **Anti-Patterns**: Explicitly defined in code sample sections above

---

## Quick Reference & Checklist

### Pre-Generation Checklist
- [ ] Read this document completely
- [ ] Review [`claude_suggestions.md`](../../claude_suggestions.md) creativity guidelines  
- [ ] Understand target feature requirements
- [ ] Check existing code patterns in the relevant module

### Post-Generation Validation
- [ ] **Syntax**: Code compiles/transpiles without errors
- [ ] **Linting**: ESLint (frontend) and flake8 (backend) pass
- [ ] **Formatting**: Prettier (frontend) and Black (backend) applied
- [ ] **Type Checking**: TypeScript and mypy pass
- [ ] **Testing**: Relevant test cases created and passing
- [ ] **Creativity**: Frontend meets uniqueness requirements
- [ ] **Security**: No hard-coded secrets, proper input validation
- [ ] **Performance**: No obvious performance anti-patterns

### Emergency Lint Fix Commands
```bash
# Frontend emergency fixes
cd frontend && npm run lint:fix && npm run format

# Backend emergency fixes  
cd backend && poetry run black . && poetry run isort . && poetry run flake8 app/
```

---

## Further Reading

### Configuration Files Reference
- **Frontend ESLint**: `frontend/.eslintrc.json` & `frontend/eslint.config.js`
- **Frontend Prettier**: `frontend/.prettierrc.json`
- **Backend Python**: `backend/pyproject.toml` (Black, isort, mypy config)
- **Backend Linting**: `backend/.flake8`
- **Pre-commit**: `backend/.pre-commit-config.yaml`

### External Documentation
- [TypeScript ESLint Rules](https://typescript-eslint.io/rules/)
- [React ESLint Plugin](https://github.com/jsx-eslint/eslint-plugin-react)
- [Python Black Code Style](https://black.readthedocs.io/en/stable/)
- [flake8 Error Codes](https://flake8.pycqa.org/en/latest/user/error-codes.html)
- [mypy Type Checking](https://mypy.readthedocs.io/en/stable/)
- [Pydantic Models](https://pydantic-docs.helpmanual.io/usage/models/)

---

*This document is maintained as part of the SprintSense development workflow and should be updated when linting rules or project patterns change.*
