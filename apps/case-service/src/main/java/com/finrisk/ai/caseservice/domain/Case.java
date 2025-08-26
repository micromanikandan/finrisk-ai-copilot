package com.finrisk.ai.caseservice.domain;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.springframework.data.annotation.*;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Case domain entity representing a fraud/compliance investigation case
 */
@Table("cases")
public class Case {

    @Id
    private UUID id;

    @NotBlank(message = "Case number is required")
    @Size(max = 50, message = "Case number must not exceed 50 characters")
    @Column("case_number")
    @JsonProperty("case_number")
    private String caseNumber;

    @NotBlank(message = "Title is required")
    @Size(max = 255, message = "Title must not exceed 255 characters")
    private String title;

    @Size(max = 5000, message = "Description must not exceed 5000 characters")
    private String description;

    @NotNull(message = "Case type is required")
    @Column("case_type")
    @JsonProperty("case_type")
    private CaseType caseType;

    @NotNull(message = "Priority is required")
    private Priority priority = Priority.MEDIUM;

    @NotNull(message = "Status is required")
    private CaseStatus status = CaseStatus.OPEN;

    @Column("assigned_to")
    @JsonProperty("assigned_to")
    private UUID assignedTo;

    @NotNull(message = "Created by is required")
    @Column("created_by")
    @JsonProperty("created_by")
    private UUID createdBy;

    @CreatedDate
    @Column("created_at")
    @JsonProperty("created_at")
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column("updated_at")
    @JsonProperty("updated_at")
    private LocalDateTime updatedAt;

    @Column("closed_at")
    @JsonProperty("closed_at")
    private LocalDateTime closedAt;

    private Map<String, Object> metadata;

    private List<String> tags;

    @Version
    private Integer version = 1;

    @NotBlank(message = "Tenant ID is required")
    @Column("tenant_id")
    @JsonProperty("tenant_id")
    private String tenantId;

    @NotBlank(message = "Cell ID is required")
    @Column("cell_id")
    @JsonProperty("cell_id")
    private String cellId;

    // Constructors
    public Case() {}

    public Case(String caseNumber, String title, CaseType caseType, UUID createdBy, String tenantId, String cellId) {
        this.caseNumber = caseNumber;
        this.title = title;
        this.caseType = caseType;
        this.createdBy = createdBy;
        this.tenantId = tenantId;
        this.cellId = cellId;
    }

    // Getters and Setters
    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getCaseNumber() {
        return caseNumber;
    }

    public void setCaseNumber(String caseNumber) {
        this.caseNumber = caseNumber;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public CaseType getCaseType() {
        return caseType;
    }

    public void setCaseType(CaseType caseType) {
        this.caseType = caseType;
    }

    public Priority getPriority() {
        return priority;
    }

    public void setPriority(Priority priority) {
        this.priority = priority;
    }

    public CaseStatus getStatus() {
        return status;
    }

    public void setStatus(CaseStatus status) {
        this.status = status;
    }

    public UUID getAssignedTo() {
        return assignedTo;
    }

    public void setAssignedTo(UUID assignedTo) {
        this.assignedTo = assignedTo;
    }

    public UUID getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(UUID createdBy) {
        this.createdBy = createdBy;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public LocalDateTime getClosedAt() {
        return closedAt;
    }

    public void setClosedAt(LocalDateTime closedAt) {
        this.closedAt = closedAt;
    }

    public Map<String, Object> getMetadata() {
        return metadata;
    }

    public void setMetadata(Map<String, Object> metadata) {
        this.metadata = metadata;
    }

    public List<String> getTags() {
        return tags;
    }

    public void setTags(List<String> tags) {
        this.tags = tags;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
    }

    public String getTenantId() {
        return tenantId;
    }

    public void setTenantId(String tenantId) {
        this.tenantId = tenantId;
    }

    public String getCellId() {
        return cellId;
    }

    public void setCellId(String cellId) {
        this.cellId = cellId;
    }

    // Business methods
    public boolean isClosed() {
        return status == CaseStatus.CLOSED;
    }

    public boolean isHighPriority() {
        return priority == Priority.HIGH || priority == Priority.CRITICAL;
    }

    public void close() {
        this.status = CaseStatus.CLOSED;
        this.closedAt = LocalDateTime.now();
    }

    public void assignTo(UUID userId) {
        this.assignedTo = userId;
        this.status = CaseStatus.IN_PROGRESS;
    }

    public void escalate() {
        this.status = CaseStatus.ESCALATED;
        if (this.priority != Priority.CRITICAL) {
            this.priority = Priority.HIGH;
        }
    }

    @Override
    public String toString() {
        return "Case{" +
                "id=" + id +
                ", caseNumber='" + caseNumber + '\'' +
                ", title='" + title + '\'' +
                ", caseType=" + caseType +
                ", priority=" + priority +
                ", status=" + status +
                ", tenantId='" + tenantId + '\'' +
                ", cellId='" + cellId + '\'' +
                '}';
    }
}
