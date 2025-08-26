package com.finrisk.ai.caseservice.repository;

import com.finrisk.ai.caseservice.domain.Case;
import com.finrisk.ai.caseservice.domain.CaseStatus;
import com.finrisk.ai.caseservice.domain.CaseType;
import com.finrisk.ai.caseservice.domain.Priority;
import org.springframework.data.domain.Pageable;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Reactive repository for Case entities
 */
@Repository
public interface CaseRepository extends ReactiveCrudRepository<Case, UUID> {

    /**
     * Find case by case number within tenant and cell
     */
    Mono<Case> findByCaseNumberAndTenantIdAndCellId(String caseNumber, String tenantId, String cellId);

    /**
     * Find all cases for a tenant and cell with pagination
     */
    Flux<Case> findByTenantIdAndCellIdOrderByCreatedAtDesc(String tenantId, String cellId, Pageable pageable);

    /**
     * Find cases by status within tenant and cell
     */
    Flux<Case> findByStatusAndTenantIdAndCellIdOrderByCreatedAtDesc(CaseStatus status, String tenantId, String cellId, Pageable pageable);

    /**
     * Find cases by case type within tenant and cell
     */
    Flux<Case> findByCaseTypeAndTenantIdAndCellIdOrderByCreatedAtDesc(CaseType caseType, String tenantId, String cellId, Pageable pageable);

    /**
     * Find cases by priority within tenant and cell
     */
    Flux<Case> findByPriorityAndTenantIdAndCellIdOrderByCreatedAtDesc(Priority priority, String tenantId, String cellId, Pageable pageable);

    /**
     * Find cases assigned to a specific user
     */
    Flux<Case> findByAssignedToAndTenantIdAndCellIdOrderByCreatedAtDesc(UUID assignedTo, String tenantId, String cellId, Pageable pageable);

    /**
     * Find cases created by a specific user
     */
    Flux<Case> findByCreatedByAndTenantIdAndCellIdOrderByCreatedAtDesc(UUID createdBy, String tenantId, String cellId, Pageable pageable);

    /**
     * Find active cases (not closed or archived)
     */
    @Query("SELECT * FROM cases WHERE status NOT IN ('CLOSED', 'ARCHIVED') AND tenant_id = :tenantId AND cell_id = :cellId ORDER BY created_at DESC")
    Flux<Case> findActiveCases(String tenantId, String cellId, Pageable pageable);

    /**
     * Find high priority cases
     */
    @Query("SELECT * FROM cases WHERE priority IN ('HIGH', 'CRITICAL') AND tenant_id = :tenantId AND cell_id = :cellId ORDER BY priority DESC, created_at DESC")
    Flux<Case> findHighPriorityCases(String tenantId, String cellId, Pageable pageable);

    /**
     * Find cases by date range
     */
    @Query("SELECT * FROM cases WHERE created_at BETWEEN :startDate AND :endDate AND tenant_id = :tenantId AND cell_id = :cellId ORDER BY created_at DESC")
    Flux<Case> findByDateRange(LocalDateTime startDate, LocalDateTime endDate, String tenantId, String cellId, Pageable pageable);

    /**
     * Search cases by title or description (simple text search)
     */
    @Query("SELECT * FROM cases WHERE (LOWER(title) LIKE LOWER(:searchTerm) OR LOWER(description) LIKE LOWER(:searchTerm)) AND tenant_id = :tenantId AND cell_id = :cellId ORDER BY created_at DESC")
    Flux<Case> searchByTitleOrDescription(String searchTerm, String tenantId, String cellId, Pageable pageable);

    /**
     * Count cases by status
     */
    @Query("SELECT COUNT(*) FROM cases WHERE status = :status AND tenant_id = :tenantId AND cell_id = :cellId")
    Mono<Long> countByStatus(CaseStatus status, String tenantId, String cellId);

    /**
     * Count cases by case type
     */
    @Query("SELECT COUNT(*) FROM cases WHERE case_type = :caseType AND tenant_id = :tenantId AND cell_id = :cellId")
    Mono<Long> countByCaseType(CaseType caseType, String tenantId, String cellId);

    /**
     * Count cases by priority
     */
    @Query("SELECT COUNT(*) FROM cases WHERE priority = :priority AND tenant_id = :tenantId AND cell_id = :cellId")
    Mono<Long> countByPriority(Priority priority, String tenantId, String cellId);

    /**
     * Count total cases for tenant and cell
     */
    Mono<Long> countByTenantIdAndCellId(String tenantId, String cellId);

    /**
     * Find overdue cases (in progress for more than specified days)
     */
    @Query("SELECT * FROM cases WHERE status = 'IN_PROGRESS' AND created_at < :cutoffDate AND tenant_id = :tenantId AND cell_id = :cellId ORDER BY created_at ASC")
    Flux<Case> findOverdueCases(LocalDateTime cutoffDate, String tenantId, String cellId);

    /**
     * Find cases by multiple statuses
     */
    @Query("SELECT * FROM cases WHERE status = ANY(:statuses) AND tenant_id = :tenantId AND cell_id = :cellId ORDER BY created_at DESC")
    Flux<Case> findByStatusIn(CaseStatus[] statuses, String tenantId, String cellId, Pageable pageable);

    /**
     * Find cases with tags containing specific tag
     */
    @Query("SELECT * FROM cases WHERE :tag = ANY(tags) AND tenant_id = :tenantId AND cell_id = :cellId ORDER BY created_at DESC")
    Flux<Case> findByTag(String tag, String tenantId, String cellId, Pageable pageable);
}
