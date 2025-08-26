package com.finrisk.ai.caseservice.service;

import com.finrisk.ai.caseservice.domain.CaseType;
import org.springframework.data.redis.core.ReactiveStringRedisTemplate;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Service for generating unique case numbers
 * Format: {CASE_TYPE_PREFIX}-{YEAR}{MONTH}-{SEQUENCE}-{TENANT_HASH}
 * Example: FRD-202412-000001-A7B3
 */
@Service
public class CaseNumberGeneratorService {

    private static final DateTimeFormatter YEAR_MONTH_FORMATTER = DateTimeFormatter.ofPattern("yyyyMM");
    private static final String SEQUENCE_KEY_PREFIX = "case_sequence:";
    
    private final ReactiveStringRedisTemplate redisTemplate;

    public CaseNumberGeneratorService(ReactiveStringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    /**
     * Generate a unique case number
     */
    public Mono<String> generateCaseNumber(CaseType caseType, String tenantId) {
        String yearMonth = LocalDateTime.now().format(YEAR_MONTH_FORMATTER);
        String prefix = getCaseTypePrefix(caseType);
        String tenantHash = generateTenantHash(tenantId);
        
        String sequenceKey = SEQUENCE_KEY_PREFIX + prefix + ":" + yearMonth + ":" + tenantId;
        
        return redisTemplate.opsForValue()
                .increment(sequenceKey)
                .map(sequence -> String.format("%s-%s-%06d-%s", prefix, yearMonth, sequence, tenantHash))
                .doOnNext(caseNumber -> {
                    // Set expiration for the sequence key (retain for 13 months)
                    redisTemplate.expire(sequenceKey, java.time.Duration.ofDays(400)).subscribe();
                });
    }

    /**
     * Get case type prefix for case number
     */
    private String getCaseTypePrefix(CaseType caseType) {
        return switch (caseType) {
            case FRAUD -> "FRD";
            case AML -> "AML";
            case SANCTIONS -> "SAN";
            case KYC -> "KYC";
            case CYBERSECURITY -> "CYB";
            case INSIDER_TRADING -> "INT";
            case COMPLIANCE -> "CMP";
            case OPERATIONAL_RISK -> "OPR";
        };
    }

    /**
     * Generate a 4-character hash from tenant ID for case number uniqueness
     */
    private String generateTenantHash(String tenantId) {
        if (tenantId == null || tenantId.isEmpty()) {
            return "0000";
        }
        
        // Simple hash function to generate 4-character alphanumeric hash
        int hash = Math.abs(tenantId.hashCode());
        StringBuilder result = new StringBuilder();
        
        String chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        for (int i = 0; i < 4; i++) {
            result.append(chars.charAt(hash % chars.length()));
            hash /= chars.length();
        }
        
        return result.toString();
    }

    /**
     * Validate case number format
     */
    public boolean isValidCaseNumber(String caseNumber) {
        if (caseNumber == null || caseNumber.isEmpty()) {
            return false;
        }
        
        // Pattern: PREFIX-YYYYMM-NNNNNN-XXXX
        String pattern = "^[A-Z]{3}-\\d{6}-\\d{6}-[A-Z0-9]{4}$";
        return caseNumber.matches(pattern);
    }

    /**
     * Extract case type from case number
     */
    public CaseType extractCaseType(String caseNumber) {
        if (!isValidCaseNumber(caseNumber)) {
            throw new IllegalArgumentException("Invalid case number format: " + caseNumber);
        }
        
        String prefix = caseNumber.split("-")[0];
        return switch (prefix) {
            case "FRD" -> CaseType.FRAUD;
            case "AML" -> CaseType.AML;
            case "SAN" -> CaseType.SANCTIONS;
            case "KYC" -> CaseType.KYC;
            case "CYB" -> CaseType.CYBERSECURITY;
            case "INT" -> CaseType.INSIDER_TRADING;
            case "CMP" -> CaseType.COMPLIANCE;
            case "OPR" -> CaseType.OPERATIONAL_RISK;
            default -> throw new IllegalArgumentException("Unknown case type prefix: " + prefix);
        };
    }

    /**
     * Extract year-month from case number
     */
    public String extractYearMonth(String caseNumber) {
        if (!isValidCaseNumber(caseNumber)) {
            throw new IllegalArgumentException("Invalid case number format: " + caseNumber);
        }
        
        return caseNumber.split("-")[1];
    }

    /**
     * Extract sequence number from case number
     */
    public int extractSequence(String caseNumber) {
        if (!isValidCaseNumber(caseNumber)) {
            throw new IllegalArgumentException("Invalid case number format: " + caseNumber);
        }
        
        return Integer.parseInt(caseNumber.split("-")[2]);
    }

    /**
     * Extract tenant hash from case number
     */
    public String extractTenantHash(String caseNumber) {
        if (!isValidCaseNumber(caseNumber)) {
            throw new IllegalArgumentException("Invalid case number format: " + caseNumber);
        }
        
        return caseNumber.split("-")[3];
    }
}
