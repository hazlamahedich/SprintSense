import http from 'k6/http';
import { check } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests must complete below 200ms
    'http_req_duration{type:analyze}': ['p(95)<100'], // Analysis endpoint
    'http_req_duration{type:ws}': ['p(95)<50'],       // WebSocket updates
    errors: ['rate<0.1'],                             // Error rate must be less than 10%
  },
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 30,                // Number of iterations per timeUnit
      timeUnit: '1s',          // Time unit for rate
      duration: '30s',         // Total scenario duration
      preAllocatedVUs: 20,     // Number of VUs to pre-allocate
      maxVUs: 50,              // Maximum number of VUs to allow
    },
  },
};

// Helper to generate JWT token (replace with actual token generation)
function getAuthToken() {
  return 'test-token';
}

// Helper to generate test data
function generateTestData() {
  return {
    sprintId: '550e8400-e29b-41d4-a716-446655440000',
    teamCapacity: [
      {
        userId: '550e8400-e29b-41d4-a716-446655440001',
        availability: 0.8,
        skills: ['python', 'react'],
        timeZone: 'UTC',
      },
    ],
    workItems: [
      {
        workItemId: '550e8400-e29b-41d4-a716-446655440002',
        storyPoints: 5,
        requiredSkills: ['python'],
        assignedTo: '550e8400-e29b-41d4-a716-446655440001',
        estimatedHours: 8,
      },
    ],
  };
}

export default function () {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`,
    },
    tags: { type: 'analyze' },
  };

  // Test sprint balance analysis endpoint
  const payload = JSON.stringify(generateTestData());
  const analysisRes = http.post('http://localhost:8000/api/v1/sprints/balance/analyze', payload, params);

  const analysisSuccess = check(analysisRes, {
    'status is 200': (r) => r.status === 200,
  });

  if (!analysisSuccess) {
    errorRate.add(1);
  }
}
