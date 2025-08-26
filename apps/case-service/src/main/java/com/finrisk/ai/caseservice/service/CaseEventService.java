package com.finrisk.ai.caseservice.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.finrisk.ai.caseservice.domain.Case;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Service for publishing case-related events to Kafka
 */
@Service
public class CaseEventService {

    private static final Logger logger = LoggerFactory.getLogger(CaseEventService.class);

    // Kafka topics
    private static final String CASE_EVENTS_TOPIC = "case-events";
    private static final String CASE_NOTIFICATIONS_TOPIC = "case-notifications";

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    public CaseEventService(KafkaTemplate<String, String> kafkaTemplate, ObjectMapper objectMapper) {
        this.kafkaTemplate = kafkaTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * Publish case created event
     */
    public Mono<Void> publishCaseCreatedEvent(Case case_) {
        return publishEvent("CASE_CREATED", case_, null)
                .doOnSuccess(v -> logger.info("Published CASE_CREATED event for case: {}", case_.getCaseNumber()));
    }

    /**
     * Publish case updated event
     */
    public Mono<Void> publishCaseUpdatedEvent(Case case_) {
        return publishEvent("CASE_UPDATED", case_, null)
                .doOnSuccess(v -> logger.info("Published CASE_UPDATED event for case: {}", case_.getCaseNumber()));
    }

    /**
     * Publish case assigned event
     */
    public Mono<Void> publishCaseAssignedEvent(Case case_, UUID assigneeId) {
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("assigneeId", assigneeId.toString());
        metadata.put("previousAssignee", case_.getAssignedTo() != null ? case_.getAssignedTo().toString() : null);
        
        return publishEvent("CASE_ASSIGNED", case_, metadata)
                .doOnSuccess(v -> logger.info("Published CASE_ASSIGNED event for case: {} to user: {}", 
                        case_.getCaseNumber(), assigneeId));
    }

    /**
     * Publish case closed event
     */
    public Mono<Void> publishCaseClosedEvent(Case case_, String reason) {
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("closureReason", reason);
        metadata.put("closedAt", case_.getClosedAt().toString());
        
        return publishEvent("CASE_CLOSED", case_, metadata)
                .doOnSuccess(v -> logger.info("Published CASE_CLOSED event for case: {}", case_.getCaseNumber()));
    }

    /**
     * Publish case escalated event
     */
    public Mono<Void> publishCaseEscalatedEvent(Case case_, String reason) {
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("escalationReason", reason);
        metadata.put("previousPriority", case_.getPriority().toString());
        
        return publishEvent("CASE_ESCALATED", case_, metadata)
                .doOnSuccess(v -> logger.info("Published CASE_ESCALATED event for case: {}", case_.getCaseNumber()));
    }

    /**
     * Publish case deleted event
     */
    public Mono<Void> publishCaseDeletedEvent(Case case_) {
        return publishEvent("CASE_DELETED", case_, null)
                .doOnSuccess(v -> logger.info("Published CASE_DELETED event for case: {}", case_.getCaseNumber()));
    }

    /**
     * Generic method to publish case events
     */
    private Mono<Void> publishEvent(String eventType, Case case_, Map<String, Object> additionalMetadata) {
        return Mono.fromCallable(() -> {
            try {
                CaseEvent event = new CaseEvent(
                        UUID.randomUUID().toString(),
                        eventType,
                        case_,
                        additionalMetadata,
                        LocalDateTime.now(),
                        case_.getTenantId(),
                        case_.getCellId()
                );

                String eventJson = objectMapper.writeValueAsString(event);
                
                // Send to case events topic for audit trail
                kafkaTemplate.send(CASE_EVENTS_TOPIC, case_.getId().toString(), eventJson);
                
                // Send to notifications topic for real-time updates
                kafkaTemplate.send(CASE_NOTIFICATIONS_TOPIC, case_.getTenantId(), eventJson);
                
                return null;
            } catch (Exception e) {
                logger.error("Error publishing case event: {}", e.getMessage(), e);
                throw new RuntimeException("Failed to publish case event", e);
            }
        }).then();
    }

    /**
     * Case event DTO for Kafka messages
     */
    public record CaseEvent(
            String eventId,
            String eventType,
            Case case_,
            Map<String, Object> metadata,
            LocalDateTime timestamp,
            String tenantId,
            String cellId
    ) {}
}
