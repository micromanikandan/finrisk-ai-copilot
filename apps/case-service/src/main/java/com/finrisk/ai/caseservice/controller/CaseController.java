package com.finrisk.ai.caseservice.controller;

import com.finrisk.ai.caseservice.domain.Case;
import com.finrisk.ai.caseservice.domain.CaseStatus;
import com.finrisk.ai.caseservice.domain.CaseType;
import com.finrisk.ai.caseservice.domain.Priority;
import com.finrisk.ai.caseservice.service.CaseService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.UUID;

/**
 * REST API controller for Case management
 */
@RestController
@RequestMapping("/api/v1/cases")
@Tag(name = "Cases", description = "Case management API for fraud and compliance investigations")
public class CaseController {

    private final CaseService caseService;

    public CaseController(CaseService caseService) {
        this.caseService = caseService;
    }

    @PostMapping
    @Operation(summary = "Create a new case", description = "Creates a new investigation case")
    @ApiResponse(responseCode = "201", description = "Case created successfully")
    @ApiResponse(responseCode = "400", description = "Invalid request data")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Mono<ResponseEntity<Case>> createCase(
            @Valid @RequestBody Case caseRequest,
            @AuthenticationPrincipal Jwt jwt) {
        
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        UUID userId = extractUserId(jwt);
        
        caseRequest.setCreatedBy(userId);
        caseRequest.setTenantId(tenantId);
        caseRequest.setCellId(cellId);
        
        return caseService.createCase(caseRequest)
                .map(createdCase -> ResponseEntity.status(HttpStatus.CREATED).body(createdCase));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get case by ID", description = "Retrieves a case by its unique identifier")
    @ApiResponse(responseCode = "200", description = "Case found")
    @ApiResponse(responseCode = "404", description = "Case not found")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Mono<ResponseEntity<Case>> getCaseById(
            @PathVariable UUID id,
            @AuthenticationPrincipal Jwt jwt) {
        
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        
        return caseService.findById(id, tenantId, cellId)
                .map(ResponseEntity::ok)
                .onErrorReturn(CaseService.CaseNotFoundException.class, 
                              ResponseEntity.notFound().build());
    }

    @GetMapping("/number/{caseNumber}")
    @Operation(summary = "Get case by case number", description = "Retrieves a case by its case number")
    @ApiResponse(responseCode = "200", description = "Case found")
    @ApiResponse(responseCode = "404", description = "Case not found")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Mono<ResponseEntity<Case>> getCaseByCaseNumber(
            @PathVariable String caseNumber,
            @AuthenticationPrincipal Jwt jwt) {
        
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        
        return caseService.findByCaseNumber(caseNumber, tenantId, cellId)
                .map(ResponseEntity::ok)
                .onErrorReturn(CaseService.CaseNotFoundException.class, 
                              ResponseEntity.notFound().build());
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update case", description = "Updates an existing case")
    @ApiResponse(responseCode = "200", description = "Case updated successfully")
    @ApiResponse(responseCode = "404", description = "Case not found")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Mono<ResponseEntity<Case>> updateCase(
            @PathVariable UUID id,
            @Valid @RequestBody Case caseUpdate,
            @AuthenticationPrincipal Jwt jwt) {
        
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        
        return caseService.updateCase(id, caseUpdate, tenantId, cellId)
                .map(ResponseEntity::ok)
                .onErrorReturn(CaseService.CaseNotFoundException.class, 
                              ResponseEntity.notFound().build());
    }

    @PostMapping("/{id}/assign")
    @Operation(summary = "Assign case", description = "Assigns a case to a user")
    @ApiResponse(responseCode = "200", description = "Case assigned successfully")
    @ApiResponse(responseCode = "404", description = "Case not found")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Mono<ResponseEntity<Case>> assignCase(
            @PathVariable UUID id,
            @RequestBody AssignCaseRequest request,
            @AuthenticationPrincipal Jwt jwt) {
        
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        
        return caseService.assignCase(id, request.assigneeId(), tenantId, cellId)
                .map(ResponseEntity::ok)
                .onErrorReturn(CaseService.CaseNotFoundException.class, 
                              ResponseEntity.notFound().build());
    }

    @PostMapping("/{id}/close")
    @Operation(summary = "Close case", description = "Closes an investigation case")
    @ApiResponse(responseCode = "200", description = "Case closed successfully")
    @ApiResponse(responseCode = "404", description = "Case not found")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Mono<ResponseEntity<Case>> closeCase(
            @PathVariable UUID id,
            @RequestBody CloseCaseRequest request,
            @AuthenticationPrincipal Jwt jwt) {
        
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        
        return caseService.closeCase(id, request.reason(), tenantId, cellId)
                .map(ResponseEntity::ok)
                .onErrorReturn(CaseService.CaseNotFoundException.class, 
                              ResponseEntity.notFound().build());
    }

    @PostMapping("/{id}/escalate")
    @Operation(summary = "Escalate case", description = "Escalates a case to higher priority")
    @ApiResponse(responseCode = "200", description = "Case escalated successfully")
    @ApiResponse(responseCode = "404", description = "Case not found")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Mono<ResponseEntity<Case>> escalateCase(
            @PathVariable UUID id,
            @RequestBody EscalateCaseRequest request,
            @AuthenticationPrincipal Jwt jwt) {
        
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        
        return caseService.escalateCase(id, request.reason(), tenantId, cellId)
                .map(ResponseEntity::ok)
                .onErrorReturn(CaseService.CaseNotFoundException.class, 
                              ResponseEntity.notFound().build());
    }

    @GetMapping
    @Operation(summary = "List cases", description = "Retrieves a paginated list of cases")
    @ApiResponse(responseCode = "200", description = "Cases retrieved successfully")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Flux<Case> listCases(
            @Parameter(description = "Page number (0-based)") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Page size") @RequestParam(defaultValue = "20") int size,
            @Parameter(description = "Filter by status") @RequestParam(required = false) CaseStatus status,
            @Parameter(description = "Filter by case type") @RequestParam(required = false) CaseType caseType,
            @Parameter(description = "Filter by priority") @RequestParam(required = false) Priority priority,
            @Parameter(description = "Filter by assigned user") @RequestParam(required = false) UUID assignedTo,
            @Parameter(description = "Search term") @RequestParam(required = false) String search,
            @Parameter(description = "Show only active cases") @RequestParam(defaultValue = "false") boolean activeOnly,
            @Parameter(description = "Show only high priority cases") @RequestParam(defaultValue = "false") boolean highPriorityOnly,
            @AuthenticationPrincipal Jwt jwt) {
        
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        
        // Apply filters based on query parameters
        if (search != null && !search.trim().isEmpty()) {
            return caseService.searchCases(search.trim(), tenantId, cellId, page, size);
        } else if (status != null) {
            return caseService.findCasesByStatus(status, tenantId, cellId, page, size);
        } else if (caseType != null) {
            return caseService.findCasesByType(caseType, tenantId, cellId, page, size);
        } else if (priority != null) {
            return caseService.findCasesByPriority(priority, tenantId, cellId, page, size);
        } else if (assignedTo != null) {
            return caseService.findCasesAssignedTo(assignedTo, tenantId, cellId, page, size);
        } else if (activeOnly) {
            return caseService.findActiveCases(tenantId, cellId, page, size);
        } else if (highPriorityOnly) {
            return caseService.findHighPriorityCases(tenantId, cellId, page, size);
        } else {
            return caseService.findAllCases(tenantId, cellId, page, size);
        }
    }

    @GetMapping("/statistics")
    @Operation(summary = "Get case statistics", description = "Retrieves case statistics for the tenant")
    @ApiResponse(responseCode = "200", description = "Statistics retrieved successfully")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Mono<CaseService.CaseStatistics> getCaseStatistics(@AuthenticationPrincipal Jwt jwt) {
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        
        return caseService.getCaseStatistics(tenantId, cellId);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete case", description = "Soft deletes a case (archives it)")
    @ApiResponse(responseCode = "204", description = "Case deleted successfully")
    @ApiResponse(responseCode = "404", description = "Case not found")
    @ApiResponse(responseCode = "401", description = "Unauthorized")
    public Mono<ResponseEntity<Void>> deleteCase(
            @PathVariable UUID id,
            @AuthenticationPrincipal Jwt jwt) {
        
        String tenantId = extractTenantId(jwt);
        String cellId = extractCellId(jwt);
        
        return caseService.deleteCase(id, tenantId, cellId)
                .then(Mono.just(ResponseEntity.noContent().<Void>build()))
                .onErrorReturn(CaseService.CaseNotFoundException.class, 
                              ResponseEntity.notFound().build());
    }

    // Helper methods to extract claims from JWT
    private String extractTenantId(Jwt jwt) {
        return jwt.getClaimAsString("tenant_id");
    }

    private String extractCellId(Jwt jwt) {
        return jwt.getClaimAsString("cell_id");
    }

    private UUID extractUserId(Jwt jwt) {
        String userIdStr = jwt.getClaimAsString("sub");
        return UUID.fromString(userIdStr);
    }

    // Request DTOs
    public record AssignCaseRequest(UUID assigneeId) {}
    public record CloseCaseRequest(String reason) {}
    public record EscalateCaseRequest(String reason) {}
}
