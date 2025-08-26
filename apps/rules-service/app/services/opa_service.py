"""OPA (Open Policy Agent) service integration."""

import asyncio
import json
from typing import Dict, Any, List, Optional
import httpx
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


class OPAService:
    """Service for integrating with Open Policy Agent (OPA)."""
    
    def __init__(self):
        self.settings = get_settings()
        self.opa_url = self.settings.OPA_URL
        self.client = None
        self.policies_loaded = False
    
    async def initialize(self) -> None:
        """Initialize OPA service and load policies."""
        logger.info("Initializing OPA service", url=self.opa_url)
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Test OPA connection
        await self._health_check()
        
        # Load default policies
        await self._load_default_policies()
        
        self.policies_loaded = True
        logger.info("OPA service initialized successfully")
    
    async def _health_check(self) -> bool:
        """Check if OPA is healthy and reachable."""
        try:
            response = await self.client.get(f"{self.opa_url}/health")
            if response.status_code == 200:
                logger.info("OPA health check passed")
                return True
            else:
                logger.error("OPA health check failed", status_code=response.status_code)
                return False
        except Exception as e:
            logger.error("OPA health check failed", error=str(e))
            return False
    
    async def _load_default_policies(self) -> None:
        """Load default fraud detection and compliance policies."""
        
        # Fraud detection policy
        fraud_policy = """
        package fraud.detection

        default allow = false
        default risk_score = 0

        # High-risk transaction patterns
        high_risk_transaction {
            input.transaction.amount > 10000
            input.transaction.time.hour >= 22
            input.transaction.time.hour <= 6
        }

        high_risk_transaction {
            input.transaction.amount > 5000
            input.customer.account_age_days < 30
        }

        high_risk_transaction {
            input.transaction.merchant.category == "cash_advance"
            input.transaction.amount > 2000
        }

        # Velocity checks
        high_velocity {
            input.customer.daily_transaction_count > 20
            input.customer.daily_transaction_amount > 50000
        }

        # Geographic risk
        geographic_risk {
            input.transaction.location.country != input.customer.home_country
            input.transaction.amount > 1000
        }

        # Calculate risk score
        risk_score = score {
            factors := [
                high_risk_transaction,
                high_velocity,
                geographic_risk,
                input.customer.has_previous_fraud,
                input.transaction.card_not_present
            ]
            
            true_count := count([factor | factors[_] == factor; factor == true])
            score := (true_count / count(factors)) * 100
        }

        # Decision logic
        allow {
            risk_score < 30
        }

        block {
            risk_score >= 80
        }

        review {
            risk_score >= 30
            risk_score < 80
        }
        """
        
        # AML screening policy
        aml_policy = """
        package aml.screening

        default allow = true
        default sanctions_hit = false
        default pep_match = false

        # Sanctions screening
        sanctions_hit {
            input.entity.name in data.sanctions_list
        }

        sanctions_hit {
            input.entity.aliases[_] in data.sanctions_list
        }

        # PEP (Politically Exposed Person) check
        pep_match {
            input.entity.name in data.pep_list
        }

        pep_match {
            input.entity.associates[_] in data.pep_list
        }

        # High-risk countries
        high_risk_country {
            input.entity.country in data.high_risk_countries
        }

        # Risk assessment
        risk_level = level {
            sanctions_hit
            level := "HIGH"
        } else = level {
            pep_match
            level := "MEDIUM"
        } else = level {
            high_risk_country
            level := "MEDIUM"
        } else = "LOW"

        # Decision
        allow {
            not sanctions_hit
            not (pep_match; input.transaction.amount > 100000)
        }
        """
        
        # KYC compliance policy
        kyc_policy = """
        package kyc.compliance

        default compliant = false
        default missing_documents = []

        required_documents = [
            "government_id",
            "proof_of_address",
            "source_of_funds"
        ]

        enhanced_due_diligence_required {
            input.customer.risk_rating == "HIGH"
        }

        enhanced_due_diligence_required {
            input.customer.country in data.high_risk_countries
        }

        enhanced_due_diligence_required {
            input.customer.occupation in ["politician", "diplomat", "judge"]
        }

        enhanced_documents = [
            "bank_statements",
            "employment_verification",
            "wealth_declaration"
        ]

        all_required_docs = docs {
            enhanced_due_diligence_required
            docs := array.concat(required_documents, enhanced_documents)
        } else = required_documents

        missing_documents = missing {
            missing := [doc | 
                doc := all_required_docs[_]
                not doc in input.customer.provided_documents
            ]
        }

        compliant {
            count(missing_documents) == 0
            input.customer.identity_verified == true
            input.customer.address_verified == true
        }

        verification_expired {
            time.now_ns() > input.customer.last_verification_ns + (365 * 24 * 60 * 60 * 1000000000)
        }
        """
        
        # Load policies into OPA
        policies = [
            ("fraud/detection", fraud_policy),
            ("aml/screening", aml_policy),
            ("kyc/compliance", kyc_policy)
        ]
        
        for policy_path, policy_content in policies:
            await self.create_or_update_policy(policy_path, policy_content)
    
    async def evaluate_policy(
        self,
        policy_path: str,
        input_data: Dict[str, Any],
        tenant_id: str,
        query: str = "data"
    ) -> Dict[str, Any]:
        """Evaluate a policy with given input data."""
        try:
            # Prepare the evaluation request
            eval_request = {
                "input": {
                    **input_data,
                    "tenant_id": tenant_id,
                    "timestamp": asyncio.get_event_loop().time()
                }
            }
            
            # Make request to OPA
            url = f"{self.opa_url}/v1/data/{policy_path.replace('/', '.')}"
            if query != "data":
                url += f"/{query}"
            
            response = await self.client.post(url, json=eval_request)
            
            if response.status_code == 200:
                result = response.json()
                
                logger.info("Policy evaluated successfully", 
                           policy=policy_path, 
                           tenant=tenant_id,
                           decision=result.get("result"))
                
                return {
                    "success": True,
                    "result": result.get("result"),
                    "decision_id": f"decision_{asyncio.current_task().get_name()}",
                    "policy_path": policy_path,
                    "evaluation_time_ms": response.elapsed.total_seconds() * 1000
                }
            else:
                logger.error("Policy evaluation failed", 
                           policy=policy_path,
                           status_code=response.status_code,
                           response=response.text)
                
                return {
                    "success": False,
                    "error": f"OPA evaluation failed: {response.status_code}",
                    "details": response.text
                }
        
        except Exception as e:
            logger.error("Policy evaluation error", error=str(e), policy=policy_path)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_or_update_policy(self, policy_path: str, policy_content: str) -> bool:
        """Create or update a policy in OPA."""
        try:
            url = f"{self.opa_url}/v1/policies/{policy_path}"
            
            response = await self.client.put(
                url,
                content=policy_content,
                headers={"Content-Type": "text/plain"}
            )
            
            if response.status_code in [200, 201]:
                logger.info("Policy created/updated successfully", policy=policy_path)
                return True
            else:
                logger.error("Policy creation failed", 
                           policy=policy_path,
                           status_code=response.status_code,
                           response=response.text)
                return False
        
        except Exception as e:
            logger.error("Policy creation error", error=str(e), policy=policy_path)
            return False
    
    async def delete_policy(self, policy_path: str) -> bool:
        """Delete a policy from OPA."""
        try:
            url = f"{self.opa_url}/v1/policies/{policy_path}"
            
            response = await self.client.delete(url)
            
            if response.status_code in [200, 204]:
                logger.info("Policy deleted successfully", policy=policy_path)
                return True
            else:
                logger.error("Policy deletion failed", 
                           policy=policy_path,
                           status_code=response.status_code)
                return False
        
        except Exception as e:
            logger.error("Policy deletion error", error=str(e), policy=policy_path)
            return False
    
    async def list_policies(self) -> List[Dict[str, Any]]:
        """List all policies in OPA."""
        try:
            response = await self.client.get(f"{self.opa_url}/v1/policies")
            
            if response.status_code == 200:
                policies = response.json()
                return policies.get("result", [])
            else:
                logger.error("Failed to list policies", status_code=response.status_code)
                return []
        
        except Exception as e:
            logger.error("Error listing policies", error=str(e))
            return []
    
    async def load_data(self, data_path: str, data: Dict[str, Any]) -> bool:
        """Load reference data into OPA (sanctions lists, PEP lists, etc.)."""
        try:
            url = f"{self.opa_url}/v1/data/{data_path.replace('/', '.')}"
            
            response = await self.client.put(url, json=data)
            
            if response.status_code in [200, 201, 204]:
                logger.info("Data loaded successfully", data_path=data_path)
                return True
            else:
                logger.error("Data loading failed", 
                           data_path=data_path,
                           status_code=response.status_code)
                return False
        
        except Exception as e:
            logger.error("Data loading error", error=str(e), data_path=data_path)
            return False
    
    async def evaluate_fraud_risk(self, transaction_data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """Evaluate fraud risk for a transaction."""
        return await self.evaluate_policy(
            "fraud/detection",
            transaction_data,
            tenant_id,
            query="allow"
        )
    
    async def screen_aml_entity(self, entity_data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """Screen entity for AML compliance."""
        return await self.evaluate_policy(
            "aml/screening",
            entity_data,
            tenant_id,
            query="allow"
        )
    
    async def check_kyc_compliance(self, customer_data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """Check KYC compliance for a customer."""
        return await self.evaluate_policy(
            "kyc/compliance",
            customer_data,
            tenant_id,
            query="compliant"
        )
    
    async def close(self) -> None:
        """Close the OPA client."""
        if self.client:
            await self.client.aclose()
