package com.finrisk.ai.caseservice.service;

import com.finrisk.ai.caseservice.domain.Case;
import com.finrisk.ai.caseservice.domain.CaseStatus;
import com.finrisk.ai.caseservice.domain.CaseType;
import com.finrisk.ai.caseservice.domain.Priority;
import com.finrisk.ai.caseservice.repository.CaseRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Service layer for Case management operations
 */
@Service
@Transactional
public class CaseService {

    private static final Logger logger = LoggerFactory.getLogger(CaseService.class);

    private final CaseRepository caseRepository;
    private final CaseEventService caseEventService;
    private final CaseNumberGeneratorService caseNumberGenerator;

    public CaseService(CaseRepository caseRepository, 
                      CaseEventService caseEventService,
                      CaseNumberGeneratorService caseNumberGenerator) {
        this.caseRepository = caseRepository;
        this.caseEventService = caseEventService;
        this.caseNumberGenerator = caseNumberGenerator;
    }

    /**
     * Create a new case
     */
    public Mono<Case> createCase(Case caseRequest) {
        logger.info("Creating new case: {}", caseRequest.getTitle());
        
        return caseNumberGenerator.generateCaseNumber(caseRequest.getCaseType(), caseRequest.getTenantId())
                .flatMap(caseNumber -> {
                    caseRequest.setCaseNumber(caseNumber);
                    caseRequest.setStatus(CaseStatus.OPEN);
                    caseRequest.setCreatedAt(LocalDateTime.now());
                    caseRequest.setUpdatedAt(LocalDateTime.now());
                    
                    return caseRepository.save(caseRequest);
                })
                .flatMap(savedCase -> {
                    // Publish case created event
                    return caseEventService.publishCaseCreatedEvent(savedCase)
                            .thenReturn(savedCase);
                })
                .doOnSuccess(savedCase -> logger.info("Case created successfully: {}", savedCase.getCaseNumber()))
                .doOnError(error -> logger.error("Error creating case: {}", error.getMessage()));
    }

    /**
     * Find case by ID with tenant and cell validation
     */
    @Transactional(readOnly = true)
    public Mono<Case> findById(UUID id, String tenantId, String cellId) {
        return caseRepository.findById(id)
                .filter(case_ -> case_.getTenantId().equals(tenantId) && case_.getCellId().equals(cellId))
                .switchIfEmpty(Mono.error(new CaseNotFoundException("Case not found: " + id)));
    }

    /**
     * Find case by case number
     */
    @Transactional(readOnly = true)
    public Mono<Case> findByCaseNumber(String caseNumber, String tenantId, String cellId) {
        return caseRepository.findByCaseNumberAndTenantIdAndCellId(caseNumber, tenantId, cellId)
                .switchIfEmpty(Mono.error(new CaseNotFoundException("Case not found: " + caseNumber)));
    }

    /**
     * Update an existing case
     */
    public Mono<Case> updateCase(UUID id, Case caseUpdate, String tenantId, String cellId) {
        logger.info("Updating case: {}", id);
        
        return findById(id, tenantId, cellId)
                .flatMap(existingCase -> {
                    // Update fields
                    existingCase.setTitle(caseUpdate.getTitle());
                    existingCase.setDescription(caseUpdate.getDescription());
                    existingCase.setPriority(caseUpdate.getPriority());
                    existingCase.setMetadata(caseUpdate.getMetadata());
                    existingCase.setTags(caseUpdate.getTags());
                    existingCase.setUpdatedAt(LocalDateTime.now());
                    
                    return caseRepository.save(existingCase);
                })
                .flatMap(updatedCase -> {
                    // Publish case updated event
                    return caseEventService.publishCaseUpdatedEvent(updatedCase)
                            .thenReturn(updatedCase);
                })
                .doOnSuccess(updatedCase -> logger.info("Case updated successfully: {}", updatedCase.getCaseNumber()))
                .doOnError(error -> logger.error("Error updating case {}: {}", id, error.getMessage()));
    }

    /**
     * Assign case to a user
     */
    public Mono<Case> assignCase(UUID caseId, UUID assigneeId, String tenantId, String cellId) {
        logger.info("Assigning case {} to user {}", caseId, assigneeId);
        
        return findById(caseId, tenantId, cellId)
                .flatMap(existingCase -> {
                    existingCase.assignTo(assigneeId);
                    existingCase.setUpdatedAt(LocalDateTime.now());
                    
                    return caseRepository.save(existingCase);
                })
                .flatMap(updatedCase -> {
                    // Publish case assigned event
                    return caseEventService.publishCaseAssignedEvent(updatedCase, assigneeId)
                            .thenReturn(updatedCase);
                })
                .doOnSuccess(updatedCase -> logger.info("Case assigned successfully: {}", updatedCase.getCaseNumber()));
    }

    /**
     * Close a case
     */
    public Mono<Case> closeCase(UUID caseId, String reason, String tenantId, String cellId) {
        logger.info("Closing case: {}", caseId);
        
        return findById(caseId, tenantId, cellId)
                .flatMap(existingCase -> {
                    existingCase.close();
                    existingCase.setUpdatedAt(LocalDateTime.now());
                    
                    return caseRepository.save(existingCase);
                })
                .flatMap(closedCase -> {
                    // Publish case closed event
                    return caseEventService.publishCaseClosedEvent(closedCase, reason)
                            .thenReturn(closedCase);
                })
                .doOnSuccess(closedCase -> logger.info("Case closed successfully: {}", closedCase.getCaseNumber()));
    }

