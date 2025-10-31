// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

// If no API URL is set, use proxy for local dev, otherwise use empty string (backend handles /analyze directly)
export const API_URL = API_BASE_URL;
export default API_URL;

