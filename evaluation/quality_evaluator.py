from typing import Dict, Any, List
import logging
from datetime import datetime

class VideoQualityEvaluator:
    """Evaluate the quality of generated videos"""
    
    def __init__(self):
        self.logger = logging.getLogger("quality_evaluator")
        self.metrics = [
            "content_quality",
            "production_value", 
            "engagement_potential",
            "seo_effectiveness",
            "overall_score"
        ]
    
    async def evaluate_video(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive video quality evaluation"""
        self.logger.info("Starting video quality evaluation")
        
        evaluation = {
            "evaluation_id": f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "scores": {},
            "feedback": {},
            "recommendations": []
        }
        
        try:
            # Evaluate different aspects
            evaluation["scores"]["content_quality"] = await self._evaluate_content(video_data)
            evaluation["scores"]["production_value"] = await self._evaluate_production(video_data)
            evaluation["scores"]["engagement_potential"] = await self._evaluate_engagement(video_data)
            evaluation["scores"]["seo_effectiveness"] = await self._evaluate_seo(video_data)
            
            # Calculate overall score
            evaluation["scores"]["overall_score"] = self._calculate_overall_score(evaluation["scores"])
            
            # Generate feedback
            evaluation["feedback"] = await self._generate_feedback(evaluation["scores"])
            evaluation["recommendations"] = await self._generate_recommendations(evaluation["scores"])
            
            # Determine if video meets quality standards
            evaluation["meets_standards"] = evaluation["scores"]["overall_score"] >= 0.7
            
            self.logger.info(f"Evaluation completed. Overall score: {evaluation['scores']['overall_score']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Evaluation failed: {str(e)}")
            evaluation["error"] = str(e)
            evaluation["scores"]["overall_score"] = 0.0
            evaluation["meets_standards"] = False
        
        return evaluation
    
    async def _evaluate_content(self, video_data: Dict[str, Any]) -> float:
        """Evaluate content quality"""
        script = video_data.get("script", {})
        scenes = script.get("scenes", [])
        
        score = 0.0
        
        # Score based on script structure
        if script.get("title"):
            score += 0.1
        
        if len(scenes) >= 3:  # Minimum scenes for good structure
            score += 0.3
        
        # Score based on content depth
        total_content = sum(len(scene.get("content", "")) for scene in scenes)
        if total_content > 1000:
            score += 0.3
        
        # Score based on engagement elements
        if any("hook" in scene.get("content", "").lower() for scene in scenes):
            score += 0.2
        
        if any("call to action" in scene.get("content", "").lower() for scene in scenes):
            score += 0.1
        
        return min(score, 1.0)
    
    async def _evaluate_production(self, video_data: Dict[str, Any]) -> float:
        """Evaluate production quality"""
        assets = video_data.get("assets", {})
        
        score = 0.0
        
        # Check for essential assets
        if assets.get("voiceovers"):
            score += 0.3
        
        if assets.get("thumbnail"):
            score += 0.2
        
        if assets.get("visuals"):
            score += 0.3
        
        # Check production completeness
        if assets.get("video_assembled"):
            score += 0.2
        
        return min(score, 1.0)
    
    async def _evaluate_engagement(self, video_data: Dict[str, Any]) -> float:
        """Evaluate engagement potential"""
        script = video_data.get("script", {})
        metadata = video_data.get("metadata", {})
        
        score = 0.0
        
        # Score based on title engagement
        title = script.get("title", "")
        if any(word in title.lower() for word in ["how", "why", "secret", "amazing"]):
            score += 0.2
        
        # Score based on duration appropriateness
        duration = metadata.get("duration", 0)
        if 300 <= duration <= 900:  # 5-15 minutes ideal for educational content
            score += 0.3
        
        # Score based on structure
        scenes = script.get("scenes", [])
        if len(scenes) >= 5:  # Good content depth
            score += 0.3
        
        # Score based on pacing (simplified)
        if scenes and all(scene.get("duration_seconds", 0) <= 120 for scene in scenes):
            score += 0.2
        
        return min(score, 1.0)
    
    async def _evaluate_seo(self, video_data: Dict[str, Any]) -> float:
        """Evaluate SEO effectiveness"""
        script = video_data.get("script", {})
        metadata = video_data.get("metadata", {})
        
        score = 0.0
        
        # Title SEO
        title = script.get("title", "")
        if len(title) >= 30 and len(title) <= 60:  # Ideal title length
            score += 0.3
        
        # Description SEO
        description = metadata.get("description", "")
        if len(description) >= 100:  # Minimum description length
            score += 0.3
        
        # Tags SEO
        tags = metadata.get("tags", [])
        if len(tags) >= 5:
            score += 0.2
        
        # Keyword optimization (simplified)
        if any(keyword in title.lower() for keyword in ["ai", "technology", "future"]):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        weights = {
            "content_quality": 0.4,
            "production_value": 0.3,
            "engagement_potential": 0.2,
            "seo_effectiveness": 0.1
        }
        
        overall = sum(scores[metric] * weights[metric] for metric in weights)
        return round(overall, 2)
    
    async def _generate_feedback(self, scores: Dict[str, float]) -> Dict[str, str]:
        """Generate constructive feedback"""
        feedback = {}
        
        for metric, score in scores.items():
            if score >= 0.8:
                feedback[metric] = f"Excellent {metric.replace('_', ' ')}"
            elif score >= 0.6:
                feedback[metric] = f"Good {metric.replace('_', ' ')} with room for improvement"
            elif score >= 0.4:
                feedback[metric] = f"Average {metric.replace('_', ' ')} - needs work"
            else:
                feedback[metric] = f"Poor {metric.replace('_', ' ')} - significant improvement needed"
        
        return feedback
    
    async def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if scores["content_quality"] < 0.7:
            recommendations.extend([
                "Add more detailed explanations in the script",
                "Include real-world examples and case studies",
                "Strengthen the introduction and conclusion"
            ])
        
        if scores["production_value"] < 0.7:
            recommendations.extend([
                "Improve audio quality and add background music",
                "Enhance visual elements with better graphics",
                "Ensure smooth transitions between scenes"
            ])
        
        if scores["engagement_potential"] < 0.7:
            recommendations.extend([
                "Add more engaging hooks and storytelling elements",
                "Include calls to action to encourage viewer interaction",
                "Optimize video length for audience retention"
            ])
        
        if scores["seo_effectiveness"] < 0.7:
            recommendations.extend([
                "Optimize title with relevant keywords",
                "Expand video description with more details",
                "Add more specific tags for better discoverability"
            ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def compare_with_benchmark(self, evaluation: Dict[str, Any], benchmark: str = "youtube_educational") -> Dict[str, Any]:
        """Compare evaluation results with benchmarks"""
        benchmarks = {
            "youtube_educational": {
                "content_quality": 0.75,
                "production_value": 0.70,
                "engagement_potential": 0.80,
                "seo_effectiveness": 0.65,
                "overall_score": 0.73
            },
            "youtube_viral": {
                "content_quality": 0.70,
                "production_value": 0.75,
                "engagement_potential": 0.85,
                "seo_effectiveness": 0.70,
                "overall_score": 0.75
            }
        }
        
        benchmark_scores = benchmarks.get(benchmark, benchmarks["youtube_educational"])
        scores = evaluation["scores"]
        
        comparison = {
            "benchmark": benchmark,
            "comparison": {},
            "above_benchmark": [],
            "below_benchmark": []
        }
        
        for metric in self.metrics:
            if metric in scores and metric in benchmark_scores:
                difference = scores[metric] - benchmark_scores[metric]
                comparison["comparison"][metric] = {
                    "actual": scores[metric],
                    "benchmark": benchmark_scores[metric],
                    "difference": difference,
                    "percentage_diff": (difference / benchmark_scores[metric]) * 100 if benchmark_scores[metric] > 0 else 0
                }
                
                if difference > 0:
                    comparison["above_benchmark"].append(metric)
                elif difference < 0:
                    comparison["below_benchmark"].append(metric)
        
        return comparison