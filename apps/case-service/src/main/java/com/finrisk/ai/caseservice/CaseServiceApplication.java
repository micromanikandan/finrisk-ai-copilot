package com.finrisk.ai.caseservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.r2dbc.config.EnableR2dbcAuditing;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;

/**
 * FinRisk Case Service Application
 * 
 * Reactive microservice for managing fraud and compliance investigation cases.
 * Features:
 * - WebFlux for reactive web layer
 * - R2DBC for reactive database access
 * - Kafka for event streaming
 * - OAuth2 Resource Server for security
 * - Multi-tenant architecture
 */
@SpringBootApplication
@EnableR2dbcAuditing
@EnableKafka
@EnableWebFluxSecurity
public class CaseServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(CaseServiceApplication.class, args);
    }
}
