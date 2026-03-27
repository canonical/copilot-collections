# Path Instruction Template Examples

This document provides complete, production-ready examples of path-specific instruction files across different domains and technology stacks.

---

## Example 1: Python Testing with Pytest

**File**: `.github/instructions/python-testing.md`

```markdown
---
applyTo:
  - "tests/**/*.py"
  - "**/*_test.py"
  - "**/test_*.py"
---

# Python Testing Standards (Pytest)

## Test Structure

### File Organization
- Test files mirror source structure: `src/utils/parser.py` → `tests/utils/test_parser.py`
- Use `test_*.py` or `*_test.py` naming convention
- Group related tests in classes using `Test` prefix: `class TestUserAuthentication`

### Test Function Naming
- Use descriptive names: `test_user_login_with_valid_credentials_succeeds`
- Pattern: `test_<what>_<condition>_<expected_outcome>`
- Avoid generic names like `test_1`, `test_case_a`

## Fixtures

### Scope Selection
- `function` (default): New instance per test
- `class`: Shared across test class
- `module`: Shared across file
- `session`: Shared across entire test run

### Fixture Location
- Conftest for shared fixtures: `tests/conftest.py`
- Local fixtures for test-specific setup
- Use fixture composition for complex setups

```python
@pytest.fixture
def user_data():
    return {"username": "testuser", "email": "test@example.com"}

@pytest.fixture
def authenticated_user(user_data, db_session):
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    return user
```

## Assertions

### Use pytest's assert
- Prefer `assert` over `self.assertEqual`
- Leverage pytest's introspection for detailed failure messages
- Use `pytest.raises` for exception testing

```python
# Good
assert user.is_active is True
assert len(results) == 5
assert "error" in response.json()

# Exception testing
with pytest.raises(ValueError, match="Invalid email"):
    create_user(email="invalid")
```

## Parametrization

### Use for Multiple Inputs
```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("123", "123"),
])
def test_uppercase_conversion(input, expected):
    assert to_uppercase(input) == expected
```

### Complex Parametrization
```python
@pytest.mark.parametrize("user_role,expected_status", [
    ("admin", 200),
    ("user", 200),
    ("guest", 403),
])
def test_endpoint_access_by_role(client, user_role, expected_status):
    response = client.get(f"/api/data", headers={"role": user_role})
    assert response.status_code == expected_status
```

## Mocking

### Use pytest-mock Plugin
- Prefer `mocker` fixture over `unittest.mock`
- Mock at the point of use, not definition
- Reset mocks between tests (automatic with pytest-mock)

```python
def test_external_api_call(mocker):
    mock_response = {"status": "success"}
    mocker.patch("app.services.external_api.call", return_value=mock_response)
    
    result = process_external_data()
    assert result["status"] == "success"
```

## Markers

### Standard Markers
- `@pytest.mark.slow` - Tests taking > 1 second
- `@pytest.mark.integration` - Tests requiring external services
- `@pytest.mark.unit` - Pure unit tests
- `@pytest.mark.smoke` - Critical path tests

### Custom Markers (define in pytest.ini)
```python
@pytest.mark.requires_database
def test_database_query(db_session):
    # Test implementation
    pass
```

## Test Data

### Use Factories for Complex Objects
```python
# tests/factories.py
class UserFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
        }
        return User(**{**defaults, **kwargs})
```

### Avoid Hardcoded Values
```python
# Bad
def test_user_creation():
    user = create_user("john_doe", "john@example.com")

# Good
def test_user_creation(user_data):
    user = create_user(**user_data)
```

## Async Testing

### Use pytest-asyncio
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result == expected_value
```

## Coverage

- Aim for 80%+ coverage on business logic
- 100% coverage on critical paths (authentication, payments)
- Use `# pragma: no cover` sparingly, with justification
```

---

## Example 2: API Documentation (Markdown)

**File**: `.github/instructions/api-documentation.md`

```markdown
---
applyTo:
  - "docs/api/**/*.md"
  - "api-docs/**/*.md"
---

# API Documentation Standards

## Document Structure

### Required Sections
Every API endpoint document must include:

