#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock implementation of the executor module.

This module provides mock functionality for executing scraping pipelines
and returning results.
"""

import time
import random
from typing import Dict, Any, List, Optional, Union, Callable
from pydantic import BaseModel
import json
from datetime import datetime
from uuid import uuid4

from cli.mocks.mock_pipeline_builder import PipelineSpec


class ExecutionResult(BaseModel):
    """Result of pipeline execution."""
    run_id: str
    pipeline_id: str
    status: str  # 'success', 'error', 'timeout'
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    execution_time_seconds: float
    timestamp: str


def mock_execute_pipeline(
    pipeline: PipelineSpec,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> ExecutionResult:
    """
    Mock implementation of pipeline execution.
    
    This function simulates executing a pipeline and returning results,
    with an optional callback for progress updates.
    
    Args:
        pipeline: Specification of the pipeline to execute
        progress_callback: Optional callback function for progress updates
        
    Returns:
        An ExecutionResult object with the execution results
    """
    # Generate a unique ID for the run
    run_id = f"run_{str(uuid4())[:8]}"
    
    # Track start time
    start_time = time.time()
    
    # Simulate execution time
    total_steps = 5
    
    # Step 1: Initialize tools
    if progress_callback:
        progress_callback(20, "Initializing tools...")
    time.sleep(0.5)  # Simulate initialization time
    
    # Step 2: Fetch content
    if progress_callback:
        progress_callback(40, f"Fetching content with {pipeline.tools[0].name}...")
    time.sleep(1.0)  # Simulate fetch time
    
    # Step 3: Process content
    if progress_callback:
        progress_callback(60, f"Processing content with {pipeline.tools[1].name}...")
    time.sleep(0.7)  # Simulate processing time
    
    # Step 4: Extract data
    if progress_callback:
        progress_callback(80, "Extracting data...")
    time.sleep(0.5)  # Simulate extraction time
    
    # Determine if the execution should succeed or fail (90% success rate)
    success = random.random() < 0.9
    
    if success:
        # Step 5: Generate results
        if progress_callback:
            progress_callback(100, "Generating results...")
        
        # Create mock data for each field
        data: Dict[str, Any] = {}
        
        for field in pipeline.intent.data_to_extract:
            if field == "title":
                data[field] = "Sample Product Title"
            elif field == "price":
                data[field] = "$49.99"
            elif field == "description":
                data[field] = "This is a sample product description. It contains information about the product."
            elif field == "image":
                data[field] = "https://example.com/images/sample-product.jpg"
            elif field == "rating":
                data[field] = "4.5 (123 reviews)"
            else:
                data[field] = f"Sample {field} data"
        
        result = ExecutionResult(
            run_id=run_id,
            pipeline_id=pipeline.id,
            status="success",
            data=data,
            error=None,
            execution_time_seconds=time.time() - start_time,
            timestamp=datetime.now().isoformat()
        )
    else:
        # Simulate failure
        if progress_callback:
            progress_callback(90, "Error encountered...")
        
        # Different types of errors
        error_types = [
            {"type": "selector_not_found", "message": "Could not find element with selector"},
            {"type": "timeout", "message": "Operation timed out"},
            {"type": "network_error", "message": "Network connection failed"},
            {"type": "anti_bot", "message": "Access blocked by anti-bot protection"}
        ]
        
        selected_error = random.choice(error_types)
        
        result = ExecutionResult(
            run_id=run_id,
            pipeline_id=pipeline.id,
            status="error",
            data=None,
            error={
                "type": selected_error["type"],
                "message": selected_error["message"],
                "details": f"Error occurred during extraction with {pipeline.tools[1].name}"
            },
            execution_time_seconds=time.time() - start_time,
            timestamp=datetime.now().isoformat()
        )
    
    return result
