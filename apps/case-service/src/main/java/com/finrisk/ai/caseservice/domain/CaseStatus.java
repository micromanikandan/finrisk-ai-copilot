package com.finrisk.ai.caseservice.domain;

import com.fasterxml.jackson.annotation.JsonValue;

/**
 * Enumeration of case statuses in the investigation lifecycle
 */
public enum CaseStatus {
    OPEN("OPEN", "Open", "Case is newly created and not yet assigned"),
    IN_PROGRESS("IN_PROGRESS", "In Progress", "Case is actively being investigated"),
    PENDING_REVIEW("PENDING_REVIEW", "Pending Review", "Case investigation is complete, awaiting review"),
    ESCALATED("ESCALATED", "Escalated", "Case has been escalated to higher authority"),
    CLOSED("CLOSED", "Closed", "Case investigation is complete and closed"),
    ARCHIVED("ARCHIVED", "Archived", "Case is archived for long-term storage");

    private final String code;
    private final String displayName;
    private final String description;

    CaseStatus(String code, String displayName, String description) {
        this.code = code;
        this.displayName = displayName;
        this.description = description;
    }

    @JsonValue
    public String getCode() {
        return code;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }

    public static CaseStatus fromCode(String code) {
        for (CaseStatus status : values()) {
            if (status.code.equals(code)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Unknown case status code: " + code);
    }

    public boolean isActive() {
        return this == OPEN || this == IN_PROGRESS || this == PENDING_REVIEW || this == ESCALATED;
    }

    public boolean isFinal() {
        return this == CLOSED || this == ARCHIVED;
    }

    @Override
    public String toString() {
        return code;
    }
}