1. **Overview** - Brief description of the endpoint's purpose
2. **Authentication** - Required auth method and permissions
3. **Request** - HTTP method, URL pattern, headers, parameters
4. **Response** - Status codes, response body structure, examples
5. **Errors** - Possible error responses with codes and messages
6. **Examples** - At least one complete request/response example

## Endpoint Documentation Template

```markdown
# GET /api/v1/users/{id}

## Overview
Retrieves a single user by their unique identifier.

## Authentication
- **Required**: Yes
- **Type**: Bearer token
- **Permissions**: `users:read` or `users:admin`

## Request

### URL Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | User's unique identifier (UUID) |

### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| include | string | No | - | Comma-separated related resources: `profile,settings` |

### Headers
- `Authorization: Bearer <token>` (required)
- `Accept: application/json` (required)

## Response

### Success (200 OK)
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### Field Descriptions
| Field | Type | Description |
|-------|------|-------------|
| id | string | User's unique identifier (UUID v4) |
| username | string | Unique username (3-30 characters) |
| email | string | User's email address |
| created_at | string | ISO 8601 timestamp of account creation |
| is_active | boolean | Account status |

## Errors

| Status Code | Error Code | Description | Resolution |
|-------------|------------|-------------|------------|
| 401 | UNAUTHORIZED | Missing or invalid token | Provide valid Bearer token |
| 403 | FORBIDDEN | Insufficient permissions | Request `users:read` permission |
| 404 | USER_NOT_FOUND | User ID doesn't exist | Verify user ID is correct |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests | Wait 60 seconds and retry |

### Error Response Format
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "No user found with ID: 123e4567-e89b-12d3-a456-426614174000",
    "request_id": "req_abc123"
  }
}
```

## Examples

### cURL
```bash
curl -X GET "https://api.example.com/api/v1/users/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Accept: application/json"
```

### JavaScript (fetch)
```javascript
const response = await fetch('https://api.example.com/api/v1/users/123e4567-e89b-12d3-a456-426614174000', {
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'Accept': 'application/json'
  }
});
const user = await response.json();
```

### Python (requests)
```python
import requests

response = requests.get(
    'https://api.example.com/api/v1/users/123e4567-e89b-12d3-a456-426614174000',
    headers={
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
        'Accept': 'application/json'
    }
)
user = response.json()
```

## Rate Limiting
- **Limit**: 100 requests per minute per API key
- **Header**: `X-RateLimit-Remaining` shows remaining requests
- **Reset**: `X-RateLimit-Reset` shows Unix timestamp for reset
```

## Formatting Conventions

### HTTP Methods
- Use all caps in headings: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- Color-code in reference tables (if supported by renderer)

### Status Codes
- Always include numeric code and description: `200 OK`, `404 Not Found`
- Group by category: 2xx Success, 4xx Client Errors, 5xx Server Errors

### JSON Examples
- Use proper JSON formatting with 2-space indentation
- Include realistic sample data (not `foo`, `bar`, `baz`)
- Show complete objects, not partial snippets

### Timestamps
- Always use ISO 8601 format: `2024-01-15T10:30:00Z`
- Include timezone (prefer UTC with `Z` suffix)

### URLs
- Show full URLs in examples: `https://api.example.com/api/v1/resource`
- Use versioning in paths: `/api/v1/`, `/api/v2/`
- Document base URL separately if it varies by environment

## Versioning Documentation

### Breaking Changes
When documenting a new version:
- Clearly mark deprecated fields/endpoints
- Provide migration guide from previous version
- Show side-by-side examples when behavior changes

```markdown
## Migration from v1 to v2

### Changed: User ID Format
- **v1**: Numeric ID (`"id": 12345`)
- **v2**: UUID v4 (`"id": "123e4567-e89b-12d3-a456-426614174000"`)

### Deprecated: Email Verification Field
- Field `email_verified` deprecated in v2
- Use `verification_status` instead (values: `verified`, `pending`, `failed`)
```

## Cross-References

### Linking Between Docs
- Link to related endpoints: "See [Create User](./post-users.md) for creating new users"
- Link to shared concepts: "Authentication works as described in [Auth Guide](../auth.md)"
- Link to data models: "Returns a [User object](../models/user.md)"

