import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomUUID } from './helpers.js';

// Test configuration
export const options = {
  // Test scenarios
  scenarios: {
    // Smoke test
    smoke: {
      executor: 'constant-vus',
      vus: 1,
      duration: '30s',
      gracefulStop: '5s',
      exec: 'smoke',
      tags: { test_type: 'smoke' },
    },
    
    // Load test
    load: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '1m', target: 10 },
        { duration: '3m', target: 10 },
        { duration: '1m', target: 0 },
      ],
      gracefulStop: '5s',
      exec: 'load',
      tags: { test_type: 'load' },
    },
    
    // Stress test
    stress: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '1m', target: 20 },
        { duration: '2m', target: 20 },
        { duration: '1m', target: 30 },
        { duration: '2m', target: 30 },
        { duration: '1m', target: 0 },
      ],
      gracefulStop: '5s',
      exec: 'stress',
      tags: { test_type: 'stress' },
    },
    
    // Spike test
    spike: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 50 },
        { duration: '1m', target: 50 },
        { duration: '30s', target: 0 },
      ],
      gracefulStop: '5s',
      exec: 'spike',
      tags: { test_type: 'spike' },
    },
  },
  
  // Test thresholds
  thresholds: {
    http_req_duration: ['p95<200'],  // 95% of requests should complete within 200ms
    http_req_failed: ['rate<0.01'],  // Less than 1% of requests should fail
    http_reqs: ['rate>=100'],        // Maintain at least 100 RPS
    ws_connecting: ['p95<500'],      // 95% of WebSocket connections within 500ms
    ws_msgs_received: ['rate>=10'],  // At least 10 messages per second
  },
};

// Shared test data
const TEST_DATA = {
  team_capacity: Array.from({ length: 50 }, (_, i) => ({
    user_id: randomUUID(),
    availability: Math.random() * 0.5 + 0.5,
    skills: ['python', 'react', 'typescript'].slice(i % 3),
    time_zone: 'UTC',
  })),
  
  work_items: Array.from({ length: 200 }, (_, i) => ({
    work_item_id: randomUUID(),
    story_points: (i % 5) + 1,
    required_skills: ['python', 'react', 'typescript'].slice(i % 3),
    assigned_to: randomUUID(),
    estimated_hours: ((i % 5) + 1) * 4,
  })),
};

// Helper to get auth token
function getAuthToken() {
  const response = http.post('http://localhost:8000/api/auth/login', {
    email: 'test@example.com',
    password: 'testpass123',
  });
  return response.json().access_token;
}

// Helper to make authenticated request
function authenticatedRequest(method, url, body = null) {
  const token = getAuthToken();
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
  
  return http.request(method, url, body, { headers });
}

// WebSocket connection helper
function connectWebSocket(sprintId) {
  const token = getAuthToken();
  const url = `ws://localhost:8000/ws/sprints/${sprintId}/balance?token=${token}`;
  
  return new WebSocket(url);
}

// Smoke test
export function smoke() {
  const sprintId = randomUUID();
  
  // Test REST API
  const response = authenticatedRequest(
    'POST',
    `http://localhost:8000/api/sprints/${sprintId}/balance`,
    JSON.stringify({
      team_capacity: TEST_DATA.team_capacity.slice(0, 5),
      work_items: TEST_DATA.work_items.slice(0, 10),
    })
  );
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'has balance metrics': (r) => r.json().overall_balance_score !== undefined,
  });
  
  // Test WebSocket
  const ws = connectWebSocket(sprintId);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    check(data, {
      'received initial balance': () => data.type === 'initial_balance',
      'has balance data': () => data.data.overall_balance_score !== undefined,
    });
  };
  
  sleep(5);
  ws.send(JSON.stringify({ type: 'refresh' }));
  sleep(5);
  ws.close();
}

// Load test
export function load() {
  const sprintId = randomUUID();
  
  // Test REST API under load
  const response = authenticatedRequest(
    'POST',
    `http://localhost:8000/api/sprints/${sprintId}/balance`,
    JSON.stringify({
      team_capacity: TEST_DATA.team_capacity.slice(0, 20),
      work_items: TEST_DATA.work_items.slice(0, 50),
    })
  );
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 200,
  });
  
  sleep(1);
}

// Stress test
export function stress() {
  const sprintId = randomUUID();
  
  // Test REST API under stress
  const response = authenticatedRequest(
    'POST',
    `http://localhost:8000/api/sprints/${sprintId}/balance`,
    JSON.stringify({
      team_capacity: TEST_DATA.team_capacity,
      work_items: TEST_DATA.work_items,
    })
  );
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 1000,
  });
  
  sleep(0.5);
}

// Spike test
export function spike() {
  const sprintId = randomUUID();
  
  // Test REST API under spike
  const response = authenticatedRequest(
    'POST',
    `http://localhost:8000/api/sprints/${sprintId}/balance`,
    JSON.stringify({
      team_capacity: TEST_DATA.team_capacity.slice(0, 30),
      work_items: TEST_DATA.work_items.slice(0, 100),
    })
  );
  
  check(response, {
    'status is 200': (r) => r.status === 200,
  });
  
  sleep(0.1);
}