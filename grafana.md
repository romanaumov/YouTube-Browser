
## Queries to display graphs using Grafana 

We can (and should) also use special grafana variables

- `$__timeFrom()` and `$__timeTo()`: Start and end of the selected time range
- `$__timeGroup(timestamp, $__interval)`: Groups results by time intervals automatically calculated by Grafana

### 1. Model Response Time

This query shows the response time for each conversation within the selected time range:

```sql
SELECT
  timestamp AS time,
  response_time
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
ORDER BY timestamp
```

### 2. Answer Relevance Distribution

This query counts the number of conversations for each relevance category within the selected time range:

```sql
SELECT
  relevance,
  COUNT(*) as count
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY relevance
```

### 3. Total Tokens Usage

This query shows the average token usage over time, grouped by Grafana's automatically calculated interval:

```sql
SELECT
  $__timeGroup(timestamp, $__interval) AS time,
  AVG(total_tokens) AS avg_tokens
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY 1
ORDER BY 1
```

### 4. OpenAI Costs

This query shows the total OpenAI cost over time, grouped by Grafana's automatically calculated interval:

```sql
SELECT
  $__timeGroup(timestamp, $__interval) AS time,
  SUM(openai_cost) AS total_cost
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
  AND openai_cost > 0
GROUP BY 1
ORDER BY 1
```

### 5. Recent Conversations

This query retrieves the 5 most recent conversations within the selected time range:

```sql
SELECT
  timestamp AS time,
  question,
  answer,
  relevance
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
ORDER BY timestamp DESC
LIMIT 5
```

### 6. Feedback Statistics

This query calculates the total number of positive and negative feedback within the selected time range:

```sql
SELECT
  SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
  SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
FROM feedback
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
```