### External References
- Link to RFCs for standard implementations: `[RFC 7519](https://tools.ietf.org/html/rfc7519)`
- Link to OAuth specs, OpenAPI specs, etc.
```

---

## Example 3: React Components (TypeScript)

**File**: `.github/instructions/react-components.md`

```markdown
---
applyTo:
  - "src/components/**/*.tsx"
  - "src/components/**/*.ts"
---

# React Component Standards

## Component Structure

### Functional Components Only
Use function declarations (not arrow functions) for better stack traces:

```typescript
// Good
export function Button({ children, onClick, variant = "primary" }: ButtonProps) {
  return <button className={styles[variant]} onClick={onClick}>{children}</button>;
}

// Avoid
export const Button: React.FC<ButtonProps> = ({ children, onClick }) => {
  // ...
};
```

### File Organization (Top to Bottom)
1. Imports (external, then internal)
2. Type definitions (Props, State)
3. Component function
4. Styled components or styles (if colocated)
5. Export statement (if not inline)

## TypeScript Conventions

### Props Interface
- Name with `Props` suffix: `ButtonProps`, `UserCardProps`
- Define above component
- Use destructuring with type annotation

```typescript
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "danger";
  disabled?: boolean;
  className?: string;
}

export function Button({ 
  children, 
  onClick, 
  variant = "primary",
  disabled = false,
  className 
}: ButtonProps) {
  // Implementation
}
```

### Avoid `React.FC`
- Don't use `React.FC` or `React.FunctionComponent`
- Implicit children causes issues
- Explicit props are clearer

### Event Handlers
Type event handlers explicitly:

```typescript
function handleClick(event: React.MouseEvent<HTMLButtonElement>) {
  event.preventDefault();
  // Handle click
}

function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
  setValue(event.target.value);
}
```

## Hooks

### Hook Order and Rules
- Call hooks at top level, before any returns
- Use `use` prefix for custom hooks
- Follow consistent ordering:
  1. Context hooks (`useContext`)
  2. State hooks (`useState`)
  3. Ref hooks (`useRef`)
  4. Effect hooks (`useEffect`, `useLayoutEffect`)
  5. Custom hooks
  6. Callback/memo hooks (`useCallback`, `useMemo`)

### useState
```typescript
const [count, setCount] = useState<number>(0);
const [user, setUser] = useState<User | null>(null);
```

### useEffect Dependencies
- Always include all dependencies
- Use ESLint rule `react-hooks/exhaustive-deps`
- Extract functions that don't need dependencies

```typescript
// Good
useEffect(() => {
  fetchData(userId);
}, [userId]);

// Bad - missing dependency
useEffect(() => {
  fetchData(userId);
}, []);
```

### Custom Hooks
```typescript
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchUser() {
      try {
        setLoading(true);
        const data = await api.getUser(userId);
        setUser(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    }
    fetchUser();
  }, [userId]);

  return { user, loading, error };
}
```

## Styling

### CSS Modules
- Use CSS Modules for component styles
- Name file same as component: `Button.module.css`
- Use camelCase for class names

```typescript
import styles from "./Button.module.css";

export function Button({ variant }: ButtonProps) {
  return <button className={styles.button} data-variant={variant}>Click</button>;
}
```

### Conditional Classes
Use `classnames` or `clsx` library:

```typescript
import clsx from "clsx";

<button className={clsx(
  styles.button,
  variant === "primary" && styles.primary,
  disabled && styles.disabled,
  className
)}>
```

## Props Patterns

### Children
```typescript
// Simple children
interface Props {
  children: React.ReactNode;
}

// Render props
interface Props {
  renderHeader: (title: string) => React.ReactNode;
}
```

### Optional Props with Defaults
Use default parameters, not defaultProps:

```typescript
function Button({ 
  variant = "primary",
  size = "medium"
}: ButtonProps) {
  // ...
}
```

### Rest Props Spreading
Spread remaining props for flexibility:

