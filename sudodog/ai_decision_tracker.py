#!/usr/bin/env python3
"""
SudoDog AI Decision Tracker - Log and analyze LLM decisions
Tracks prompts, responses, reasoning, and decision patterns
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class AIDecision:
    """Represents a single AI decision point"""
    timestamp: str
    decision_id: str
    prompt: str
    response: str
    reasoning: Optional[str]
    model: str
    command_analyzed: Optional[str]
    risk_level: Optional[str]
    action_taken: str
    metadata: Dict[str, Any]


class AIDecisionTracker:
    """Tracks and analyzes AI agent decisions for security and audit"""
    
    def __init__(self, log_path: str = "/var/log/sudodog/ai_decisions.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('sudodog.ai_tracker')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_path.parent / 'ai_tracker.log')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
    
    def generate_decision_id(self, prompt: str, timestamp: str) -> str:
        """Generate unique ID for a decision"""
        content = f"{timestamp}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def log_decision(self, 
                     prompt: str,
                     response: str,
                     model: str = "unknown",
                     reasoning: Optional[str] = None,
                     command_analyzed: Optional[str] = None,
                     risk_level: Optional[str] = None,
                     action_taken: str = "analyzed",
                     **metadata) -> str:
        """
        Log an AI decision to JSONL file
        Returns the decision ID
        """
        timestamp = datetime.utcnow().isoformat()
        decision_id = self.generate_decision_id(prompt, timestamp)
        
        decision = AIDecision(
            timestamp=timestamp,
            decision_id=decision_id,
            prompt=prompt,
            response=response,
            reasoning=reasoning,
            model=model,
            command_analyzed=command_analyzed,
            risk_level=risk_level,
            action_taken=action_taken,
            metadata=metadata
        )
        
        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(asdict(decision)) + '\n')
            
            self.logger.info(f"Logged decision {decision_id}: {action_taken}")
            return decision_id
            
        except Exception as e:
            self.logger.error(f"Failed to log decision: {str(e)}")
            raise
    
    def get_decisions(self, 
                      limit: Optional[int] = None,
                      risk_level: Optional[str] = None,
                      action_taken: Optional[str] = None) -> List[Dict]:
        """Retrieve decisions with optional filtering"""
        decisions = []
        
        try:
            if not self.log_path.exists():
                return decisions
            
            with open(self.log_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    try:
                        decision = json.loads(line)
                        
                        # Apply filters
                        if risk_level and decision.get('risk_level') != risk_level:
                            continue
                        if action_taken and decision.get('action_taken') != action_taken:
                            continue
                        
                        decisions.append(decision)
                        
                        if limit and len(decisions) >= limit:
                            break
                    
                    except json.JSONDecodeError:
                        continue
            
            return decisions
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve decisions: {str(e)}")
            return []
    
    def get_decision_by_id(self, decision_id: str) -> Optional[Dict]:
        """Retrieve a specific decision by ID"""
        decisions = self.get_decisions()
        for decision in decisions:
            if decision.get('decision_id') == decision_id:
                return decision
        return None
    
    def get_statistics(self) -> Dict:
        """Get statistics about AI decisions"""
        decisions = self.get_decisions()
        
        if not decisions:
            return {
                'total_decisions': 0,
                'risk_level_breakdown': {},
                'action_breakdown': {},
                'model_usage': {},
                'avg_prompt_length': 0,
                'avg_response_length': 0
            }
        
        stats = {
            'total_decisions': len(decisions),
            'risk_level_breakdown': {},
            'action_breakdown': {},
            'model_usage': {},
            'first_decision': decisions[0].get('timestamp'),
            'last_decision': decisions[-1].get('timestamp')
        }
        
        prompt_lengths = []
        response_lengths = []
        
        for decision in decisions:
            # Risk level breakdown
            risk = decision.get('risk_level', 'unknown')
            stats['risk_level_breakdown'][risk] = \
                stats['risk_level_breakdown'].get(risk, 0) + 1
            
            # Action breakdown
            action = decision.get('action_taken', 'unknown')
            stats['action_breakdown'][action] = \
                stats['action_breakdown'].get(action, 0) + 1
            
            # Model usage
            model = decision.get('model', 'unknown')
            stats['model_usage'][model] = \
                stats['model_usage'].get(model, 0) + 1
            
            # Length statistics
            if decision.get('prompt'):
                prompt_lengths.append(len(decision['prompt']))
            if decision.get('response'):
                response_lengths.append(len(decision['response']))
        
        if prompt_lengths:
            stats['avg_prompt_length'] = sum(prompt_lengths) / len(prompt_lengths)
        if response_lengths:
            stats['avg_response_length'] = sum(response_lengths) / len(response_lengths)
        
        return stats
    
    def analyze_patterns(self) -> Dict:
        """Analyze patterns in AI decisions"""
        decisions = self.get_decisions()
        
        patterns = {
            'high_risk_commands': [],
            'blocked_commands': [],
            'common_reasoning': {},
            'escalation_trends': []
        }
        
        for decision in decisions:
            # Track high-risk decisions
            if decision.get('risk_level') == 'high':
                patterns['high_risk_commands'].append({
                    'command': decision.get('command_analyzed'),
                    'timestamp': decision.get('timestamp'),
                    'reasoning': decision.get('reasoning')
                })
            
            # Track blocked commands
            if decision.get('action_taken') == 'blocked':
                patterns['blocked_commands'].append({
                    'command': decision.get('command_analyzed'),
                    'timestamp': decision.get('timestamp')
                })
            
            # Common reasoning patterns
            reasoning = decision.get('reasoning')
            if reasoning:
                # Simple keyword extraction
                for keyword in ['dangerous', 'malicious', 'suspicious', 'safe', 'benign']:
                    if keyword in reasoning.lower():
                        patterns['common_reasoning'][keyword] = \
                            patterns['common_reasoning'].get(keyword, 0) + 1
        
        return patterns
    
    def export_report(self, output_file: str, format: str = 'json'):
        """Export analysis report in various formats"""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'statistics': self.get_statistics(),
            'patterns': self.analyze_patterns(),
            'recent_decisions': self.get_decisions(limit=10)
        }
        
        output_path = Path(output_file)
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
        
        elif format == 'text':
            with open(output_path, 'w') as f:
                f.write("=== SudoDog AI Decision Analysis Report ===\n\n")
                f.write(f"Generated: {report['generated_at']}\n\n")
                
                f.write("Statistics:\n")
                stats = report['statistics']
                f.write(f"  Total Decisions: {stats['total_decisions']}\n")
                f.write(f"  Risk Levels: {stats['risk_level_breakdown']}\n")
                f.write(f"  Actions: {stats['action_breakdown']}\n")
                f.write(f"  Models Used: {stats['model_usage']}\n\n")
                
                f.write("Patterns:\n")
                patterns = report['patterns']
                f.write(f"  High Risk Commands: {len(patterns['high_risk_commands'])}\n")
                f.write(f"  Blocked Commands: {len(patterns['blocked_commands'])}\n")
                f.write(f"  Common Reasoning: {patterns['common_reasoning']}\n")
        
        self.logger.info(f"Exported report to {output_path}")
        return output_path
