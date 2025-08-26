package com.finrisk.ai.caseservice.domain;

import com.fasterxml.jackson.annotation.JsonValue;

/**
 * Enumeration of case priorities for investigation urgency
 */
public enum Priority {
    LOW("LOW", "Low", 1, "Non-urgent cases with minimal impact"),
    MEDIUM("MEDIUM", "Medium", 2, "Standard priority cases"),
    HIGH("HIGH", "High", 3, "High priority cases requiring urgent attention"),
    CRITICAL("CRITICAL", "Critical", 4, "Critical cases requiring immediate action");

    private final String code;
    private final String displayName;
    private final int level;
    private final String description;

    Priority(String code, String displayName, int level, String description) {
        this.code = code;
        this.displayName = displayName;
        this.level = level;
        this.description = description;
    }

    @JsonValue
    public String getCode() {
        return code;
    }

    public String getDisplayName() {
        return displayName;
    }

    public int getLevel() {
        return level;
    }

    public String getDescription() {
        return description;
    }

    public static Priority fromCode(String code) {
        for (Priority priority : values()) {
            if (priority.code.equals(code)) {
                return priority;
            }
        }
        throw new IllegalArgumentException("Unknown priority code: " + code);
    }

    public boolean isHigherThan(Priority other) {
        return this.level > other.level;
    }

    public boolean isLowerThan(Priority other) {
        return this.level < other.level;
    }

    @Override
    public String toString() {
        return code;
    }
}