```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

function Button({ variant = "primary", className, ...rest }: ButtonProps) {
  return <button className={clsx(styles.button, className)} {...rest} />;
}
```

## Performance

### React.memo
Memoize expensive components:

```typescript
export const ExpensiveComponent = React.memo(function ExpensiveComponent({ 
  data 
}: Props) {
  // Expensive rendering
}, (prevProps, nextProps) => {
  return prevProps.data.id === nextProps.data.id;
});
```

### useCallback
Memoize callbacks passed to child components:

```typescript
const handleClick = useCallback(() => {
  doSomething(value);
}, [value]);
```

### useMemo
Memoize expensive calculations:

```typescript
const sortedItems = useMemo(() => {
  return items.sort((a, b) => a.name.localeCompare(b.name));
}, [items]);
```

## Testing Compatibility

### Data Test IDs
Add `data-testid` for testing:

```typescript
<button data-testid="submit-button">Submit</button>
```

### Avoid Inline Functions in JSX
Extract handlers for easier testing and debugging:

```typescript
// Good
function handleSubmit() {
  // Handle submit
}
return <form onSubmit={handleSubmit}>

// Avoid
return <form onSubmit={() => { /* handle submit */ }}>
```

## Accessibility

### Semantic HTML
Use appropriate HTML elements:

```typescript
// Good
<button onClick={handleClick}>Click</button>

// Bad
<div onClick={handleClick}>Click</div>
```

### ARIA Attributes
```typescript
<button
  aria-label="Close dialog"
  aria-pressed={isPressed}
  aria-disabled={isDisabled}
>
  <CloseIcon />
</button>
```

### Keyboard Navigation
Support keyboard interactions:

```typescript
function handleKeyDown(event: React.KeyboardEvent) {
  if (event.key === "Enter" || event.key === " ") {
    handleClick();
  }
}
```
```

---

## Example 4: Kubernetes Manifests (YAML)

**File**: `.github/instructions/kubernetes-manifests.md`

```markdown
---
applyTo:
  - "k8s/**/*.yaml"
  - "k8s/**/*.yml"
  - "kubernetes/**/*.yaml"
  - "manifests/**/*.yaml"
---

# Kubernetes Manifest Standards

## File Organization

### Directory Structure
```
k8s/
├── base/               # Base configurations
│   ├── namespace.yaml
│   ├── configmap.yaml
│   └── secret.yaml
├── apps/               # Application deployments
│   ├── api/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   └── worker/
│       └── deployment.yaml
└── overlays/           # Environment-specific (if using Kustomize)
    ├── dev/
    ├── staging/
    └── production/
```

### File Naming
- Use lowercase with hyphens: `api-deployment.yaml`
- Include resource type: `redis-service.yaml`, `app-configmap.yaml`
- One resource per file (exception: tightly coupled resources)

## Resource Structure

### Standard Order in Multi-Resource Files
1. Namespace
2. ConfigMap / Secret
3. PersistentVolumeClaim
4. Deployment / StatefulSet / DaemonSet
5. Service
6. Ingress

### Metadata Standards

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  namespace: production
  labels:
    app: api-server
    component: backend
    environment: production
    version: v1.2.3
  annotations:
    description: "Main API server handling REST requests"
    maintainer: "platform-team@example.com"
```

#### Required Labels
Every resource must have:
- `app`: Application name
- `component`: Component type (frontend, backend, database, cache)
- `environment`: Environment (dev, staging, production)
- `version`: Application version (semver)

## Deployments

### Resource Limits
Always specify requests and limits:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
        component: backend
    spec:
      containers:
      - name: api
        image: registry.example.com/api-server:v1.2.3
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: log-level
```

### Health Checks
- **Liveness probe**: Detects if container needs restart
- **Readiness probe**: Detects if container can accept traffic
- **Startup probe**: For slow-starting containers (optional)

### Image Practices
- Always use specific tags, never `:latest`
- Use SHA256 digests for production: `image@sha256:abc123...`
- Pull policy: `IfNotPresent` for tagged images, `Always` for `:latest`

```yaml
image: registry.example.com/api-server:v1.2.3
imagePullPolicy: IfNotPresent
```

## Services

