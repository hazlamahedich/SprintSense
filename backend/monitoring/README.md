# Sprintsense Quality Metrics Monitoring

This document describes the monitoring and alerting setup for the Sprintsense Quality Metrics system.

## Overview

Our monitoring system consists of:
- Prometheus for metrics collection and alerting
- Alertmanager for alert routing and aggregation
- Grafana for visualization
- PagerDuty for urgent notifications
- Slack for general alerts

## Metrics Collection

### Performance Metrics
- API Response Time (p95): `quality_metrics:api_latency:p95`
- Cache Operation Time (p95): `quality_metrics:cache_latency:p95`
- Request Rate: `quality_metrics:request_rate:per_second`

### Reliability Metrics
- Error Rate: `quality_metrics:api_error_rate:ratio`
- Cache Hit Rate: `quality_metrics:cache_hit_rate:ratio`
- Data Consistency: `quality_metrics:feedback_consistency:ratio`

### Business Metrics
- Recommendation Acceptance Rate: `quality_metrics:acceptance_rate:ratio`
- Confidence Score (median): `quality_metrics:confidence_score:median`

## Alert Rules

### Critical Alerts (PagerDuty)

1. **High Error Rate**
   - Trigger: Error rate > 5% over 5 minutes
   - Potential causes:
     - Database connectivity issues
     - Cache service failure
     - API rate limiting
   - Resolution steps:
     1. Check error logs in ELK
     2. Verify database connectivity
     3. Check cache service status
     4. Investigate rate limiting metrics

2. **API Performance Degradation**
   - Trigger: p95 latency > 200ms over 5 minutes
   - Potential causes:
     - High database load
     - Network congestion
     - Resource exhaustion
   - Resolution steps:
     1. Check system resources (CPU, memory)
     2. Analyze database query performance
     3. Review network metrics
     4. Scale services if needed

### Warning Alerts (Slack)

1. **Cache Effectiveness Drop**
   - Trigger: Cache miss rate > 20% over 5 minutes
   - Resolution steps:
     1. Check cache server health
     2. Review cache invalidation patterns
     3. Analyze cache hit/miss distributions
     4. Adjust cache TTLs if needed

2. **Low Confidence Scores**
   - Trigger: Median confidence < 70% over 30 minutes
   - Resolution steps:
     1. Review recent model changes
     2. Check input data quality
     3. Analyze low-confidence patterns
     4. Consider model retraining

3. **Data Inconsistency**
   - Trigger: Feedback inconsistency > 10% over 1 hour
   - Resolution steps:
     1. Check feedback collection pipeline
     2. Verify database consistency
     3. Review event processing logs
     4. Run consistency check jobs

## Dashboards

### Main Overview Dashboard
- Overall system health
- Key performance indicators
- Alert status and history

### Technical Dashboard
- Detailed performance metrics
- Resource utilization
- Error rate breakdown
- Cache performance

### Business Metrics Dashboard
- Acceptance rates
- Confidence scores
- Feedback distribution
- Quality trends

## Setup Instructions

1. Deploy Prometheus Rules:
   ```bash
   cp monitoring/prometheus/rules/*.yml /etc/prometheus/rules/
   ```

2. Configure Alertmanager:
   ```bash
   cp monitoring/alertmanager/alertmanager.yml /etc/alertmanager/
   ```

3. Set Environment Variables:
   ```bash
   export SLACK_WEBHOOK_URL="your-webhook-url"
   export PAGERDUTY_SERVICE_KEY="your-service-key"
   ```

4. Restart Services:
   ```bash
   sudo systemctl restart prometheus alertmanager
   ```

## Configuration Files

- Alert Rules: `prometheus/rules/quality_metrics_alerts.yml`
- Recording Rules: `prometheus/rules/quality_metrics_recording.yml`
- Alertmanager Config: `alertmanager/alertmanager.yml`

## Alert Severity Levels

1. **Critical (PagerDuty)**
   - Service outage
   - High error rates (>5%)
   - Severe performance degradation
   - Data consistency issues

2. **Warning (Slack)**
   - Performance degradation
   - Cache issues
   - Model quality concerns
   - Resource utilization warnings

## Response Guidelines

### Immediate Actions
1. Acknowledge alert in PagerDuty/Slack
2. Check relevant dashboards
3. Review recent deployments
4. Check error logs

### Investigation
1. Use provided metrics
2. Follow error patterns
3. Review system logs
4. Check dependent services

### Resolution
1. Apply necessary fixes
2. Document root cause
3. Update runbooks
4. Create post-mortem if needed

## Maintenance

### Daily
- Review alert status
- Check dashboard health
- Verify metric collection

### Weekly
- Review alert thresholds
- Check for stale rules
- Update documentation

### Monthly
- Full system review
- Threshold adjustments
- Cleanup old alerts
- Document improvements
