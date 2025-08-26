package com.finrisk.ai.caseservice.domain;

import com.fasterxml.jackson.annotation.JsonValue;

/**
 * Enumeration of case types for fraud and compliance investigations
 */
public enum CaseType {
    FRAUD("FRAUD", "Fraud Investigation", "Cases involving suspected fraudulent activities"),
    AML("AML", "Anti-Money Laundering", "Money laundering investigation cases"),
    SANCTIONS("SANCTIONS", "Sanctions Screening", "Sanctions violations and screening cases"),
    KYC("KYC", "Know Your Customer", "Customer due diligence and verification cases"),
    CYBERSECURITY("CYBERSECURITY", "Cybersecurity Incident", "Security breaches and cyber attacks"),
    INSIDER_TRADING("INSIDER_TRADING", "Insider Trading", "Market manipulation and insider trading cases"),
    COMPLIANCE("COMPLIANCE", "Regulatory Compliance", "General regulatory compliance violations"),
    OPERATIONAL_RISK("OPERATIONAL_RISK", "Operational Risk", "Operational failures and risk incidents");

    private final String code;
    private final String displayName;
    private final String description;

    CaseType(String code, String displayName, String description) {
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

    public static CaseType fromCode(String code) {
        for (CaseType type : values()) {
            if (type.code.equals(code)) {
                return type;
            }
        }
        throw new IllegalArgumentException("Unknown case type code: " + code);
    }

    @Override
    public String toString() {
        return code;
    }
}