### Service Types
- **ClusterIP**: Internal cluster communication (default)
- **NodePort**: External access via node IP
- **LoadBalancer**: Cloud provider load balancer
- **ExternalName**: DNS alias

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-server
  labels:
    app: api-server
spec:
  type: ClusterIP
  selector:
    app: api-server
    component: backend
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
  sessionAffinity: None
```

## ConfigMaps and Secrets

### ConfigMap
Use for non-sensitive configuration:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  log-level: "info"
  max-connections: "100"
  config.json: |
    {
      "feature_flags": {
        "new_ui": true,
        "beta_api": false
      }
    }
```

### Secret
Use for sensitive data (note: encode in base64):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: cGFzc3dvcmQxMjM=  # base64 encoded
```

⚠️ **Never commit real secrets to Git**. Use external secret management (Sealed Secrets, External Secrets Operator, Vault).

## Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls-cert
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-server
            port:
              number: 80
```

## Best Practices

### Security
- Run as non-root user
- Read-only root filesystem when possible
- Drop unnecessary capabilities
- Use Pod Security Standards

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
```

### High Availability
- Set anti-affinity for multi-replica deployments
- Use Pod Disruption Budgets
- Configure appropriate replica counts

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - api-server
        topologyKey: kubernetes.io/hostname
```

### Resource Management
- Set memory/CPU requests based on actual usage
- Set limits to prevent runaway processes
- Use Vertical Pod Autoscaler for optimization

### Documentation
- Add meaningful annotations explaining non-obvious choices
- Document scaling decisions, resource limit rationale
- Include runbook links for operational procedures

```yaml
annotations:
  description: "API server requires high memory for caching"
  scaling-policy: "HPA configured for 60% CPU target"
  runbook: "https://docs.example.com/runbooks/api-server"
```
```

---

## Example 5: Go Testing

**File**: `.github/instructions/go-testing.md`

```markdown
---
applyTo:
  - "**/*_test.go"
---

# Go Testing Standards

## Test File Organization

### Naming and Location
- Test files: `*_test.go` in same package as code under test
- Black-box tests: Use `package foo_test` for external perspective
- White-box tests: Use `package foo` for internal access

```go
// parser_test.go - white-box testing
package parser

// parser_test.go - black-box testing
package parser_test

import (
    "testing"
    "github.com/example/app/parser"
)
```

## Test Function Structure

### Naming Convention
- Function prefix: `Test` for tests, `Benchmark` for benchmarks, `Example` for examples
- Use descriptive names: `TestUserCreate_ValidData_Success`
- Pattern: `Test<Function>_<Condition>_<Expected>`

### Table-Driven Tests
Preferred pattern for multiple test cases:

```go
func TestParseURL(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    *URL
        wantErr bool
    }{
        {
            name:  "valid http URL",
            input: "http://example.com/path",
            want: &URL{
                Scheme: "http",
                Host:   "example.com",
                Path:   "/path",
            },
            wantErr: false,
        },
        {
            name:    "invalid URL missing scheme",
            input:   "example.com",
            want:    nil,
            wantErr: true,
        },
        {
            name:  "URL with query parameters",
            input: "https://example.com?foo=bar&baz=qux",
            want: &URL{
                Scheme: "https",
                Host:   "example.com",
                Query:  "foo=bar&baz=qux",
            },
            wantErr: false,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ParseURL(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("ParseURL() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if !reflect.DeepEqual(got, tt.want) {
                t.Errorf("ParseURL() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

### Subtests
Use `t.Run()` for grouping related tests:

```go
func TestUser(t *testing.T) {
    t.Run("Create", func(t *testing.T) {
        // Test user creation
    })
    
    t.Run("Update", func(t *testing.T) {
        // Test user update
    })
    
    t.Run("Delete", func(t *testing.T) {
        // Test user deletion
    })
}
```

## Assertions

### Standard Library
Use standard `testing` package methods:

```go
if got != want {
    t.Errorf("got %v, want %v", got, want)
}

if err != nil {
    t.Fatalf("unexpected error: %v", err)
}
```

### testify/assert (if used)
```go
import "github.com/stretchr/testify/assert"

