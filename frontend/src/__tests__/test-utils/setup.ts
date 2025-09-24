import '@testing-library/jest-dom';
import './mocks/icons';
import './mocks/headless-ui';
import './mocks/select';

console.log('Loading test setup...');
console.log('Test utilities imported');

// Mock URL environment variable
process.env.VITE_API_URL = 'http://localhost:3000';
