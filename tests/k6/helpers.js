// Random UUID generator
export function randomUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Random item from array
export function randomItem(array) {
  return array[Math.floor(Math.random() * array.length)];
}

// Sleep with jitter
export function sleepWithJitter(base, jitter = 0.1) {
  const delay = base * (1 + (Math.random() * jitter * 2 - jitter));
  sleep(delay);
}

// Parse and check response
export function checkResponse(response, context = {}) {
  const result = {
    status: response.status === 200,
    duration: response.timings.duration < (context.maxDuration || 200),
    validJson: false,
    hasData: false,
  };

  try {
    const data = response.json();
    result.validJson = true;
    result.hasData = Object.keys(data).length > 0;
  } catch (e) {
    // Invalid JSON
  }

  return result;
}