assert.Equal(t, expected, actual, "they should be equal")
assert.NoError(t, err)
assert.True(t, isValid)
```

## Test Fixtures and Setup

### TestMain
For package-level setup/teardown:

```go
func TestMain(m *testing.M) {
    // Setup
    db := setupTestDatabase()
    defer db.Close()
    
    // Run tests
    code := m.Run()
    
    // Teardown
    cleanupTestData()
    
    os.Exit(code)
}
```

### Helper Functions
Mark helpers with `t.Helper()`:

```go
func createTestUser(t *testing.T, name string) *User {
    t.Helper()
    user, err := NewUser(name)
    if err != nil {
        t.Fatalf("failed to create test user: %v", err)
    }
    return user
}
```

## Mocking

### Interfaces for Testability
Define interfaces for dependencies:

```go
type UserRepository interface {
    Get(id string) (*User, error)
    Save(user *User) error
}

// Mock implementation
type mockUserRepository struct {
    users map[string]*User
}

func (m *mockUserRepository) Get(id string) (*User, error) {
    user, ok := m.users[id]
    if !ok {
        return nil, ErrNotFound
    }
    return user, nil
}
```

### httptest for HTTP Testing
```go
func TestAPIHandler(t *testing.T) {
    req := httptest.NewRequest("GET", "/users/123", nil)
    w := httptest.NewRecorder()
    
    handler := NewUserHandler(mockRepo)
    handler.ServeHTTP(w, req)
    
    assert.Equal(t, http.StatusOK, w.Code)
}
```

## Benchmarks

```go
func BenchmarkParseURL(b *testing.B) {
    url := "https://example.com/path?query=value"
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        _, _ = ParseURL(url)
    }
}

// Benchmark with different inputs
func BenchmarkSortInts(b *testing.B) {
    sizes := []int{10, 100, 1000, 10000}
    
    for _, size := range sizes {
        b.Run(fmt.Sprintf("size-%d", size), func(b *testing.B) {
            data := generateTestData(size)
            b.ResetTimer()
            
            for i := 0; i < b.N; i++ {
                sort.Ints(data)
            }
        })
    }
}
```

## Examples

### Testable Examples
```go
func ExampleParseURL() {
    url, _ := ParseURL("https://example.com/path")
    fmt.Printf("Scheme: %s, Host: %s", url.Scheme, url.Host)
    // Output: Scheme: https, Host: example.com
}
```

## Coverage

### Running Tests with Coverage
```bash
go test -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### Coverage Goals
- Aim for 80%+ coverage on business logic
- 100% on critical paths (auth, payments, security)
- Use `//go:build integration` tags for integration tests

## Testing Tags

### Build Tags
```go
//go:build integration
// +build integration

package api_test

func TestDatabaseIntegration(t *testing.T) {
    // Integration test requiring real database
}
```

Run with: `go test -tags=integration ./...`

## Best Practices

### Parallel Tests
Mark independent tests as parallel:

```go
func TestIndependentFeature(t *testing.T) {
    t.Parallel()
    // Test implementation
}
```

### Cleanup
Use `t.Cleanup()` for resource cleanup:

```go
func TestWithTempFile(t *testing.T) {
    f, err := os.CreateTemp("", "test")
    if err != nil {
        t.Fatal(err)
    }
    t.Cleanup(func() {
        os.Remove(f.Name())
    })
    
    // Use temporary file
}
```

### Context
Pass context for cancellation and deadlines:

```go
func TestWithTimeout(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    result, err := FetchData(ctx)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}
```
```

---

## Usage Guidelines

Each example above demonstrates:
- **YAML frontmatter** with `applyTo` glob patterns
- **Complete, realistic rules** for the domain
- **Code examples** showing good vs. bad patterns
- **Framework-specific conventions** that would clutter global instructions
- **Practical advice** teams can immediately apply

To use these templates:
1. Copy the relevant example
2. Adjust `applyTo` patterns for your repository structure
3. Customize rules to match your team's conventions
4. Save to `.github/instructions/<name>.md`
5. Test with the glob pattern script to verify scope