    /**
     * Escalate a case
     */
    public Mono<Case> escalateCase(UUID caseId, String reason, String tenantId, String cellId) {
        logger.info("Escalating case: {}", caseId);
        
        return findById(caseId, tenantId, cellId)
                .flatMap(existingCase -> {
                    existingCase.escalate();
                    existingCase.setUpdatedAt(LocalDateTime.now());
                    
                    return caseRepository.save(existingCase);
                })
                .flatMap(escalatedCase -> {
                    // Publish case escalated event
                    return caseEventService.publishCaseEscalatedEvent(escalatedCase, reason)
                            .thenReturn(escalatedCase);
                })
                .doOnSuccess(escalatedCase -> logger.info("Case escalated successfully: {}", escalatedCase.getCaseNumber()));
    }

    /**
     * Find all cases with pagination
     */
    @Transactional(readOnly = true)
    public Flux<Case> findAllCases(String tenantId, String cellId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return caseRepository.findByTenantIdAndCellIdOrderByCreatedAtDesc(tenantId, cellId, pageable);
    }

    /**
     * Find cases by status
     */
    @Transactional(readOnly = true)
    public Flux<Case> findCasesByStatus(CaseStatus status, String tenantId, String cellId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return caseRepository.findByStatusAndTenantIdAndCellIdOrderByCreatedAtDesc(status, tenantId, cellId, pageable);
    }

    /**
     * Find cases by type
     */
    @Transactional(readOnly = true)
    public Flux<Case> findCasesByType(CaseType caseType, String tenantId, String cellId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return caseRepository.findByCaseTypeAndTenantIdAndCellIdOrderByCreatedAtDesc(caseType, tenantId, cellId, pageable);
    }

    /**
     * Find cases by priority
     */
    @Transactional(readOnly = true)
    public Flux<Case> findCasesByPriority(Priority priority, String tenantId, String cellId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return caseRepository.findByPriorityAndTenantIdAndCellIdOrderByCreatedAtDesc(priority, tenantId, cellId, pageable);
    }

    /**
     * Find cases assigned to a user
     */
    @Transactional(readOnly = true)
    public Flux<Case> findCasesAssignedTo(UUID userId, String tenantId, String cellId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return caseRepository.findByAssignedToAndTenantIdAndCellIdOrderByCreatedAtDesc(userId, tenantId, cellId, pageable);
    }

    /**
     * Find active cases
     */
    @Transactional(readOnly = true)
    public Flux<Case> findActiveCases(String tenantId, String cellId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return caseRepository.findActiveCases(tenantId, cellId, pageable);
    }

    /**
     * Find high priority cases
     */
    @Transactional(readOnly = true)
    public Flux<Case> findHighPriorityCases(String tenantId, String cellId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        return caseRepository.findHighPriorityCases(tenantId, cellId, pageable);
    }

    /**
     * Search cases by title or description
     */
    @Transactional(readOnly = true)
    public Flux<Case> searchCases(String searchTerm, String tenantId, String cellId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        String searchPattern = "%" + searchTerm + "%";
        return caseRepository.searchByTitleOrDescription(searchPattern, tenantId, cellId, pageable);
    }

    /**
     * Get case statistics
     */
    @Transactional(readOnly = true)
    public Mono<CaseStatistics> getCaseStatistics(String tenantId, String cellId) {
        return Mono.zip(
                caseRepository.countByTenantIdAndCellId(tenantId, cellId),
                caseRepository.countByStatus(CaseStatus.OPEN, tenantId, cellId),
                caseRepository.countByStatus(CaseStatus.IN_PROGRESS, tenantId, cellId),
                caseRepository.countByStatus(CaseStatus.CLOSED, tenantId, cellId),
                caseRepository.countByPriority(Priority.HIGH, tenantId, cellId),
                caseRepository.countByPriority(Priority.CRITICAL, tenantId, cellId)
        ).map(tuple -> new CaseStatistics(
                tuple.getT1(), // total
                tuple.getT2(), // open
                tuple.getT3(), // in progress
                tuple.getT4(), // closed
                tuple.getT5() + tuple.getT6() // high priority (high + critical)
        ));
    }

    /**
     * Delete a case (soft delete by setting status to ARCHIVED)
     */
    public Mono<Void> deleteCase(UUID caseId, String tenantId, String cellId) {
        logger.info("Deleting case: {}", caseId);
        
        return findById(caseId, tenantId, cellId)
                .flatMap(existingCase -> {
                    existingCase.setStatus(CaseStatus.ARCHIVED);
                    existingCase.setUpdatedAt(LocalDateTime.now());
                    
                    return caseRepository.save(existingCase);
                })
                .flatMap(archivedCase -> {
                    // Publish case deleted event
                    return caseEventService.publishCaseDeletedEvent(archivedCase);
                })
                .doOnSuccess(result -> logger.info("Case deleted successfully: {}", caseId))
                .then();
    }

    /**
     * Case statistics DTO
     */
    public record CaseStatistics(
            Long totalCases,
            Long openCases,
            Long inProgressCases,
            Long closedCases,
            Long highPriorityCases
    ) {}

    /**
     * Case not found exception
     */
    public static class CaseNotFoundException extends RuntimeException {
        public CaseNotFoundException(String message) {
            super(message);
        }
    }
}
