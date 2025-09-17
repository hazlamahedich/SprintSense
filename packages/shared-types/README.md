# SprintSense Shared Types

This package contains automatically generated TypeScript types from the SprintSense backend API.

## Generation

Types are generated using `openapi-typescript-codegen` from the FastAPI OpenAPI specification.

To regenerate types:

```bash
cd frontend
npm run gen-types
```

## Usage

Import types in your frontend code:

```typescript
import { HealthResponse } from '@sprintsense/shared-types';
```

## Note

**Do not manually edit files in this directory** - they are automatically generated and will be overwritten.
