# GatherHub API Rate Limiting Guide

## Overview

GatherHub implements comprehensive rate limiting to ensure fair usage, prevent abuse, and maintain optimal performance for all users. Different endpoints have different limits based on their impact and security considerations.

## Rate Limiting Strategy

### Limit Types

The API implements multiple rate limiting strategies:

1. **Per-User Limits**: Applied to authenticated users
2. **Per-IP Limits**: Applied to anonymous requests and as a fallback
3. **Endpoint-Specific Limits**: Different limits for different types of operations
4. **Global Limits**: Overall API usage limits

### Rate Limit Headers

Every API response includes rate limiting information in the headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1640995200
X-RateLimit-Type: general
```

- `X-RateLimit-Limit`: Maximum requests allowed in the time window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when the limit resets
- `X-RateLimit-Type`: Type of rate limit applied

## Endpoint-Specific Limits

### Authentication Endpoints

**Type**: `auth`  
**Limit**: 5 requests per minute per IP address

**Affected Endpoints**:

- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/token/`
- `POST /api/v1/auth/password/change/`

**Example Response Headers**:

```http
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1640995260
X-RateLimit-Type: auth
```

### Voting Endpoints

**Type**: `voting`  
**Limit**: 10 requests per minute per user

**Affected Endpoints**:

- `POST /api/v1/voting/votes/`
- `PUT /api/v1/voting/votes/{id}/`
- `DELETE /api/v1/voting/votes/{id}/`

**Example**:

```bash
curl -X POST http://localhost:8000/api/v1/voting/votes/ \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"timeslot": 1}'
```

### Task Management Endpoints

**Type**: `tasks`  
**Limit**: 20 requests per minute per user

**Affected Endpoints**:

- `POST /api/v1/tasks/`
- `PUT /api/v1/tasks/{id}/`
- `PATCH /api/v1/tasks/{id}/`
- `DELETE /api/v1/tasks/{id}/`

### General API Endpoints

**Type**: `general`  
**Limit**: 100 requests per minute per user / 100 per hour for anonymous

**Affected Endpoints**:

- `GET /api/v1/events/`
- `GET /api/v1/events/{id}/`
- `GET /api/v1/profile/`
- All other read operations

## Rate Limit Responses

### Success Response

When within limits, requests proceed normally with rate limit headers:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Type: general
Content-Type: application/json

{
  "data": "..."
}
```

### Rate Limit Exceeded

When limits are exceeded, the API returns a 429 status code:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995260
X-RateLimit-Type: auth
Content-Type: application/json

{
  "error": "Rate limit exceeded",
  "detail": "Too many requests. Please try again later.",
  "type": "auth"
}
```

## Implementation Examples

### JavaScript with Automatic Retry

```javascript
class GatherHubAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async request(method, endpoint, data = null, retryCount = 0) {
    const url = `${this.baseURL}${endpoint}`;
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      // Handle rate limiting
      if (response.status === 429) {
        const retryAfter = this.getRetryDelay(response);

        if (retryCount < 3) {
          // Max 3 retries
          console.log(`Rate limited. Retrying after ${retryAfter}ms...`);
          await this.sleep(retryAfter);
          return this.request(method, endpoint, data, retryCount + 1);
        } else {
          throw new Error("Rate limit exceeded. Max retries reached.");
        }
      }

      return response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  getRetryDelay(response) {
    const resetTime = parseInt(response.headers.get("X-RateLimit-Reset"));
    const currentTime = Math.floor(Date.now() / 1000);
    const delay = (resetTime - currentTime) * 1000;

    // Minimum delay of 1 second, maximum of 60 seconds
    return Math.min(Math.max(delay, 1000), 60000);
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // Example usage methods
  async getEvents() {
    return this.request("GET", "/api/v1/events/");
  }

  async createVote(timeslotId) {
    return this.request("POST", "/api/v1/voting/votes/", {
      timeslot: timeslotId,
    });
  }
}

// Usage
const api = new GatherHubAPI("http://localhost:8000", "your_token");

try {
  const events = await api.getEvents();
  console.log("Events:", events);
} catch (error) {
  console.error("Failed to get events:", error);
}
```

### Python with Exponential Backoff

```python
import requests
import time
import random
from typing import Optional

class GatherHubAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

    def request(self, method: str, endpoint: str, data: Optional[dict] = None,
                max_retries: int = 3) -> dict:
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries + 1):
            try:
                response = self.session.request(method, url, json=data)

                if response.status_code == 429:
                    if attempt < max_retries:
                        delay = self._calculate_retry_delay(response, attempt)
                        print(f"Rate limited. Retrying after {delay}s...")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception("Rate limit exceeded. Max retries reached.")

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    delay = self._exponential_backoff(attempt)
                    time.sleep(delay)
                    continue
                raise e

    def _calculate_retry_delay(self, response: requests.Response, attempt: int) -> float:
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        current_time = int(time.time())
        delay = max(reset_time - current_time, 1)

        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.1, 0.5)
        return min(delay + jitter, 60)

    def _exponential_backoff(self, attempt: int) -> float:
        delay = (2 ** attempt) + random.uniform(0, 1)
        return min(delay, 30)

    # API methods
    def get_events(self):
        return self.request('GET', '/api/v1/events/')

    def create_vote(self, timeslot_id: int):
        return self.request('POST', '/api/v1/voting/votes/', {
            'timeslot': timeslot_id
        })

# Usage
api = GatherHubAPI('http://localhost:8000', 'your_token')

try:
    events = api.get_events()
    print(f"Retrieved {len(events['results'])} events")
except Exception as e:
    print(f"API request failed: {e}")
```

### curl with Rate Limit Handling

```bash
#!/bin/bash

# Function to make API request with rate limit handling
make_api_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    local max_retries=3
    local retry_count=0

    while [ $retry_count -lt $max_retries ]; do
        if [ -n "$data" ]; then
            response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
                -X $method "http://localhost:8000$endpoint" \
                -H "Authorization: Bearer $token" \
                -H "Content-Type: application/json" \
                -d "$data")
        else
            response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
                -X $method "http://localhost:8000$endpoint" \
                -H "Authorization: Bearer $token")
        fi

        http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
        body=$(echo $response | sed -e 's/HTTPSTATUS:.*//g')

        if [ $http_code -eq 429 ]; then
            echo "Rate limited. Retrying in 5 seconds..."
            sleep 5
            retry_count=$((retry_count + 1))
        else
            echo $body
            return 0
        fi
    done

    echo "Max retries reached. Request failed."
    return 1
}

# Usage examples
TOKEN="your_access_token"

# Get events (no data needed)
make_api_request "GET" "/api/v1/events/" "" "$TOKEN"

# Create vote (with data)
make_api_request "POST" "/api/v1/voting/votes/" '{"timeslot": 1}' "$TOKEN"
```

## Best Practices

### Client-Side Implementation

1. **Monitor Rate Limits**:

   ```javascript
   const remaining = parseInt(response.headers.get("X-RateLimit-Remaining"));
   if (remaining < 10) {
     console.warn("Approaching rate limit");
   }
   ```

2. **Implement Exponential Backoff**:

   - Start with a small delay (1 second)
   - Double the delay after each retry
   - Add random jitter to prevent synchronized retries
   - Set a maximum delay limit

3. **Cache Responses**:

   ```javascript
   const cache = new Map();

   async function getCachedEvents() {
     const cacheKey = "events";
     const cached = cache.get(cacheKey);

     if (cached && Date.now() - cached.timestamp < 60000) {
       // 1 minute cache
       return cached.data;
     }

     const data = await api.getEvents();
     cache.set(cacheKey, { data, timestamp: Date.now() });
     return data;
   }
   ```

4. **Batch Operations**:

   ```javascript
   // Instead of multiple individual requests
   const votes = [1, 2, 3];
   for (const timeslotId of votes) {
     await api.createVote(timeslotId); // Rate limit risk
   }

   // Use batch endpoint when available
   await api.createBatchVotes(votes);
   ```

### Server-Side Optimization

1. **Use Connection Pooling**: Reuse HTTP connections
2. **Implement Caching**: Cache frequent requests
3. **Optimize Queries**: Reduce database load
4. **Use CDN**: Cache static content

## Monitoring and Alerts

### Rate Limit Monitoring

Track rate limit metrics:

- Requests per minute by endpoint
- Rate limit violations by user/IP
- Average response times
- Error rates

### Alert Thresholds

Set up alerts for:

- High rate limit violation rates (>5%)
- Unusual traffic patterns
- Slow response times during rate limiting
- Failed retry attempts

## Production Considerations

### Rate Limit Adjustments

Production environments may have different limits:

- **Authentication**: 3 requests per minute (stricter)
- **Voting**: 5 requests per minute (stricter)
- **General API**: 500 requests per hour per user (higher limit)

### Load Balancing

When using multiple servers:

- Use Redis for shared rate limit counters
- Consider sticky sessions for user-based limits
- Implement circuit breakers for downstream services

### Graceful Degradation

When rate limits are exceeded:

- Serve cached responses when possible
- Provide helpful error messages
- Suggest alternative actions
- Queue non-critical operations

## Testing Rate Limits

### Load Testing

```python
import asyncio
import aiohttp
import time

async def test_rate_limit():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(20):  # Exceed rate limit
            task = session.post(
                'http://localhost:8000/api/v1/auth/token/',
                json={'email': 'test@example.com', 'password': 'test123'},
                headers={'Content-Type': 'application/json'}
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Request {i}: Exception - {response}")
            else:
                print(f"Request {i}: Status {response.status}")

# Run test
asyncio.run(test_rate_limit())
```

### Manual Testing

```bash
# Test authentication rate limit
for i in {1..10}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/v1/auth/token/ \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "test123"}' \
    -w "Status: %{http_code}\n"
  echo "---"
done
```

This rate limiting system ensures fair usage while maintaining good performance for all GatherHub users.
